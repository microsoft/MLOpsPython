from azureml.pipeline.core import PublishedPipeline
from azureml.core import Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
import os
import sys
sys.path.append(os.path.abspath("./ml_service/util"))  # NOQA: E402
from env_variables import Env


def main():
    e = Env()
    service_principal = ServicePrincipalAuthentication(
            tenant_id=e.tenant_id,
            service_principal_id=e.app_id,
            service_principal_password=e.app_secret)

    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group,
        auth=service_principal
    )

    # Find the pipeline that was published by the specified build ID
    pipelines = PublishedPipeline.list(aml_workspace)
    matched_pipes = []

    for p in pipelines:
        if p.name == e.pipeline_name:
            if p.version == e.build_id:
                matched_pipes.append(p)

    if(len(matched_pipes) > 1):
        published_pipeline = None
        raise Exception(f"Multiple active pipelines are published for build {e.build_id}.")  # NOQA: E501
    elif(len(matched_pipes) == 0):
        published_pipeline = None
        raise KeyError(f"Unable to find a published pipeline for this build {e.build_id}")  # NOQA: E501
    else:
        published_pipeline = matched_pipes[0]
        print("published pipeline id is", published_pipeline.id)

        # Save the Pipeline ID for other AzDO jobs after script is complete
        os.environ['amlpipeline_id'] = published_pipeline.id
        savePIDcmd = 'echo "export AMLPIPELINE_ID=$amlpipeline_id" >tmp.sh'
        os.system(savePIDcmd)

        # Set this to True for local development or
        # if not using Azure DevOps pipeline execution task
        skip_train_execution = True
        if(skip_train_execution is False):
            pipeline_parameters = {"model_name": e.model_name}
            response = published_pipeline.submit(
                aml_workspace,
                e.experiment_name,
                pipeline_parameters)

            run_id = response.id
            print("Pipeline run initiated ", run_id)


if __name__ == "__main__":
    main()
