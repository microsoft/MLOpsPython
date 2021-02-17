import os
import argparse
from azureml.core import Workspace
from azureml.core.environment import Environment
from azureml.core.model import Model, InferenceConfig
import shutil
from ml_service.util.env_variables import Env

from utils.logger.logger_interface import Severity
from utils.logger.observability import Observability

observability = Observability()

e = Env()

# Get Azure machine learning workspace
ws = Workspace.get(
    name=e.workspace_name,
    subscription_id=e.subscription_id,
    resource_group=e.resource_group
)

parser = argparse.ArgumentParser("create scoring image")
parser.add_argument(
    "--output_image_location_file",
    type=str,
    help=("Name of a file to write image location to, "
          "in format REGISTRY.azurecr.io/IMAGE_NAME:IMAGE_VERSION")
)
args = parser.parse_args()

model = Model(ws, name=e.model_name, version=e.model_version)
sources_dir = e.sources_directory_train
if (sources_dir is None):
    sources_dir = '.'
score_script = os.path.join(".", sources_dir, e.score_script)
score_file = os.path.basename(score_script)
path_to_scoring = os.path.dirname(score_script)
cwd = os.getcwd()
# Copy conda_dependencies.yml into scoring as this method does not accept relative paths. # NOQA: E501
shutil.copy(os.path.join(".", sources_dir,
                         "conda_dependencies.yml"), path_to_scoring)
os.chdir(path_to_scoring)

scoring_env = Environment.from_conda_specification(name="scoringenv", file_path="conda_dependencies.yml")  # NOQA: E501
inference_config = InferenceConfig(
    entry_script=score_file, environment=scoring_env)
package = Model.package(ws, [model], inference_config)
package.wait_for_creation(show_output=True)
# Display the package location/ACR path
observability.log(package.location)

os.chdir(cwd)

if package.state != "Succeeded":
    error = "Image creation status: {package.creation_state}"
    observability.log(description=error, severity=Severity.ERROR)
    raise Exception(error)

observability.log(
    "Package stored at {} with build log {}".format(package.location, package.package_build_log_uri))  # NOQA: E501

# Save the Image Location for other AzDO jobs after script is complete
if args.output_image_location_file is not None:
    observability.log("Writing image location to %s"
                      % args.output_image_location_file)
    with open(args.output_image_location_file, "w") as out_file:
        out_file.write(str(package.location))
