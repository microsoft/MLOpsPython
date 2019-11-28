import os
import sys
from azureml.core import Workspace
from azureml.core.image import ContainerImage, Image
from azureml.core.model import Model
sys.path.append(os.path.abspath("./ml_service/util"))  # NOQA: E402
from env_variables import Env

e = Env()

# Get Azure machine learning workspace
ws = Workspace.get(
    name=e.workspace_name,
    subscription_id=e.subscription_id,
    resource_group=e.resource_group
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
