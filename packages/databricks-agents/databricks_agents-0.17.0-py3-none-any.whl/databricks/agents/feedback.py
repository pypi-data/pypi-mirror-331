# IMPORTANT NOTE: Please don't add any other dependencies to this file other than MLflow.
from mlflow.pyfunc import PythonModel

_FEEDBACK_MODEL_NAME = "feedback"


class DummyFeedbackModel(PythonModel):
    def predict(self, model_input):
        return {"result": "ok"}


def _load_pyfunc(model_path):
    return DummyFeedbackModel()
