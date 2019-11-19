from azureml.pipeline.core import Pipeline
import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.abspath("./ml_service/util"))  # NOQA: E402
from workspace import get_workspace
from attach_compute import get_compute
from azureml.pipeline.steps import DatabricksStep


def main():
    load_dotenv()
    workspace_name = os.environ.get("WORKSPACE_NAME")
    resource_group = os.environ.get("RESOURCE_GROUP")
    subscription_id = os.environ.get("SUBSCRIPTION_ID")
    tenant_id = os.environ.get("TENANT_ID")
    app_id = os.environ.get("SP_APP_ID")
    app_secret = os.environ.get("SP_APP_SECRET")
    vm_size = os.environ.get("AML_COMPUTE_CLUSTER_CPU_SKU")
    compute_name = os.environ.get("DATABRICKS_COMPUTE_NAME")
    db_cluster_id = os.environ.get("DB_CLUSTER_ID")
    build_id = os.environ.get("BUILD_BUILDID")
    pipeline_name = os.environ.get("TRAINING_PIPELINE_NAME")

    # Get Azure machine learning workspace
    aml_workspace = get_workspace(
        workspace_name,
        resource_group,
        subscription_id,
        tenant_id,
        app_id,
        app_secret)
    print(aml_workspace)

    # Get Azure machine learning cluster
    aml_compute = get_compute(
        aml_workspace,
        compute_name,
        vm_size)
    if aml_compute is not None:
        print(aml_compute)

    train_step = DatabricksStep(
        name="DBPythonInLocalMachine",
        num_workers=1,
        python_script_name="train_with_r_on_databricks.py",
        source_directory="code/training/R",
        run_name='DB_Python_R_demo',
        existing_cluster_id=db_cluster_id,
        compute_target=aml_compute,
        allow_reuse=False
    )

    print("Step Train created")

    steps = [train_step]

    train_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    train_pipeline.validate()
    published_pipeline = train_pipeline.publish(
        name=pipeline_name + "_with_R_on_DB",
        description="Model training/retraining pipeline",
        version=build_id
    )
    print(f'Published pipeline: {published_pipeline.name}')
    print(f'for build {published_pipeline.version}')


if __name__ == '__main__':
    main()
