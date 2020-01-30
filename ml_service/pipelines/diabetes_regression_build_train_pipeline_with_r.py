from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline
from azureml.core import Workspace
from azureml.core.runconfig import RunConfiguration, CondaDependencies
import os
import sys
sys.path.append(os.path.abspath("./ml_service/util"))  # NOQA: E402
from attach_compute import get_compute
from env_variables import Env


def main():
    e = Env()
    # Get Azure machine learning workspace
    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group
    )
    print("get_workspace:")
    print(aml_workspace)

    # Get Azure machine learning cluster
    aml_compute = get_compute(
        aml_workspace,
        e.compute_name,
        e.vm_size)
    if aml_compute is not None:
        print("aml_compute:")
        print(aml_compute)

    run_config = RunConfiguration(conda_dependencies=CondaDependencies.create(
        conda_packages=['numpy', 'pandas',
                        'scikit-learn', 'tensorflow', 'keras'],
        pip_packages=['azure', 'azureml-core',
                      'azure-storage',
                      'azure-storage-blob'])
    )
    run_config.environment.docker.enabled = True
    run_config.environment.docker.base_image = "mcr.microsoft.com/mlops/python"

    train_step = PythonScriptStep(
        name="Train Model",
        script_name="train_with_r.py",
        compute_target=aml_compute,
        source_directory="diabetes_regression/training/R",
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Step Train created")

    steps = [train_step]

    train_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    train_pipeline.validate()
    published_pipeline = train_pipeline.publish(
        name=e.pipeline_name + "_with_R",
        description="Model training/retraining pipeline",
        version=e.build_id
    )
    print(f'Published pipeline: {published_pipeline.name}')
    print(f'for build {published_pipeline.version}')


if __name__ == '__main__':
    main()
