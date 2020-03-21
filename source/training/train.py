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

import argparse
import os
import joblib
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from azureml.core import Run


# Split the dataframe into test and train data
def split_data(df):
    X = df.drop('Y', axis=1).values
    y = df['Y'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0)
    data = {"train": {"X": X_train, "y": y_train},
            "test": {"X": X_test, "y": y_test}}
    return data


# Train the model, return the model
def train_model(data, ridge_args):
    reg_model = Ridge(**ridge_args)
    reg_model.fit(data["train"]["X"], data["train"]["y"])
    return reg_model


# Evaluate the metrics for the model
def get_model_metrics(model, data):
    preds = model.predict(data["test"]["X"])
    mse = mean_squared_error(preds, data["test"]["y"])
    metrics = {"mse": mse}
    return metrics


def main(model_name, source_data, step_output):
    print("Running train.py")

    # load context of current run
    run = Run.get_context()
    print("current run: {}".format(vars(run)))

    if not run.id.lower().startswith('offlinerun'):
        print("parent run: {}".format(vars(run.parent)))

    # Define training parameters
    ridge_args = {"alpha": 0.5}

    # Load the training data as dataframe
    data_file = os.path.abspath(source_data)
    train_df = pd.read_csv(data_file)
    data = split_data(train_df)

    # Train the model
    model = train_model(data, ridge_args)

    # Log the metrics for the model
    print("model metrics:")
    metrics = get_model_metrics(model, data)
    for (k, v) in metrics.items():
        print(f"{k}: {v}")
        # log run metrics for cloud run
        if not run.id.lower().startswith('offlinerun'):
            run.log(k, v)
            run.parent.log(k, v)

    # Pass model file to next step
    os.makedirs(step_output, exist_ok=True)
    model_output_path = os.path.join(step_output, model_name)
    joblib.dump(value=model, filename=model_output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='diabetes training task')
    parser.add_argument(
        "--model_name",
        help="Name of the Model",
        default="diabetes_model")
    parser.add_argument(
        "--source_data",
        help="input raw data",
        default="input")
    parser.add_argument(
        "--step_output",
        help="output for passing data to next step",
        default="output")
    args = parser.parse_args()

    params = vars(args)
    for i in params:
        print('{} => {}'.format(i, params[i]))

    main(**params)
