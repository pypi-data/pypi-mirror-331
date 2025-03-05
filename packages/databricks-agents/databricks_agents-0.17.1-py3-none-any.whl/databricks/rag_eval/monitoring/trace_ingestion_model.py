# IMPORTANT NOTE: Please don't add any other dependencies to this file other than MLflow.
from mlflow.pyfunc import PythonModel

EXTERNAL_TRACE_INGESTION_MODEL_NAME = "agent_monitoring_trace_ingestion"


class ExternalMonitorTraceIngestionModel(PythonModel):
    def predict(self, model_input):
        return {"result": "ok"}


def _load_pyfunc(model_path):
    return ExternalMonitorTraceIngestionModel()
