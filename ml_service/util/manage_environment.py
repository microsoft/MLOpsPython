
from azureml.core import Workspace, Environment
from ml_service.util.env_variables import Env
from azureml.core.runconfig import DEFAULT_CPU_IMAGE, DEFAULT_GPU_IMAGE
from azureml.core.conda_dependencies import CondaDependencies
import os


def get_environment(
    workspace: Workspace, environment_name: str, create_new: bool = False
):
    try:
        e = Env()
        environments = Environment.list(workspace=workspace)
        restored_environment = None
        for env in environments:
            if env == environment_name:
                restored_environment = environments[environment_name]

        if restored_environment is None or create_new:
            new_env = Environment.from_conda_specification(
                environment_name,
                os.path.join(e.sources_directory_train, "conda_dependencies.yml"),  # NOQA: E501
            )  # NOQA: E501
            restored_environment = new_env
            restored_environment.register(workspace)

        if restored_environment is not None:
            print(restored_environment)
        return restored_environment
    except Exception as e:
        print(e)
        exit(1)


def get_environment_for_scoring(
    workspace: Workspace, environment_name: str, create_new: bool = False
):
    try:
        e = Env()
        environments = Environment.list(workspace=workspace)
        restored_environment = None
        for env in environments:
            if env == environment_name:
                restored_environment = environments[environment_name]

        if restored_environment is None or create_new:
            restored_environment = Environment(environment_name)
            restored_environment.python.conda_dependencies = CondaDependencies.create(  # noqa E501
                pip_packages=["pandas", "scikit-learn", "azureml-sdk"]
            )
            restored_environment.docker.enabled = True
            restored_environment.docker.base_image = DEFAULT_GPU_IMAGE if e.use_gpu_for_scoring else DEFAULT_CPU_IMAGE  # NOQA: E501
            restored_environment.spark.precache_packages = False
            restored_environment.register(workspace)

        if restored_environment is not None:
            print(restored_environment)
        return restored_environment
    except Exception as e:
        print(e)
        exit(1)


def get_environment_for_score_copy(
    workspace: Workspace, environment_name: str, create_new: bool = False
):
    try:
        e = Env()
        environments = Environment.list(workspace=workspace)
        restored_environment = None
        for env in environments:
            if env == environment_name:
                restored_environment = environments[environment_name]

        if restored_environment is None or create_new:
            restored_environment = Environment(environment_name)
            restored_environment.python.conda_dependencies = CondaDependencies.create(  # noqa E501
                pip_packages=["azure-storage-blob", "azureml-sdk"]
            )
            restored_environment.docker.enabled = True
            restored_environment.docker.base_image = DEFAULT_CPU_IMAGE
            restored_environment.register(workspace)

        if restored_environment is not None:
            print(restored_environment)
        return restored_environment
    except Exception as e: # NOQA
        print(e)
        exit(1)
