from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.core.runconfig import RunConfiguration, CondaDependencies
from azureml.core import Datastore
import datetime
import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.abspath("./aml_service"))  # NOQA: E402
from workspace import get_workspace
from attach_compute import get_compute


def main():
    load_dotenv()
    workspace_name = os.environ.get("AML_WORKSPACE_NAME")
    resource_group = os.environ.get("RESOURCE_GROUP")
    subscription_id = os.environ.get("SUBSCRIPTION_ID")
    tenant_id = os.environ.get("TENANT_ID")
    app_id = os.environ.get("SP_APP_ID")
    app_secret = os.environ.get("SP_APP_SECRET")
    sources_directory_train = os.environ.get("SOURCES_DIR_TRAIN")
    train_script_path = os.environ.get("TRAIN_SCRIPT_PATH")
    evaluate_script_path = os.environ.get("EVALUATE_SCRIPT_PATH")
    register_script_path = os.environ.get("REGISTER_SCRIPT_PATH")
    vm_size_cpu = os.environ.get("AML_COMPUTE_CLUSTER_CPU_SKU")
    compute_name_cpu = os.environ.get("AML_COMPUTE_CLUSTER_NAME")
    experiment_name = os.environ.get("EXPERIMENT_NAME")
    model_name = os.environ.get("MODEL_NAME")

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
    aml_compute_cpu = get_compute(
        aml_workspace,
        compute_name_cpu,
        vm_size_cpu)
    if aml_compute_cpu is not None:
        print(aml_compute_cpu)

    run_config = RunConfiguration(conda_dependencies=CondaDependencies.create(
        conda_packages=['numpy', 'pandas',
                        'scikit-learn', 'tensorflow', 'keras'],
        pip_packages=['azure', 'azureml-core',
                      'azure-storage',
                      'azure-storage-blob'])
    )
    run_config.environment.docker.enabled = True

    model_name = PipelineParameter(
        name="model_name", default_value=model_name)
    def_blob_store = Datastore(aml_workspace, "workspaceblobstore")
    jsonconfigs = PipelineData("jsonconfigs", datastore=def_blob_store)
    config_suffix = datetime.datetime.now().strftime("%Y%m%d%H")

    train_step = PythonScriptStep(
        name="Train Model",
        script_name=train_script_path,
        compute_target=aml_compute_cpu,
        source_directory=sources_directory_train,
        arguments=[
            "--config_suffix", config_suffix,
            "--json_config", jsonconfigs,
            "--model_name", model_name,
        ],
        runconfig=run_config,
        # inputs=[jsonconfigs],
        outputs=[jsonconfigs],
        allow_reuse=False,
    )
    print("Step Train created")

    evaluate_step = PythonScriptStep(
        name="Evaluate Model ",
        script_name=evaluate_script_path,
        compute_target=aml_compute_cpu,
        source_directory=sources_directory_train,
        arguments=[
            "--config_suffix", config_suffix,
            "--json_config", jsonconfigs,
        ],
        runconfig=run_config,
        inputs=[jsonconfigs],
        # outputs=[jsonconfigs],
        allow_reuse=False,
    )
    print("Step Evaluate created")

    register_model_step = PythonScriptStep(
        name="Register New Trained Model",
        script_name=register_script_path,
        compute_target=aml_compute_cpu,
        source_directory=sources_directory_train,
        arguments=[
            "--config_suffix", config_suffix,
            "--json_config", jsonconfigs,
            "--model_name", model_name,
        ],
        runconfig=run_config,
        inputs=[jsonconfigs],
        # outputs=[jsonconfigs],
        allow_reuse=False,
    )
    print("Step register model created")

    evaluate_step.run_after(train_step)
    register_model_step.run_after(evaluate_step)
    steps = [register_model_step]

    train_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    train_pipeline.validate()
    train_pipeline.submit(experiment_name=experiment_name)

    train_pipeline_json = {}
    train_pipeline_json["rest_endpoint"] = train_pipeline.endpoint
    with open($(Build.ArtifactStagingDirectory)"/train_pipeline.json", "w") as outfile:
        json.dump(train_pipeline_json, outfile)


if __name__ == '__main__':
    main()
