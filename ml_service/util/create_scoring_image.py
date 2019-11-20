import os
from azureml.core import Workspace
from azureml.core.image import ContainerImage, Image
from azureml.core.model import Model
from azureml.core.authentication import ServicePrincipalAuthentication
from env_variables import Env

e = Env()

SP_AUTH = ServicePrincipalAuthentication(
    tenant_id=e.tenant_id,
    service_principal_id=e.app_id,
    service_principal_password=e.app_secret)

ws = Workspace.get(
    e.workspace_name,
    SP_AUTH,
    e.subscription_id,
    e.resource_group
)


model = Model(ws, name=e.model_name, version=e.model_version)
os.chdir("./code/scoring")

image_config = ContainerImage.image_configuration(
    execution_script="score.py",
    runtime="python",
    conda_file="conda_dependencies.yml",
    description="Image with ridge regression model",
    tags={"area": "diabetes", "type": "regression"},
)

image = Image.create(
    name=e.image_name, models=[model], image_config=image_config, workspace=ws
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
