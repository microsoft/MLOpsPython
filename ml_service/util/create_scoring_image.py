import os
from azureml.core import Workspace
from azureml.core.image import ContainerImage, Image
from azureml.core.model import Model
from dotenv import load_dotenv
from azureml.core.authentication import ServicePrincipalAuthentication

load_dotenv()

TENANT_ID = os.environ.get('TENANT_ID')
APP_ID = os.environ.get('SP_APP_ID')
APP_SECRET = os.environ.get('SP_APP_SECRET')
WORKSPACE_NAME = os.environ.get("BASE_NAME")+"-AML-WS"
SUBSCRIPTION_ID = os.environ.get('SUBSCRIPTION_ID')
RESOURCE_GROUP = os.environ.get("BASE_NAME")+"-AML-RG"
MODEL_NAME = os.environ.get('MODEL_NAME')
MODEL_VERSION = os.environ.get('MODEL_VERSION')
IMAGE_NAME = os.environ.get('IMAGE_NAME')


SP_AUTH = ServicePrincipalAuthentication(
    tenant_id=TENANT_ID,
    service_principal_id=APP_ID,
    service_principal_password=APP_SECRET)

ws = Workspace.get(
    WORKSPACE_NAME,
    SP_AUTH,
    SUBSCRIPTION_ID,
    RESOURCE_GROUP
)


model = Model(ws, name=MODEL_NAME, version=MODEL_VERSION)
os.chdir("./code/scoring")

image_config = ContainerImage.image_configuration(
    execution_script="score.py",
    runtime="python",
    conda_file="conda_dependencies.yml",
    description="Image with ridge regression model",
    tags={"area": "diabetes", "type": "regression"},
)

image = Image.create(
    name=IMAGE_NAME, models=[model], image_config=image_config, workspace=ws
)

image.wait_for_creation(show_output=True)

if image.creation_state != "Succeeded":
    raise Exception("Image creation status: {image.creation_state}")

print("{}(v.{} [{}]) stored at {} with build log {}".format(
    image.name,
    image.version,
    image.creation_state,
    image.image_location,
    image.image_build_log_uri,
)
)
