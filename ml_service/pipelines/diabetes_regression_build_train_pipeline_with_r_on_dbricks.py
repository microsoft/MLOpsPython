from azureml.pipeline.core import Pipeline
from azureml.core import Workspace
from ml_service.util.attach_compute import get_compute
from azureml.pipeline.steps import DatabricksStep
from ml_service.util.env_variables import Env


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

    train_step = DatabricksStep(
        name="DBPythonInLocalMachine",
        num_workers=1,
        python_script_name="train_with_r_on_databricks.py",
        source_directory="diabetes_regression/training/R",
        run_name='DB_Python_R_demo',
        existing_cluster_id=e.db_cluster_id,
        compute_target=aml_compute,
        allow_reuse=False
    )

    print("Step Train created")

    steps = [train_step]

    train_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    train_pipeline.validate()
    published_pipeline = train_pipeline.publish(
        name=e.pipeline_name + "_with_R_on_DB",
        description="Model training/retraining pipeline",
        version=e.build_id
    )
    print(f'Published pipeline: {published_pipeline.name}')
    print(f'for build {published_pipeline.version}')


if __name__ == '__main__':
    main()
