from azureml.core.authentication import AzureCliAuthentication
from azureml.core.compute import ComputeTarget
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.core import PublishedPipeline
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, PipelineData, StepSequence
from azureml.data.data_reference import DataReference
from azureml.core.runconfig import RunConfiguration, CondaDependencies
from azureml.core import Workspace, Experiment, Datastore
import argparse
import datetime
import requests
import json
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
    vm_size_cpu = os.environ.get("AML_COMPUTE_CLUSTER_CPU_SKU")
    compute_name_cpu = os.environ.get("AML_COMPUTE_CLUSTER_NAME")
    experiment_name = os.environ.get("EXPERIMENT_NAME")

    # Get Azure machine learning workspace
    #aml_workspace = get_workspace(
    #    workspace_name,
    #    resource_group,
    #    subscription_id,
    #    tenant_id,
    #    app_id,
    #    app_secret)
    #print(aml_workspace)    

    # Get Azure machine learning cluster
    #aml_compute_cpu = get_compute(
    #    aml_workspace,
    #    compute_name_cpu,
    #    vm_size_cpu)
    #if aml_compute_cpu is not None:
    #    print(aml_compute_cpu)

    run_config = RunConfiguration(conda_dependencies=CondaDependencies.create(
        conda_packages=['numpy', 'pandas',
                        'scikit-learn', 'tensorflow', 'keras'],
        pip_packages=['azure', 'azureml-core',
                      'azure-storage',
                      'azure-storage-blob'])
    )
    run_config.environment.docker.enabled = True

    aml_compute_cpu=None
    aml_workspace=None
    model_name = PipelineParameter(name="model_name", default_value="sklearn_regression_model.pkl")
    def_blob_store = Datastore(aml_workspace, "workspaceblobstore")
    jsonconfigs = PipelineData("jsonconfigs", datastore=def_blob_store)
    config_suffix = datetime.datetime.now().strftime("%Y%m%d%H")

    train_step = PythonScriptStep(
        name="Train Model",
        script_name="training/train.py",
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

    print("hi")

if __name__ == '__main__':
    main()