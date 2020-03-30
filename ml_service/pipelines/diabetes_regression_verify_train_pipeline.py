import argparse
import sys
import os
from azureml.core import Run, Experiment, Workspace
from ml_service.util.env_variables import Env
from diabetes_regression.util.model_helper import get_latest_model


def main():

    run = Run.get_context()

    if (run.id.startswith('OfflineRun')):
        from dotenv import load_dotenv
        load_dotenv()
        sources_dir = os.environ.get("SOURCES_DIR_TRAIN")
        if (sources_dir is None):
            sources_dir = 'diabetes_regression'
        workspace_name = os.environ.get("WORKSPACE_NAME")
        experiment_name = os.environ.get("EXPERIMENT_NAME")
        resource_group = os.environ.get("RESOURCE_GROUP")
        subscription_id = os.environ.get("SUBSCRIPTION_ID")
        build_id = os.environ.get('BUILD_BUILDID')
        aml_workspace = Workspace.get(
            name=workspace_name,
            subscription_id=subscription_id,
            resource_group=resource_group
        )
        ws = aml_workspace
        exp = Experiment(ws, experiment_name)
    else:
        exp = run.experiment

    e = Env()

    parser = argparse.ArgumentParser("register")
    parser.add_argument(
        "--build_id",
        type=str,
        help="The Build ID of the build triggering this pipeline run",
    )
    parser.add_argument(
        "--output_model_version_file",
        type=str,
        default="model_version.txt",
        help="Name of a file to write model version to"
    )

    args = parser.parse_args()
    if (args.build_id is not None):
        build_id = args.build_id
    model_name = e.model_name

    try:
        tag_name = 'BuildId'
        model = get_latest_model(
            model_name, tag_name, build_id, exp.workspace)
        if (model is not None):
            print("Model was registered for this build.")
        if (model is None):
            print("Model was not registered for this run.")
            sys.exit(1)
    except Exception as e:
        print(e)
        print("Model was not registered for this run.")
        sys.exit(1)

    # Save the Model Version for other AzDO jobs after script is complete
    if args.output_model_version_file is not None:
        with open(args.output_model_version_file, "w") as out_file:
            out_file.write(str(model.version))


if __name__ == '__main__':
    main()
