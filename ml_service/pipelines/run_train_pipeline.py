from azureml.pipeline.core import PublishedPipeline
from azureml.core import Experiment, Workspace
import argparse
from ml_service.util.env_variables import Env

from utils.logger.logger_interface import Severity
from utils.logger.observability import Observability

observability = Observability()


def main():
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

    e = Env()

    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group
    )

    # Find the pipeline that was published by the specified build ID
    pipelines = PublishedPipeline.list(aml_workspace)
    matched_pipes = []

    for p in pipelines:
        if p.name == e.pipeline_name:
            if p.version == e.build_id:
                matched_pipes.append(p)

    if (len(matched_pipes) > 1):
        published_pipeline = None
        error = f"Multiple active pipelines are published for build {e.build_id}."  # NOQA: E501
        observability.log(description=error, severity=Severity.ERROR)
        raise Exception(error)
    elif (len(matched_pipes) == 0):
        published_pipeline = None
        error = f"Unable to find a published pipeline for this build " \
            f"{e.build_id}"
        observability.log(description=error, severity=Severity.ERROR)
        raise KeyError(error)  # NOQA: E501
    else:
        published_pipeline = matched_pipes[0]
        observability.log("published pipeline id is"
                          + str(published_pipeline.id))

        # Save the Pipeline ID for other AzDO jobs after script is complete
        if args.output_pipeline_id_file is not None:
            with open(args.output_pipeline_id_file, "w") as out_file:
                out_file.write(published_pipeline.id)

        if (args.skip_train_execution is False):
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

            observability.log("Pipeline run initiated " + str(run.id))


if __name__ == "__main__":
    main()
