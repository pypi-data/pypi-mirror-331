from databricks.agents.utils.mlflow_utils import get_workspace_url


def get_monitoring_page_url(experiment_id: str, endpoint_name: str) -> str:
    """Get the monitoring page URL.

    Args:
        experiment_id (str): id of the experiment
        endpoint_name (str): name of the agent serving endpoint

    Returns:
        str: the monitoring page URL
    """
    return f"{get_workspace_url()}/ml/experiments/{experiment_id}/evaluation-monitoring?endpointName={endpoint_name}"
