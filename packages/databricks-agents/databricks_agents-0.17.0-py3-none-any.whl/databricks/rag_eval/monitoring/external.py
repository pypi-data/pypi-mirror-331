import logging
from typing import cast

import mlflow
import pyspark
from mlflow import MlflowClient
from mlflow import types as mlflow_types
from mlflow.models.model import ModelInfo
from mlflow.models.signature import ModelSignature
from tenacity import RetryError, retry, retry_if_result, stop_after_delay, wait_fixed

import databricks.rag_eval
from databricks import sdk
from databricks.agents.utils.mlflow_utils import get_databricks_uc_registry_uri
from databricks.agents.utils.uc import _sanitize_model_name
from databricks.rag_eval.monitoring.trace_ingestion_model import (
    EXTERNAL_TRACE_INGESTION_MODEL_NAME,
)
from databricks.rag_eval.utils import model_utils, uc_utils
from databricks.sdk.errors.platform import ResourceDoesNotExist
from databricks.sdk.service import catalog, serving

# Setup logger to stream to stdout messages at the "INFO" level and above
_logger = logging.getLogger(__name__)

TRACE_INGESTION_MODEL_VERSION = 1


def _create_external_trace_ingestion_model(
    model: uc_utils.UnityCatalogEntity,
) -> ModelInfo:
    """Create a new external trace ingestion model in the registry.

    Assumes the model does not already exist in the registry.

    Args:
        model (uc_utils.UnityCatalogEntity): The model's Unity Catalog entity.

    Returns:
        ModelInfo: Information on the created model.
    """
    input_schema = mlflow_types.Schema(
        [mlflow_types.ColSpec(mlflow_types.DataType.string, "inputs")]
    )
    # output schema cannot be empty
    output_schema = mlflow_types.Schema(
        [mlflow_types.ColSpec(mlflow_types.DataType.string, "result")]
    )
    input_signature = ModelSignature(inputs=input_schema, outputs=output_schema)

    mlflow.set_registry_uri(get_databricks_uc_registry_uri())
    with mlflow.start_run(run_name="external-trace-ingestion-model"):
        model_info = mlflow.pyfunc.log_model(
            artifact_path=model.entity,
            signature=input_signature,
            loader_module="trace_ingestion_model",
            pip_requirements=[
                "mlflow",
            ],
            code_paths=[databricks.rag_eval.monitoring.trace_ingestion_model.__file__],
            registered_model_name=model.fullname,
        )

    _setup_trace_ingestion_model_permissions(model.fullname)
    return model_info


def _setup_trace_ingestion_model_permissions(model_fullname: str):
    """Set up permissions for the external trace ingestion model.

    Args:
        model_fullname (str): Target model's UC fullname.
    """
    w = sdk.WorkspaceClient()
    w.grants.update(
        securable_type=catalog.SecurableType.FUNCTION,
        full_name=model_fullname,
        changes=[
            catalog.PermissionsChange(
                principal="account users",
                add=[catalog.Privilege.EXECUTE],
            )
        ],
    )


def _validate_external_trace_ingestion_model(model: ModelInfo):
    """Validate the signature of an external trace ingestion model.

    Args:
        model (ModelInfo): The model to validate.

    Raises:
        ModelHasInvalidSignature: When the model has an invalid signature.
    """
    signature = model.signature
    in_properties = signature.inputs.to_dict()
    out_properties = signature.outputs.to_dict()

    expected_in_properties = {"type": "string", "name": "inputs", "required": True}
    expected_out_properties = {"type": "string", "name": "result", "required": True}
    if len(in_properties) != 1 or in_properties[0] != expected_in_properties:
        raise model_utils.ModelHasInvalidSignature("Has invalid input schema")
    if len(out_properties) != 1 or out_properties[0] != expected_out_properties:
        raise model_utils.ModelHasInvalidSignature("Has invalid output schema")


def _build_trace_ingestion_serving_config(
    model: uc_utils.UnityCatalogEntity, endpoint_name: str
) -> serving.EndpointCoreConfigInput:
    """Builds the core configuration for a trace ingestion serving endpoint.

    Args:
        model (uc_utils.UnityCatalogEntity): The trace ingestion model.
        endpoint_name (str): The name of the serving endpoint.

    Returns:
        EndpointCoreConfigInput: The core configuration for the trace ingestion serving endpoint.
    """
    table_name = model_utils.build_inference_table_name(endpoint_name)

    return serving.EndpointCoreConfigInput(
        name=endpoint_name,
        served_entities=[
            serving.ServedEntityInput(
                name=EXTERNAL_TRACE_INGESTION_MODEL_NAME,
                entity_name=model.fullname,
                entity_version=str(TRACE_INGESTION_MODEL_VERSION),
                workload_size=serving.ServedModelInputWorkloadSize.MEDIUM.value,
                scale_to_zero_enabled=False,
                environment_vars=None,
                instance_profile_arn=None,
            )
        ],
        traffic_config=serving.TrafficConfig(
            routes=[
                serving.Route(
                    served_model_name=EXTERNAL_TRACE_INGESTION_MODEL_NAME,
                    traffic_percentage=100,
                ),
            ]
        ),
        auto_capture_config=serving.AutoCaptureConfigInput(
            enabled=True,
            catalog_name=model.catalog,
            schema_name=model.schema,
            table_name_prefix=table_name,
        ),
    )


def _validate_external_trace_serving_endpoint(
    endpoint: serving.ServingEndpointDetailed,
    expected_model: uc_utils.UnityCatalogEntity,
):
    """Validate that a serving endpoint is serving a trace ingestion model.

    Args:
        endpoint (ServingEndpointDetailed): The serving endpoint to validate.
        expected_model (uc_utils.UnityCatalogEntity): The trace ingestion model that should be served.

    Raises:
        ValueError: When the serving endpoint is invalid.
    """
    served_entities = (endpoint.config or endpoint.pending_config).served_entities
    if served_entities is None or len(served_entities) != 1:
        raise model_utils.InvalidServingEndpoint(
            "endpoint must have exactly one served entity"
        )
    if served_entities[0].entity_name != expected_model.fullname:
        raise model_utils.InvalidServingEndpoint(
            f'endpoint must be serving "{expected_model.fullname}" model'
        )


def _build_endpoint_name(monitoring_table_name: str) -> str:
    """Builds the name of the serving endpoint associated with a given monitoring table.

    Args:
        monitoring_table_name (str): The name of the monitoring table.

    Returns:
        str: The name of the serving endpoint.
    """
    prefix = "monitor_"
    truncated_monitoring_table_name = monitoring_table_name[
        : uc_utils.MAX_UC_ENTITY_NAME_LEN - len(prefix)
    ]
    sanitized_truncated_model_name = _sanitize_model_name(
        truncated_monitoring_table_name
    )
    return f"{prefix}{sanitized_truncated_model_name}"


@retry(
    stop=stop_after_delay(30 * 60),  # Stop after 30 minutes
    wait=wait_fixed(30),  # Wait 30 seconds between retries
    retry=retry_if_result(lambda result: not result),  # Retry if result is False
)
def _is_endpoint_ready(
    endpoint_name: str, workspace_client: databricks.sdk.WorkspaceClient
) -> bool:
    """Checks if the serving endpoint is ready and not updating.

    Args:
        endpoint_name (str): The name of the serving endpoint.
        workspace_client (databricks.sdk.WorkspaceClient): The Databricks workspace client.

    Returns:
        bool: True if the endpoint is ready, False otherwise.

    Raises:
        Exception: If the endpoint is not ready, the endpoint update fails, or the model deployment fails.
        RetryError: If the endpoint is not ready after 30 minutes.
    """

    if (
        (
            endpoint := cast(
                serving.ServingEndpointDetailed | None,
                workspace_client.serving_endpoints.get(name=endpoint_name),
            )
        )
        and (state := endpoint.state)
        and not (
            state.ready == serving.EndpointStateReady.READY
            and state.config_update == serving.EndpointStateConfigUpdate.NOT_UPDATING
        )
    ):
        # throw if model deployment update somehow fails or is cancelled
        if state.config_update in (
            serving.EndpointStateConfigUpdate.UPDATE_FAILED,
            serving.EndpointStateConfigUpdate.UPDATE_CANCELED,
        ):
            raise Exception(
                f"Failed to create trace ingestion endpoint (status={state.config_update})"
            )

        # throw if noop model deployment cannot be completed (aborted or failed)
        if (
            (config := endpoint.config)
            and (served_entities := config.served_entities)
            and (model_state := served_entities[0].state)
            and (model_deployment_status := model_state.deployment)
            and model_deployment_status
            in (
                serving.ServedModelStateDeployment.FAILED,
                serving.ServedModelStateDeployment.ABORTED,
            )
        ):
            raise Exception(
                f"Failed to deploy trace ingestion endpoint (deployment status={model_deployment_status})"
            )

        print(
            "Trace ingestion endpoint is deploying. This may take several minutes. Waiting...",
            flush=True,
        )
        return False

    print("Trace ingestion endpoint is ready.", flush=True)
    return True


def create_monitoring_table(
    monitoring_table: uc_utils.UnityCatalogEntity,
):
    spark = pyspark.sql.SparkSession.builder.getOrCreate()
    # This will create the table without the schema. The schema will be inferred from the
    # first batch of data when data is streamed in from the monitoring job.
    query = f"""CREATE TABLE IF NOT EXISTS {monitoring_table.fullname} (
        timestamp TIMESTAMP,
        execution_time_ms LONG
    )"""
    spark.sql(query)


def setup_trace_ingestion_endpoint(
    monitoring_table: uc_utils.UnityCatalogEntity,
) -> str:
    """Set up the trace ingestion endpoint for a monitoring table and wait for it to be in a READY state.

    This is required for external agent monitoring.

    Args:
        monitoring_table (uc_utils.UnityCatalogEntity): The monitoring table to set up the trace ingestion endpoint for.

    Raises:
        ValueError: When the existing trace ingestion endpoint or model found is invalid.
    """
    mlflow_client = MlflowClient(registry_uri=get_databricks_uc_registry_uri())
    model_entity = uc_utils.UnityCatalogEntity(
        catalog=monitoring_table.catalog,
        schema=monitoring_table.schema,
        entity=EXTERNAL_TRACE_INGESTION_MODEL_NAME,
    )

    # 1. get model version, or create a new one
    try:
        model_version = model_utils.get_model_version(
            mlflow_client, model_entity, TRACE_INGESTION_MODEL_VERSION
        )
    except model_utils.ModelVersionDoesNotExist:
        # If an existing trace endpoint ingestion model does not have version 1, it likely has been
        # deleted. Since versions are immutable, if we try to create a new version, it will not be
        # version 1. Therefore, we should prompt the user to delete the existing model to try again.
        raise ValueError(
            f'Found existing model "{model_entity.fullname}" that does not have version 1. Please delete the existing model and try again.'
        )
    except model_utils.ModelDoesNotExist:
        model_version = _create_external_trace_ingestion_model(model_entity)
        print(f'Registered trace ingestion model "{model_entity.fullname}"', flush=True)
    else:
        print(
            f'Reusing existing trace ingestion model "{model_entity.fullname}"',
            flush=True,
        )
        # check that the existing model version has the correct signature
        _validate_external_trace_ingestion_model(model_version)

    # 2. get trace ingestion endpoint, or create a new one
    endpoint_name = _build_endpoint_name(monitoring_table.entity)
    workspace_client = sdk.WorkspaceClient()
    try:
        serving_endpoint = workspace_client.serving_endpoints.get(name=endpoint_name)
    except ResourceDoesNotExist:
        model_utils.create_model_serving_endpoint(
            client=workspace_client,
            endpoint_name=endpoint_name,
            config=_build_trace_ingestion_serving_config(model_entity, endpoint_name),
        )
        print(f'Created trace ingestion endpoint "{endpoint_name}"', flush=True)
    else:
        print(f'Found existing trace ingestion endpoint "{endpoint_name}"', flush=True)

        # check that existing trace ingestion endpoint is serving a trace ingestion model
        try:
            _validate_external_trace_serving_endpoint(serving_endpoint, model_entity)
        except model_utils.InvalidServingEndpoint as err:
            raise model_utils.InvalidServingEndpoint(
                f"existing trace ingestion endpoint is invalid: {str(err)}. Please delete the existing serving endpoint as well as the associated inference table and try again."
            )

    try:
        _is_endpoint_ready(endpoint_name, workspace_client)
    except RetryError:
        print(
            "Trace ingestion endpoint is not ready after 30 minutes. Exiting...",
            flush=True,
        )
        return endpoint_name

    print(f'Trace ingestion endpoint "{endpoint_name}" is ready.', flush=True)

    return endpoint_name
