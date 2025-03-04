"""Entry point to the evaluation harness"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partialmethod
from typing import Dict, List, Optional, Union

import mlflow
from tqdm.auto import tqdm

from databricks.rag_eval import context, env_vars, session
from databricks.rag_eval.clients.managedrag import managed_rag_client
from databricks.rag_eval.config import assessment_config, evaluation_config
from databricks.rag_eval.evaluation import (
    assessments,
    datasets,
    entities,
    metrics,
    models,
    per_run_metrics,
    rca,
    traces,
)
from databricks.rag_eval.evaluation import custom_metrics as agent_custom_metrics
from databricks.rag_eval.utils import input_output_utils, rate_limit

_logger = logging.getLogger(__name__)

EvalResults = List[entities.EvalResult]


def run(
    *,
    eval_dataset: Union[datasets.EvaluationDataframe, List[entities.EvalItem]],
    config: evaluation_config.EvaluationConfig,
    run_id: Optional[str] = None,
    model=None,
) -> EvalResults:
    """
    Run the logic of the eval harness.

    :param eval_dataset: The evaluation dataset
    :param config: The evaluation config
    :param run_id: The MLflow run ID to log the results to (used for logging traces)
    :param model: Optional model to use for generating responses and traces
    """

    eval_items = (
        eval_dataset.eval_items
        if isinstance(eval_dataset, datasets.EvaluationDataframe)
        else eval_dataset
    )

    # Disable tqdm progress bar by default so that the progress bars inside MLflow eval_fn do not show
    tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)

    client = context.get_context().build_managed_rag_client()
    rate_limiter = _build_rate_limiter_for_assessment()

    # Emit usage events prior to all logic
    _emit_custom_assessments_usage_event_if_present(client, config.assessment_configs)

    eval_results = []
    with ThreadPoolExecutor(
        max_workers=env_vars.RAG_EVAL_MAX_WORKERS.get()
    ) as executor:
        futures = [
            executor.submit(
                _run_single,
                eval_item=eval_item,
                config=config,
                model=model,
                client=client,
                rate_limiter=rate_limiter,
                current_session=session.current_session(),
                run_id=run_id,
            )
            for eval_item in eval_items
        ]

        futures_as_completed = as_completed(futures)
        # Add a progress bar to show the progress of the assessments
        futures_as_completed = tqdm(
            futures_as_completed,
            total=len(futures),
            disable=False,
            desc="Evaluating",
            smoothing=0,  # 0 means using average speed for remaining time estimates
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [Elapsed: {elapsed}, Remaining: {remaining}]",
        )

        for future in futures_as_completed:
            result = future.result()
            eval_results.append(result)

    # Compute aggregate metrics if there are custom metrics configured
    aggregate_metrics = None
    if config.custom_metrics:
        try:
            aggregate_metrics = per_run_metrics.compute_aggregate_metric_results(
                eval_results
            )
        except Exception as e:
            _logger.error(
                "Failed to compute aggregate metrics. Skipping emitting custom metric usage event.",
                exc_info=e,
            )

    _emit_custom_metric_usage_event_if_present(
        client, config.custom_metrics, metric_stats=aggregate_metrics
    )

    return eval_results


def _run_single(
    eval_item: entities.EvalItem,
    config: evaluation_config.EvaluationConfig,
    client: managed_rag_client.ManagedRagClient,
    rate_limiter: rate_limit.RateLimiter,
    run_id: Optional[str] = None,
    model: Optional[mlflow.pyfunc.PyFuncModel] = None,
    current_session: Optional[session.Session] = None,
) -> entities.EvalResult:
    """
    Run the logic of the eval harness for a single eval item.

    :param eval_item: The eval item to evaluate
    :param config: The evaluation config
    :param model: Optional model to use for generating responses and traces
    """
    session.set_session(current_session)

    if model:
        eval_item = _populate_model_result_to_eval_item(
            eval_item=eval_item,
            model_result=models.invoke_model(model, eval_item, run_id),
        )
        # Skip the evaluation if invoking the model failed
        if eval_item.model_error_message is not None:
            try:
                client.emit_client_error_usage_event(eval_item.model_error_message)
            except Exception:
                # Telemetry logging failures are non-fatal.
                pass
            return _no_op_eval_result(eval_item)
    else:
        eval_item = _maybe_populate_eval_item_with_trace(eval_item)

    assessment_results = assessments.generate_llm_assessments(
        client=client,
        rate_limiter=rate_limiter,
        eval_item=eval_item,
        config=config,
    )

    metric_results = metrics.compute_eval_metrics(
        eval_item=eval_item,
        assessment_results=assessment_results,
        metrics=metrics.BUILT_IN_METRICS + config.custom_metrics,
    )

    return entities.EvalResult(
        eval_item=eval_item,
        assessment_results=assessment_results,
        overall_assessment=rca.compute_overall_assessment(
            assessment_results, metric_results
        ),
        metric_results=metric_results,
    )


def _no_op_eval_result(eval_item: entities.EvalItem) -> entities.EvalResult:
    """
    Create a no-op eval result for the eval item for skipping the evaluation.

    :param eval_item: The eval item to create a no-op eval result for
    :return: The no-op eval result
    """
    return entities.EvalResult(
        eval_item=eval_item,
        assessment_results=[],
        overall_assessment=None,
        metric_results=[],
    )


def _populate_model_result_to_eval_item(
    eval_item: entities.EvalItem, model_result: models.ModelResult
) -> entities.EvalItem:
    """
    Populate the model result to the eval item in place.

    :param eval_item: The eval item to populate the model result
    :param model_result: The model result to populate
    :return: The populated eval item
    """
    eval_item.answer = model_result.response
    # The response needs to be json-serializable, so we try to convert it to a dict.
    try:
        eval_item.raw_response = input_output_utils.parse_variant_data(
            model_result.raw_model_output
        )
    except Exception as e:
        raise ValueError(
            f"The response from the model must be JSON serializable: {type(model_result.raw_model_output)}. "
        ) from e
    eval_item.retrieval_context = model_result.retrieval_context
    eval_item.tool_calls = model_result.tool_calls
    eval_item.trace = model_result.trace
    eval_item.model_error_message = model_result.error_message
    return eval_item


def _maybe_populate_eval_item_with_trace(eval_item: entities.EvalItem):
    """
    Populate the eval item in place by extracting additional information from the trace.

    Keep the existing values in the eval item if they already exist.
    """
    # Extract tool calls from the trace, or response if trace is not available.
    eval_item.tool_calls = traces.extract_tool_calls(
        response=eval_item.raw_response, trace=eval_item.trace
    )

    # Skip if the trace is None
    if eval_item.trace is None:
        return eval_item

    eval_item.answer = (
        input_output_utils.response_to_string(
            traces.extract_model_output_from_trace(eval_item.trace)
        )
        if eval_item.answer is None
        else eval_item.answer
    )
    eval_item.retrieval_context = (
        traces.extract_retrieval_context_from_trace(eval_item.trace)
        if eval_item.retrieval_context is None
        else eval_item.retrieval_context
    )

    return eval_item


def _emit_custom_assessments_usage_event_if_present(
    client: managed_rag_client.ManagedRagClient,
    assessment_configs: List[assessment_config.AssessmentConfig],
):
    # TODO: change this to use the new usage tracking API
    evaluation_metric_configs = [
        assessment_conf
        for assessment_conf in assessment_configs
        if isinstance(
            assessment_conf, assessment_config.EvaluationMetricAssessmentConfig
        )
    ]

    if evaluation_metric_configs:
        try:
            batch_size = session.current_session().session_batch_size
            client.emit_chat_assessment_usage_event(
                evaluation_metric_configs, batch_size
            )
        except Exception:
            # Telemetry logging failures are non-fatal.
            # Don't want to indicate to users that we're emitting data
            # TODO [ML-43811]: handle this case better since it means we have a loss of billing data
            pass


def _emit_custom_metric_usage_event_if_present(
    client: managed_rag_client.ManagedRagClient,
    custom_metrics: List[agent_custom_metrics.CustomMetric],
    metric_stats: Optional[Dict[str, per_run_metrics.MetricAggregateData]] = None,
):
    if custom_metrics:
        try:
            batch_size = session.current_session().session_batch_size
            client.emit_custom_metric_usage_event(
                custom_metrics=custom_metrics,
                eval_count=batch_size,
                metric_stats=metric_stats,
            )
        except Exception:
            # Telemetry logging failures are non-fatal.
            # Don't want to indicate to users that we're emitting data
            # TODO [ML-43811]: handle this case better since it means we have a loss of billing data
            pass


def _build_rate_limiter_for_assessment() -> rate_limit.RateLimiter:
    """Build a rate limiter for the assessment."""
    # Return a no-op rate limiter if the rate limiter for assessment is not enabled
    if not env_vars.RAG_EVAL_ENABLE_RATE_LIMIT_FOR_ASSESSMENT.get():
        return rate_limit.RateLimiter.no_op()

    # For now, rate limiter config is from environment variables
    rate_limit_config = rate_limit.RateLimitConfig(
        quota=env_vars.RAG_EVAL_RATE_LIMIT_QUOTA.get(),
        time_window_in_seconds=env_vars.RAG_EVAL_RATE_LIMIT_TIME_WINDOW_IN_SECONDS.get(),
    )
    return rate_limit.RateLimiter.build(
        quota=rate_limit_config.quota,
        time_window_in_seconds=rate_limit_config.time_window_in_seconds,
    )
