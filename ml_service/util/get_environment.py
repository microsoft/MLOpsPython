from azureml.core import Workspace, Environment


def get_environment(
    workspace: Workspace,
    environment_name: str,
    create_new: bool
):
    try:
        restored_environment = Environment.get(
            workspace=workspace, name=environment_name)
        if create_new:
            new_env = Environment.from_conda_specification(name=environment_name,
                                                           file_path="path-to-conda-specification-file")
            restored_environment = new_env
            restored_environment.register(workspace)
        elif restored_environment is None:
            raise Exception("Environment not found")
        return restored_environment
    except Exception as e:
        print(e)
        print('An error occurred while creating an environment.')
        exit(1)
