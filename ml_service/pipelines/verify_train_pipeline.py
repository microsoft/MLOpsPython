import os
import sys
import argparse
from azureml.core import Run, Experiment, Workspace
sys.path.append(os.path.abspath("./ml_service/util"))  # NOQA: E402
from env_variables import Env


def main():

    run = Run.get_context()
    if (run.id.startswith('OfflineRun')):
        from dotenv import load_dotenv
        # For local development, set values in this section
        load_dotenv()
        sources_dir = os.environ.get("SOURCES_DIR_TRAIN")
        if (sources_dir is None):
            sources_dir = 'diabetes_regression'
        path_to_util = os.path.join(".", sources_dir, "util")
        sys.path.append(os.path.abspath(path_to_util))  # NOQA: E402
        from model_helper import get_model_by_tag
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
        sys.path.append(os.path.abspath("./util"))  # NOQA: E402
        from model_helper import get_model_by_tag
        ws = run.experiment.workspace
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
        model = get_model_by_tag(
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
