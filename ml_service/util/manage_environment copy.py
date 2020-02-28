from azureml.core import Workspace, Environment
from azureml.core import Workspace
import os


def get_environment(
    workspace: Workspace,
    environment_name: str,
    create_new: bool = False
):
    try:

        environments = Environment.list(workspace=workspace)
        restored_environment = None
        for env in environments:
            if env == environment_name:
                restored_environment = env

        if restored_environment is None or create_new:
            new_env = Environment.from_conda_specification(environment_name, os.path.join("", "conda_dependencies.yml"))  # NOQA: E501
            restored_environment = new_env
            restored_environment.register(workspace)

        return restored_environment
    except Exception as e:
        print(e)
        exit(1)


if __name__ == '__main__':
    aml_workspace = Workspace.get(
        name='mlopspython-aml', subscription_id='92c76a2f-0e1c-4216-b65e-abf7a3f34c1e', resource_group='MLOpsPythonCI')
    environment = get_environment(
        aml_workspace, 'diabetes_regression__training_env', create_new=False)
