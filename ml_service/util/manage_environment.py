from azureml.core import Workspace, Environment
import hashlib


def get_environment(
    workspace: Workspace,
    base_name: str,
    environment_file: str,
):
    """
    Get or create an Azure ML environment definition from a Conda YAML file.
    For DevOps scenarios, it's important to have reproducible outcomes,
    so that environments should be automatically updated whenever the Conda
    YAML file is modified. It's also important that the pipeline can run
    in multiple branches in parallel without interference. To enable that,
    this function automatically creates an environment name from a base
    name with a checksum appended. If that environment already exists,
    it is retrieved, otherwise it is created from the Conda file.
    """

    with open(environment_file, 'rb') as file:
        checksum = hashlib.sha1(file.read()).hexdigest()

    environment_name = base_name + "_" + checksum
    try:
        env = Environment.get(
            workspace=workspace, name=environment_name)
        print(f'Reusing environment {env}')
    except Exception:
        print(f'Creating environment {environment_name}')
        env = create_environment(
            workspace, environment_name, environment_file)
    return env


def create_environment(
    workspace: Workspace,
    environment_name: str,
    environment_file: str,
):
    print("Creating a new environment " + environment_name)

    try:
        aml_env = Environment.from_conda_specification(
            name=environment_name,
            file_path=environment_file)
        aml_env.register(workspace)
        return aml_env
    except Exception as e:
        print(e)
        print('An error occurred while creating an environment.')
        raise
