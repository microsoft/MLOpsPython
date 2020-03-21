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
import os
import sys
import argparse
import joblib
from azureml.core import Run
from util.model_helper import get_latest_model

_MODEL_METRIC_EVAL_KEY = 'mse'


def evaluate(model=None, new_model_mse=0):
    if model:
        production_model_mse = 10000
        if (_MODEL_METRIC_EVAL_KEY in model.tags):
            production_model_mse = float(model.tags[_MODEL_METRIC_EVAL_KEY])

        if (production_model_mse is None or new_model_mse is None):
            print("Unable to find", _MODEL_METRIC_EVAL_KEY,
                  "metrics, exiting evaluation")
            return False

        print("Current Production model mse: {}, New trained model mse: {}"
              .format(production_model_mse, new_model_mse))

        if (new_model_mse < production_model_mse):
            print("New trained model performs better, will be registered")
            return True
        else:
            print("New trained model metric is worse than or equal to "
                  "production model so skipping model registration.")
            return False

    else:
        print("This is the first model, thus it should be registered")
        return True


def main(model_name, step_input, model_upload_folder):
    print("Running eval_register.py")

    # load context of current run
    run = Run.get_context()
    print(vars(run))

    # load the model
    print("Loading model from " + step_input)
    model_file = os.path.join(step_input, model_name)
    model = joblib.load(model_file)

    if not model:
        print("error: failed to load model")
        sys.exit(1)

    # not offline - we can register in AML
    if not run.id.lower().startswith('offlinerun'):
        print('Get current Azure Machine Learning workspace')
        ws = run.experiment.workspace
        print(vars(ws))

        print('Evaluate model with the latest version in workspace')
        latest_model = get_latest_model(ws, model_name)
        model_mse = float(run.parent.get_metrics().get(
            _MODEL_METRIC_EVAL_KEY))

        should_register = evaluate(latest_model, model_mse)
        if should_register:
            print('Register to Azure Machine Learning workspace')

            tags = {"area": "diabetes_regression", "mse": model_mse}
            parent_tags = run.parent.get_tags()

            try:
                build_id = parent_tags["BuildId"]
                tags["build_id"] = build_id
            except KeyError:
                build_id = None
                print("BuildId tag not found on parent run.")
                print("Tags present: {parent_tags}")

            try:
                build_uri = parent_tags["BuildUri"]
                tags["build_uri"] = build_uri
            except KeyError:
                build_uri = None
                print("BuildUri tag not found on parent run.")
                print("Tags present: {parent_tags}")

            # try:
            #     dataset_id = parent_tags["dataset_id"]
            # except KeyError:
            #     dataset_id = None
            #     print("dataset_id tag not found on parent run.")
            #     print("Tags present: {parent_tags}")

            # upload model files to run. TODO: set dataset metadata to model
            run.upload_folder(
                name=model_upload_folder,
                path=os.path.abspath(step_input))

            aml_model = run.register_model(
                model_name=model_name,
                model_path=model_upload_folder,
                tags=tags)

            print(vars(aml_model))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='diabetes model evaluation and registration task')
    parser.add_argument(
        "--model_name",
        help="Name of the Model",
        default="diabetes_model")
    parser.add_argument(
        "--step_input",
        help="Input from previous steps")
    parser.add_argument(
        "--model_upload_folder",
        help="Name of the folder to upload model",
        default="models")
    args = parser.parse_args()

    params = vars(args)
    for i in params:
        print('{} => {}'.format(i, params[i]))

    main(**params)
