from azureml.core import Workspace, Environment
from ml_service.util.env_variables import Env


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
                restored_environment = env

        if restored_environment is None or create_new:
            # Read definition from diabetes_regression/azureml_environment.json
            new_env = Environment.load_from_directory(e.sources_directory_train)  # NOQA: E501
            stored_environment = new_env
            restored_environment.register(workspace)

        return restored_environment
    except Exception as e:
        print(e)
        exit(1)
