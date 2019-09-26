import os
from azureml.pipeline.core import PublishedPipeline
from azureml.core import Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
from dotenv import load_dotenv


def main():
    load_dotenv()
    workspace_name = os.environ.get("BASE_NAME")+"-AML-WS"
    resource_group = os.environ.get("BASE_NAME")+"-AML-RG"
    subscription_id = os.environ.get("SUBSCRIPTION_ID")
    tenant_id = os.environ.get("TENANT_ID")
    experiment_name = os.environ.get("EXPERIMENT_NAME")
    model_name = os.environ.get("MODEL_NAME")
    app_id = os.environ.get('SP_APP_ID')
    app_secret = os.environ.get('SP_APP_SECRET')
    release_id = os.environ.get('RELEASE_RELEASEID')
    build_id = os.environ.get('BUILD_BUILDID')

    service_principal = ServicePrincipalAuthentication(
            tenant_id=tenant_id,
            service_principal_id=app_id,
            service_principal_password=app_secret)

    aml_workspace = Workspace.get(
        name=workspace_name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        auth=service_principal
        )

    # Find the pipeline that was published by the specified build ID
    pipelines = PublishedPipeline.list(aml_workspace)
    matched_pipes = []

    for p in pipelines:
        if p.version == build_id:
            matched_pipes.append(p)

    if(len(matched_pipes) > 1):
        published_pipeline = None
        raise Exception(f"Multiple active pipelines are published for build {build_id}.")  # NOQA: E501
    elif(len(matched_pipes) == 0):
        published_pipeline = None
        raise KeyError(f"Unable to find a published pipeline for this build {build_id}")  # NOQA: E501
    else:
        published_pipeline = matched_pipes[0]

    pipeline_parameters = {"model_name": model_name, "release_id": release_id}

    response = published_pipeline.submit(
        aml_workspace,
        experiment_name,
        pipeline_parameters)

    run_id = response.id
    print("Pipeline run initiated ", run_id)


if __name__ == "__main__":
    main()
