import sys
import os
import os.path
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core.authentication import ServicePrincipalAuthentication
from env_variables import Env

e = Env()

if os.path.isfile(e.model_path) is False:
    print("The given model path %s is invalid" % (e.model_path))
    sys.exit(1)

SP_AUTH = ServicePrincipalAuthentication(
    tenant_id=e.tenant_id,
    service_principal_id=e.app_id,
    service_principal_password=e.app_secret)

WORKSPACE = Workspace.get(
    e.workspace_name,
    SP_AUTH,
    e.subscription_id,
    e.resource_group
)

try:
    MODEL = Model.register(
        model_path=e.model_path,
        model_name=e.model_name,
        description="Forecasting Model",
        workspace=e.workspace)

    print("Model registered successfully. ID: " + MODEL.id)
except Exception as caught_error:
    print("Error while registering the model: " + str(caught_error))
    sys.exit(1)
