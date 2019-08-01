import sys
import os.path
import argparse
from dotenv import load_dotenv
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core.authentication import ServicePrincipalAuthentication

# Load the environment variables from .env in case this script
# is called outside an existing process
load_dotenv()

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--TENANT_ID')
PARSER.add_argument('--APP_ID')
PARSER.add_argument('--APP_SECRET')
PARSER.add_argument('--MODEL_PATH')
PARSER.add_argument('--MODEL_NAME')
PARSER.add_argument('--AZUREML_ARM_WORKSPACE_NAME')
PARSER.add_argument('--AZUREML_ARM_SUBSCRIPTION')
PARSER.add_argument('--AZUREML_ARM_RESOURCEGROUP')


ARGS = PARSER.parse_args()
TENANT_ID = ARGS.TENANT_ID
APP_ID = ARGS.APP_ID
APP_SECRET = ARGS.APP_SECRET
MODEL_PATH = ARGS.MODEL_PATH
MODEL_NAME = ARGS.MODEL_NAME
WORKSPACE_NAME = ARGS.AZUREML_ARM_WORKSPACE_NAME
SUBSCRIPTION_ID = ARGS.AZUREML_ARM_SUBSCRIPTION
RESOURCE_GROUP = ARGS.AZUREML_ARM_RESOURCEGROUP


if os.path.isfile(MODEL_PATH) is False:
    print("The given model path %s is invalid" % (MODEL_PATH))
    sys.exit(1)

SP_AUTH = ServicePrincipalAuthentication(
    tenant_id=TENANT_ID,
    service_principal_id=APP_ID,
    service_principal_password=APP_SECRET)

WORKSPACE = Workspace.get(
    WORKSPACE_NAME,
    SP_AUTH,
    SUBSCRIPTION_ID,
    RESOURCE_GROUP
)

try:
    MODEL = Model.register(
        model_path=MODEL_PATH,
        model_name=MODEL_NAME,
        description="Pepsi Forecasting Model",
        workspace=WORKSPACE)

    print("Model registered successfully. ID: " + MODEL.id)
except Exception as caught_error:
    print("Error while registering the model: " + str(caught_error))
    sys.exit(1)
