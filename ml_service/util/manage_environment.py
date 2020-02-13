from azureml.core import Workspace, Environment


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
            new_env = Environment.from_conda_specification(name=environment_name,  # NOQA: E501
                                                           file_path="MLOpsPython\diabetes_regression\conda_dependencies.yml")  # NOQA: E501
            restored_environment = new_env
            restored_environment.register(workspace)

        return restored_environment
    except Exception as e:
        print(e)
        exit(1)
