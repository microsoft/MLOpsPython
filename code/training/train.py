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
from azureml.core.run import Run
from azureml.core import Dataset
import os
import argparse
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib


def train_model(run, data, alpha):
    run.log("alpha", alpha)
    run.parent.log("alpha", alpha)
    reg = Ridge(alpha=alpha)
    reg.fit(data["train"]["X"], data["train"]["y"])
    preds = reg.predict(data["test"]["X"])
    run.log("mse", mean_squared_error(
        preds, data["test"]["y"]), description="Mean squared error metric")
    run.parent.log("mse", mean_squared_error(
        preds, data["test"]["y"]), description="Mean squared error metric")
    return reg


def main():
    print("Running train.py")

    parser = argparse.ArgumentParser("train")
    parser.add_argument(
        "--build_id",
        type=str,
        help="The build ID of the build triggering this pipeline run",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        help="Name of the Model",
        default="sklearn_regression_model.pkl",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.5,
        help=("Ridge regression regularization strength hyperparameter; "
              "must be a positive float.")
    )

    parser.add_argument(
        "--dataset_name",
        type=str,
        help=("Dataset with the training data")
    )
    args = parser.parse_args()

    print("Argument [build_id]: %s" % args.build_id)
    print("Argument [model_name]: %s" % args.model_name)
    print("Argument [alpha]: %s" % args.alpha)
    print("Argument [dataset_name]: %s" % args.dataset_name)

    model_name = args.model_name
    build_id = args.build_id
    alpha = args.alpha
    dataset_name = args.dataset_name

    run = Run.get_context()
    ws = run.experiment.workspace

    if (dataset_name):
        dataset = Dataset.get_by_name(workspace=ws, name=dataset_name)
        df = dataset.to_pandas_dataframe()
        X = df.values
        y = df.Y
    else:
        X, y = load_diabetes(return_X_y=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0)
    data = {"train": {"X": X_train, "y": y_train},
            "test": {"X": X_test, "y": y_test}}

    reg = train_model(run, data, alpha)

    joblib.dump(value=reg, filename=model_name)

    # upload model file explicitly into artifacts for parent run
    run.parent.upload_file(name="./outputs/" + model_name,
                           path_or_stream=model_name)
    print("Uploaded the model {} to experiment {}".format(
        model_name, run.experiment.name))
    dirpath = os.getcwd()
    print(dirpath)
    print("Following files are uploaded ")
    print(run.parent.get_file_names())

    run.parent.tag("BuildId", value=build_id)

    # Add properties to identify this specific training run
    run.tag("BuildId", value=build_id)
    run.tag("run_type", value="train")
    builduri_base = os.environ.get("BUILDURI_BASE")
    if (builduri_base is not None):
        build_uri = builduri_base + build_id
        run.tag("BuildUri", value=build_uri)
        run.parent.tag("BuildUri", value=build_uri)
    print(f"tags now present for run: {run.tags}")

    run.complete()


if __name__ == '__main__':
    main()
