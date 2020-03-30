<<<<<<< HEAD
import sys
import os
import json
import requests
from azure.common.credentials import ServicePrincipalCredentials


tenant_id = os.environ.get("TENANT_ID")
app_id = os.environ.get("SP_APP_ID")
app_secret = os.environ.get("SP_APP_SECRET")

try:
    with open("train_pipeline.json") as f:
        train_pipeline_json = json.load(f)
except Exception:
    print("No pipeline json found")
    sys.exit(0)
=======
from azureml.pipeline.core import PublishedPipeline
from azureml.core import Experiment, Workspace
import argparse
from ml_service.util.env_variables import Env


def main():
>>>>>>> af2b77295365f449d535a4903f5516561e82b9fd

    parser = argparse.ArgumentParser("register")
    parser.add_argument(
        "--output_pipeline_id_file",
        type=str,
        default="pipeline_id.txt",
        help="Name of a file to write pipeline ID to"
    )
    parser.add_argument(
        "--skip_train_execution",
        action="store_true",
        help=("Do not trigger the execution. "
              "Use this in Azure DevOps when using a server job to trigger")
    )
    args = parser.parse_args()

<<<<<<< HEAD
credentials = ServicePrincipalCredentials(
    client_id=app_id,
    secret=app_secret,
    tenant=tenant_id
)

token = credentials.token['access_token']
print("token", token)
auth_header = {"Authorization": "Bearer " + token}
=======
    e = Env()
>>>>>>> af2b77295365f449d535a4903f5516561e82b9fd

    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group
    )

<<<<<<< HEAD
response = requests.post(
    rest_endpoint, headers=auth_header,
    json={"ExperimentName": experiment_name,
          "ParameterAssignments": {"model_name": model_name}}
)
=======
    # Find the pipeline that was published by the specified build ID
    pipelines = PublishedPipeline.list(aml_workspace)
    matched_pipes = []
>>>>>>> af2b77295365f449d535a4903f5516561e82b9fd

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
        if args.output_pipeline_id_file is not None:
            with open(args.output_pipeline_id_file, "w") as out_file:
                out_file.write(published_pipeline.id)

        if(args.skip_train_execution is False):
            pipeline_parameters = {"model_name": e.model_name}
            tags = {"BuildId": e.build_id}
            if (e.build_uri is not None):
                tags["BuildUri"] = e.build_uri
            experiment = Experiment(
                workspace=aml_workspace,
                name=e.experiment_name)
            run = experiment.submit(
                published_pipeline,
                tags=tags,
                pipeline_parameters=pipeline_parameters)

            print("Pipeline run initiated ", run.id)


if __name__ == "__main__":
    main()
