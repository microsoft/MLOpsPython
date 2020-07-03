import os
from azureml.core import Workspace, Environment
from ml_service.util.env_variables import Env
from azureml.core.runconfig import DEFAULT_CPU_IMAGE, DEFAULT_GPU_IMAGE

from utils.logger.logger_interface import Severity
from utils.logger.observability import Observability

observability = Observability()


def get_environment(
        workspace: Workspace,
        environment_name: str,
        conda_dependencies_file: str,
        create_new: bool = False,
        enable_docker: bool = None,
        use_gpu: bool = False
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
                os.path.join(e.sources_directory_train, "diabetes_regression/" + conda_dependencies_file),  # NOQA: E501
            )  # NOQA: E501
            restored_environment = new_env
            if enable_docker is not None:
                restored_environment.docker.enabled = enable_docker
                restored_environment.docker.base_image = DEFAULT_GPU_IMAGE if use_gpu else DEFAULT_CPU_IMAGE  # NOQA: E501
            restored_environment.register(workspace)

        if restored_environment is not None:
            observability.log(restored_environment)
        return restored_environment
    except Exception as e:
        observability.log(description=e, severity=Severity.ERROR)
        exit(1)
