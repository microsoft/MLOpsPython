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
import json
from azureml.core.model import Model
from azureml.core import Run
import argparse


# Get workspace
# ws = Workspace.from_config()
run = Run.get_context()
exp = run.experiment
ws = run.experiment.workspace


parser = argparse.ArgumentParser("evaluate")
parser.add_argument(
    "--config_suffix", type=str, help="Datetime suffix for json config files"
)
parser.add_argument(
    "--json_config",
    type=str,
    help="Directory to write all the intermediate json configs",
)
args = parser.parse_args()

print("Argument 1: %s" % args.config_suffix)
print("Argument 2: %s" % args.json_config)

if not (args.json_config is None):
    os.makedirs(args.json_config, exist_ok=True)
    print("%s created" % args.json_config)
# Paramaterize the matrics on which the models should be compared
# Add golden data set on which all the model performance can be evaluated

# Get the latest run_id
# with open("aml_config/run_id.json") as f:
#     config = json.load(f)

train_run_id_json = "run_id_{}.json".format(args.config_suffix)
train_output_path = os.path.join(args.json_config, train_run_id_json)
with open(train_output_path) as f:
    config = json.load(f)


new_model_run_id = config["run_id"]  # args.train_run_id
experiment_name = config["experiment_name"]
# exp = Experiment(workspace=ws, name=experiment_name)


try:
    # Get most recently registered model, we assume that
    # is the model in production.
    # Download this model and compare it with the recently
    # trained model by running test with same data set.
    model_list = Model.list(ws)
    production_model = next(
        filter(
            lambda x: x.created_time == max(
                model.created_time for model in model_list),
            model_list,
        )
    )
    production_model_run_id = production_model.tags.get("run_id")
    run_list = exp.get_runs()

    # Get the run history for both production model and
    # newly trained model and compare mse
    production_model_run = Run(exp, run_id=production_model_run_id)
    new_model_run = Run(exp, run_id=new_model_run_id)

    production_model_mse = production_model_run.get_metrics().get("mse")
    new_model_mse = new_model_run.get_metrics().get("mse")
    print(
        "Current Production model mse: {}, New trained model mse: {}".format(
            production_model_mse, new_model_mse
        )
    )

    promote_new_model = False
    if new_model_mse < production_model_mse:
        promote_new_model = True
        print("New trained model performs better, thus it will be registered")
except Exception:
    promote_new_model = True
    print("This is the first model to be trained, \
          thus nothing to evaluate for now")

run_id = {}
run_id["run_id"] = ""
# Writing the run id to /aml_config/run_id.json
if promote_new_model:
    run_id["run_id"] = new_model_run_id
    # register new model
    # new_model_run.register_model(model_name='',model_path='outputs/sklearn_regression_model.pkl')

run_id["experiment_name"] = experiment_name
filename = "run_id_{}.json".format(args.config_suffix)
output_path = os.path.join(args.json_config, filename)
with open(output_path, "w") as outfile:
    json.dump(run_id, outfile)
