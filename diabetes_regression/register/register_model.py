"""
Copyright (C) Microsoft Corporation. All rights reserved.​
 ​
Microsoft Corporation (“Microsoft”) grants you a nonexclusive, perpetual,
royalty-free right to use, copy, and modify the software code provided by us
("Software Code"). You may not sublicense the Software Code or any use of it
(except to your affiliates and to vendors to perform work on your behalf)
through distribution, network access, service agreement, lease, rental, or
otherwise. This license does not purport to express any claim of ownership over
data you may have shared with Microsoft in the creation of the Software Code.
Unless applicable law gives you more rights, Microsoft reserves all other
rights not expressly granted herein, whether by implication, estoppel or
otherwise. ​
 ​
THE SOFTWARE CODE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
MICROSOFT OR ITS LICENSORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THE SOFTWARE CODE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
import json
import os
import sys
import argparse
import traceback
import joblib
from azureml.core import Run, Experiment, Workspace, Dataset
from azureml.core.model import Model as AMLModel
from utils.logger.logger_interface import Severity
from utils.logger.observability import Observability

observability = Observability()


def main():
    run = Run.get_context()
    if (run.id.startswith('OfflineRun')):
        from dotenv import load_dotenv
        # For local development, set values in this section
        load_dotenv()
        workspace_name = os.environ.get("WORKSPACE_NAME")
        experiment_name = os.environ.get("EXPERIMENT_NAME")
        resource_group = os.environ.get("RESOURCE_GROUP")
        subscription_id = os.environ.get("SUBSCRIPTION_ID")
        # run_id useful to query previous runs
        run_id = "bd184a18-2ac8-4951-8e78-e290bef3b012"
        aml_workspace = Workspace.get(
            name=workspace_name,
            subscription_id=subscription_id,
            resource_group=resource_group
        )
        ws = aml_workspace
        exp = Experiment(ws, experiment_name)
    else:
        ws = run.experiment.workspace
        exp = run.experiment
        run_id = 'amlcompute'

    parser = argparse.ArgumentParser("register")

    parser.add_argument(
        "--run_id",
        type=str,
        help="Training run ID",
    )

    parser.add_argument(
        "--model_name",
        type=str,
        help="Name of the Model",
        default="diabetes_model.pkl",
    )

    parser.add_argument(
        "--step_input",
        type=str,
        help=("input from previous steps")
    )

    args = parser.parse_args()
    if (args.run_id is not None):
        run_id = args.run_id
    if (run_id == 'amlcompute'):
        run_id = run.parent.id
    model_name = args.model_name
    model_path = args.step_input

    observability.log("Getting registration parameters")

    # Load the registration parameters from the parameters file
    with open("diabetes_regression/parameters.json") as f:
        pars = json.load(f)
    try:
        register_args = pars["registration"]
    except KeyError:
        observability.log(
            description="Could not load registration values from file",
            severity=Severity.ERROR)
        register_args = {"tags": []}

    model_tags = {}
    for tag in register_args["tags"]:
        try:
            mtag = run.parent.get_metrics()[tag]
            model_tags[tag] = mtag
        except KeyError:
            observability.log(
                description=f"Could not find {tag} metric on parent run.",
                severity=Severity.ERROR)

    # load the model
    observability.log("Loading model from " + model_path)
    model_file = os.path.join(model_path, model_name)
    model = joblib.load(model_file)
    parent_tags = run.parent.get_tags()
    try:
        build_id = parent_tags["BuildId"]
    except KeyError:
        build_id = None
        observability.log("BuildId tag not found on parent run.",
                          severity=Severity.ERROR)
        observability.log(description=f"Tags present: {parent_tags}",
                          severity=Severity.ERROR)
    try:
        build_uri = parent_tags["BuildUri"]
    except KeyError:
        build_uri = None
        observability.log(description="BuildUri tag not found on parent run.",
                          severity=Severity.ERROR)
        observability.log(description=f"Tags present: {parent_tags}",
                          severity=Severity.ERROR)

    if (model is not None):
        dataset_id = parent_tags["dataset_id"]
        if (build_id is None):
            register_aml_model(
                model_file,
                model_name,
                model_tags,
                exp,
                run_id,
                dataset_id)
        elif (build_uri is None):
            register_aml_model(
                model_file,
                model_name,
                model_tags,
                exp,
                run_id,
                dataset_id,
                build_id)
        else:
            register_aml_model(
                model_file,
                model_name,
                model_tags,
                exp,
                run_id,
                dataset_id,
                build_id,
                build_uri)
    else:
        observability.log("Model not found. Skipping model registration.")
        sys.exit(0)


def model_already_registered(model_name, exp, run_id):
    model_list = AMLModel.list(exp.workspace, name=model_name, run_id=run_id)
    if len(model_list) >= 1:
        e = ("Model name:", model_name, "in workspace",
             exp.workspace, "with run_id ", run_id, "is already registered.")
        observability.log(description=e, severity=Severity.ERROR)
        raise Exception(e)
    else:
        observability.log("Model is not registered for this run.")


def register_aml_model(
        model_path,
        model_name,
        model_tags,
        exp,
        run_id,
        dataset_id,
        build_id: str = 'none',
        build_uri=None
):
    try:
        tagsValue = {"area": "diabetes_regression",
                     "run_id": run_id,
                     "experiment_name": exp.name}
        tagsValue.update(model_tags)
        if (build_id != 'none'):
            model_already_registered(model_name, exp, run_id)
            tagsValue["BuildId"] = build_id
            if (build_uri is not None):
                tagsValue["BuildUri"] = build_uri

        model = AMLModel.register(
            workspace=exp.workspace,
            model_name=model_name,
            model_path=model_path,
            tags=tagsValue,
            datasets=[('training data',
                       Dataset.get_by_id(exp.workspace, dataset_id))])
        os.chdir("..")
        observability.log(
            "Model registered: {} \nModel Description: {} "
            "\nModel Version: {}".format(
                model.name, model.description, model.version
            )
        )
    except Exception:
        traceback.print_exc(limit=None, file=None, chain=True)
        observability.log("Model registration failed",
                          severity=Severity.ERROR)
        raise


if __name__ == '__main__':
    main()
