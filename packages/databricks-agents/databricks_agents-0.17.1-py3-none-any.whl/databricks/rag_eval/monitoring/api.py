import logging
import os
from warnings import warn

import mlflow
import requests
from mlflow.tracking import fluent

from databricks.rag_eval import context
from databricks.rag_eval.mlflow import mlflow_utils
from databricks.rag_eval.monitoring import entities
from databricks.rag_eval.monitoring import external as external_monitor
from databricks.rag_eval.utils import model_utils, uc_utils
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import platform as platform_errors

_logger = logging.getLogger(__name__)


def _get_managed_evals_client():
    return context.get_context().build_managed_evals_client()


def _parse_monitoring_config(
    monitoring_config: dict | entities.MonitoringConfig,
) -> entities.MonitoringConfig:
    assert monitoring_config is not None, "monitoring_config is required"
    monitoring_config = entities.MonitoringConfig.from_dict(monitoring_config)

    # Validate sampling.
    assert isinstance(
        monitoring_config.sample, (int, float)
    ), "monitoring_config.sample must be a number"
    assert (
        0 <= monitoring_config.sample <= 1
    ), "monitoring_config.sample must be between 0 and 1"

    if monitoring_config.periodic is not None:
        assert isinstance(
            monitoring_config.periodic.interval, int
        ), "monitoring_config.periodic.interval must be an integer"
        assert monitoring_config.periodic.unit in [
            "HOURS",
            "DAYS",
            "WEEKS",
        ], "monitoring_config.periodic.unit must be one of 'HOURS', 'DAYS', 'WEEKS'"

    # Validate paused.
    assert monitoring_config.paused is None or isinstance(
        monitoring_config.paused, bool
    ), "monitoring_config.paused must be a boolean"

    # Validate metrics.
    assert monitoring_config.metrics is None or (
        isinstance(monitoring_config.metrics, list)
    ), "monitoring_config.metrics must be a list of strings"

    # Validate guidelines
    if monitoring_config.global_guidelines is not None:
        error_msg = "monitoring_config.global_guidelines must be a dictionary of {<guideline_name>: [<guidelines>]}"
        assert isinstance(monitoring_config.global_guidelines, dict), error_msg
        assert all(
            isinstance(g, list) for g in monitoring_config.global_guidelines.values()
        ), error_msg
        assert all(
            isinstance(e, str)
            for g in monitoring_config.global_guidelines.values()
            for e in g
        ), error_msg
        assert all(
            isinstance(k, str) for k in monitoring_config.global_guidelines.keys()
        ), error_msg

    return monitoring_config


def _warn_identifier_deprecation(func_name: str, with_ellipsis: bool = False):
    """Warn about the deprecation of the `identifier` argument in the given function.

    Args:
        func_name (str): Name of function with deprecated `idnetifier` argument.
        with_ellipsis (bool, optional): Whether to include an ellipsis representing
            the rest of the function signature. Defaults to False.
    """
    ellipsis = ", ..." if with_ellipsis else ""
    warn(
        (
            f"Using {func_name} without explicitly specifying an `endpoint_name` "
            "or `monitoring_table` argument is deprecated, and support will "
            f"soon be removed. Please update `{func_name}($ENDPOINT_NAME{ellipsis})` "
            f"calls to instead call `{func_name}(endpoint_name=$ENDPOINT_NAME{ellipsis})."
        ),
        DeprecationWarning,
    )


@context.eval_context
def create_monitor(
    endpoint_name: str,
    *,
    monitoring_config: dict | entities.MonitoringConfig,
    experiment_id: str | None = None,
) -> entities.Monitor:
    """
    Create a monitor for a serving endpoint.

    Args:
        endpoint_name: The name of the serving endpoint.
        monitoring_config: The monitoring configuration.
        experiment_id: The experiment ID to log the monitoring results. Defaults to the experiment
            used to log the model that is serving the provided `endpoint_name`.
    Returns:
        The monitor for the serving endpoint.
    """
    monitoring_config = _parse_monitoring_config(monitoring_config)

    if experiment_id is None:
        # Infer the experiment ID and the workspace path from the current environment.
        experiment = mlflow_utils.infer_experiment_from_endpoint(endpoint_name)
    else:
        experiment = mlflow.get_experiment(experiment_id)

    workspace_path = os.path.dirname(experiment.name)
    return _get_managed_evals_client().create_monitor(
        endpoint_name=endpoint_name,
        monitoring_config=monitoring_config,
        experiment_id=experiment.experiment_id,
        workspace_path=workspace_path,
    )


@context.eval_context
def create_external_monitor(
    *,
    monitoring_table: str,
    monitoring_config: dict | entities.MonitoringConfig,
    experiment_id: str | None = None,
    experiment_name: str | None = None,
) -> entities.ExternalMonitor:
    """Create a monitor for an agent served outside Databricks.

    Args:
        monitoring_table (str): Delta table to write monitoring results to.
            This should be in ``"{catalog}.{schema}.{table}"`` format.
        monitoring_config (dict | MonitoringConfig): The monitor configuration.
        experiment_id (str | None, optional): ID of Mlflow experiment
            that the monitor should be associated with. Defaults to the
            currently active experiment.
        experiment_name (str | None, optional): The name of the Mlflow experiment that the monitor
            should be associated with. Defaults to the currently active experiment.

    Returns:
        ExternalMonitor: The created monitor.
    """
    monitoring_table_uc_entity = uc_utils.UnityCatalogEntity.from_fullname(
        monitoring_table
    )
    endpoint_name = external_monitor.setup_trace_ingestion_endpoint(
        monitoring_table_uc_entity
    )
    monitoring_config = _parse_monitoring_config(monitoring_config)

    mlflow.set_tracking_uri("databricks")
    if experiment_id:
        pass
    elif experiment_name:
        experiment = mlflow.set_experiment(experiment_name=experiment_name)
        experiment_id = experiment.experiment_id
    else:
        # Infer the experiment ID from the current environment.
        try:
            experiment_id = fluent._get_experiment_id()
            if (
                experiment_id
                == mlflow.tracking.default_experiment.DEFAULT_EXPERIMENT_ID
            ):
                raise ValueError
        except Exception:
            raise ValueError(
                "Please provide an experiment_name or run this code within an active experiment."
            )
    try:
        monitor = _get_managed_evals_client().create_monitor(
            endpoint_name=endpoint_name,
            monitoring_config=monitoring_config,
            experiment_id=experiment_id,
            workspace_path=None,
            monitoring_table=monitoring_table,
        )
    except requests.HTTPError as e:
        # If the user doesn't have permission or a referenced table doesn't exist, don't delete
        # the ingestion endpoint so they can fix the error and try again.
        if e.response.status_code not in (403, 404):
            model_utils.delete_model_serving_endpoint(
                client=WorkspaceClient(),
                endpoint_name=endpoint_name,
            )

        raise

    # Create the monitoring table now so that it exists immediately after this function finishes,
    # but allows the service to perform validations.
    try:
        external_monitor.create_monitoring_table(monitoring_table_uc_entity)
    except Exception as e:
        _logger.debug(f"Failed to create monitoring table: {e}")

    print(
        f"Created external monitor successfully using experiment_id '{experiment_id}'.\n\n"
        "You will need this experiment_id when you set your agent's tracing destination to "
        f"`DatabricksAgentMonitoring(experiment_id={experiment_id})`"
    )
    return monitor


@context.eval_context
def get_monitor(
    identifier: str | None = None,
    *,
    endpoint_name: str | None = None,
    monitoring_table: str | None = None,
) -> entities.Monitor | entities.ExternalMonitor:
    """
    Retrieves a monitor for a serving endpoint.

    Args:
        endpoint_name (str, optional): The name of the agent's serving endpoint.
            Only supported for agents served on Databricks.
        monitoring_table (str, optional): The fullname of the monitoring table backed by the monitor.

    Returns:
        Monitor | ExternalMonitor metadata. For external monitors, this will include the status of the ingestion endpoint.
    """
    if identifier is not None:
        endpoint_name = identifier
        _warn_identifier_deprecation("get_monitor")

    monitor = _get_managed_evals_client().get_monitor(
        endpoint_name=endpoint_name,
        monitoring_table=monitoring_table,
    )
    print("Monitor URL: ", monitor.monitoring_page_url)
    return monitor


@context.eval_context
def update_monitor(
    identifier: str | None = None,
    *,
    endpoint_name: str | None = None,
    monitoring_table: str | None = None,
    monitoring_config: dict | entities.MonitoringConfig,
) -> entities.Monitor | entities.ExternalMonitor:
    """
    Partially update a monitor for a serving endpoint.

    Args:
        endpoint_name (str, optional): The name of the agent's serving endpoint.
            Only supported for agents served on Databricks.
        monitoring_table (str, optional): Delta table that monitoring results are written to.
            This should be in ``"{catalog}.{schema}.{table}"`` format.
        monitoring_config: The configuration change, using upsert semantics.

    Returns:
        Monitor | ExternalMonitor: The updated monitor for the serving endpoint.
    """
    assert monitoring_config is not None, "monitoring_config is required"
    monitoring_config = entities.MonitoringConfig.from_dict(monitoring_config)
    # Do not allow partial updates for nested fields.
    if monitoring_config.periodic:
        assert (
            monitoring_config.periodic.interval is not None
            and monitoring_config.periodic.unit is not None
        ), "Partial update for periodic monitoring is not supported."

    if identifier:
        endpoint_name = identifier
        _warn_identifier_deprecation("update_monitor", with_ellipsis=True)

    if not endpoint_name:
        external_monitor = get_monitor(monitoring_table=monitoring_table)
        endpoint_name = external_monitor.ingestion_endpoint_name

    return _get_managed_evals_client().update_monitor(
        endpoint_name=endpoint_name,
        monitoring_config=monitoring_config,
    )


@context.eval_context
def delete_monitor(
    identifier: str | None = None,
    *,
    endpoint_name: str | None = None,
    monitoring_table: str | None = None,
) -> None:
    """
    Deletes a monitor for a serving endpoint.

    Args:
        endpoint_name (str, optional): The name of the agent's serving endpoint.
            Only supported for agents served on Databricks.
        monitoring_table (str, optional): Delta table that monitoring results are written to.
            This should be in ``"{catalog}.{schema}.{table}"`` format.
    """
    if identifier:
        endpoint_name = identifier
        _warn_identifier_deprecation("delete_monitor")

    # for external monitors, find the endpoint name using the monitoring table
    if not endpoint_name:
        external_monitor = get_monitor(monitoring_table=monitoring_table)
        endpoint_name = external_monitor.ingestion_endpoint_name
        try:
            model_utils.delete_model_serving_endpoint(
                client=WorkspaceClient(),
                endpoint_name=endpoint_name,
            )
        except platform_errors.ResourceDoesNotExist:
            # Don't need to fail on this.
            pass

    return _get_managed_evals_client().delete_monitor(endpoint_name=endpoint_name)
