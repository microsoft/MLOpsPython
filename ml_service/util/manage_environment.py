from azureml.core import Workspace, Environment
from ml_service.util.env_variables import Env
import os


def get_environment(
    workspace: Workspace,
    environment_name: str,
    create_new: bool = False
):
    try:
        e = Env()
        environments = Environment.list(workspace=workspace)
        restored_environment = None
        for env in environments:
            if env == environment_name:
                restored_environment = environments[environment_name]

        if restored_environment is None or create_new:
            new_env = Environment.from_conda_specification(environment_name, os.path.join(e.sources_directory_train, "conda_dependencies.yml"))  # NOQA: E501
            restored_environment = new_env
            restored_environment.register(workspace)

        if restored_environment is not None:
            print(restored_environment)
        return restored_environment
    except Exception as e:
        print(e)
        exit(1)
