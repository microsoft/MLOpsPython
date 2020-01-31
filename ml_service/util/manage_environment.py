from azureml.core import Workspace, Environment


def get_environment(
    workspace: Workspace,
    environment_name: str,
    create_new: bool = False
):
    try:

        if create_new:
            new_env = Environment.from_conda_specification(name=environment_name,  # NOQA: E501
                                                           file_path="MLOpsPython\diabetes_regression\conda_dependencies.yml")  # NOQA: E501
            restored_env = new_env  # NOQA: E501
            restored_env.register(workspace)
        else:
            restored_env = Environment.get(
                workspace=workspace, name=environment_name)

        print(
            "packages", restored_env.python.conda_dependencies.serialize_to_string())  # NOQA: E501
        return restored_env
    except Exception as e:
        print(e)
        print('An error occurred while creating an environment.')
        exit(1)
