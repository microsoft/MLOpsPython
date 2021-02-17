from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline
from azureml.core import Workspace
from azureml.core.runconfig import RunConfiguration
from ml_service.util.attach_compute import get_compute
from ml_service.util.env_variables import Env
from ml_service.util.manage_environment import get_environment

from utils.logger.observability import Observability

observability = Observability()


def main():
    e = Env()
    # Get Azure machine learning workspace
    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group,
    )
    observability.log("get_workspace:")
    observability.log(aml_workspace)

    # Get Azure machine learning cluster
    aml_compute = get_compute(aml_workspace, e.compute_name, e.vm_size)
    if aml_compute is not None:
        observability.log("aml_compute:")
        observability.log(aml_compute)

    # Create a reusable Azure ML environment
    # Make sure to include `r-essentials'
    #   in diabetes_regression/conda_dependencies.yml
    environment = get_environment(
        aml_workspace,
        e.aml_env_name,
        conda_dependencies_file=e.aml_env_train_conda_dep_file,
        create_new=e.rebuild_env,
    )  # NOQA: E501
    run_config = RunConfiguration()
    run_config.environment = environment

    train_step = PythonScriptStep(
        name="Train Model",
        script_name="train_with_r.py",
        compute_target=aml_compute,
        source_directory="diabetes_regression/training/R",
        runconfig=run_config,
        allow_reuse=False,
    )
    observability.log("Step Train created")

    steps = [train_step]

    train_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    train_pipeline.validate()
    published_pipeline = train_pipeline.publish(
        name=e.pipeline_name,
        description="Model training/retraining pipeline",
        version=e.build_id,
    )
    observability.log(f"Published pipeline: {published_pipeline.name}")
    observability.log(f"for build {published_pipeline.version}")


if __name__ == "__main__":
    main()
