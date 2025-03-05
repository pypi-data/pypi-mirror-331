import logging
from dataclasses import dataclass
from typing import Optional

from mlflow.tracing.destination import TraceDestination

from databricks.rag_eval import context, entities, env_vars

_logger = logging.getLogger(__name__)


@dataclass
class DatabricksAgentMonitoringDestination(TraceDestination):
    """
    A destination representing a Databricks agent monitor.
    Sets databricks_monitor_id to the endpoint name for the monitor for the provided
    experiment id, if a monitor is found. Sets to None otherwise.
    """

    experiment_id: str
    databricks_monitor_id: Optional[str] = None

    @property
    def type(self) -> str:
        return "databricks-ingestion-endpoint"

    @property
    def _export_to_serving_endpoint(self) -> bool:
        # TODO(ML-50681): Clean up once trace server is fully deployed
        return not env_vars.AGENT_EVAL_TRACE_SERVER_ENABLED.get()

    @context.eval_context
    def __init__(self, *, experiment_id: str):
        self.experiment_id = experiment_id

        managed_evals_client = context.get_context().build_managed_evals_client()
        monitors = managed_evals_client.list_monitors(
            experiment_id=experiment_id,
        )

        # Find first external agent monitor associated with the experiment.
        # There should be only one due to changes made in ML-50204.
        external_monitor = None
        for monitor in monitors:
            if isinstance(monitor, entities.ExternalMonitor):
                external_monitor = monitor
                break

        if external_monitor is None:
            _logger.warning(
                f"Unable to find a monitor for experiment id='{experiment_id}'. "
                f"Traces will not be available in Databricks until a monitor is created "
                f"and this agent is restarted."
            )
            return

        self.databricks_monitor_id = external_monitor.ingestion_endpoint_name
