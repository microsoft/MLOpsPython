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
from azureml.core import Model, Run, Workspace, Experiment
import argparse
from azureml.core.authentication import ServicePrincipalAuthentication
import traceback

run = Run.get_context()
if (run.id.startswith('OfflineRun')):
    from dotenv import load_dotenv
    # For local development, set values in this section
    load_dotenv()
    workspace_name = os.environ.get("WORKSPACE_NAME")
    experiment_name = os.environ.get("EXPERIMENT_NAME")
    resource_group = os.environ.get("RESOURCE_GROUP")
    subscription_id = os.environ.get("SUBSCRIPTION_ID")
    tenant_id = os.environ.get("TENANT_ID")
    model_name = os.environ.get("MODEL_NAME")
    app_id = os.environ.get('SP_APP_ID')
    app_secret = os.environ.get('SP_APP_SECRET')
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
    ws = aml_workspace
    exp = Experiment(ws, experiment_name)
    run_id = "e78b2c27-5ceb-49d9-8e84-abe7aecf37d5"
else:
    exp = run.experiment
    ws = run.experiment.workspace
    run_id = 'amlcompute'

parser = argparse.ArgumentParser("evaluate")
parser.add_argument(
    "--build_id",
    type=str,
    help="The Build ID of the build triggering this pipeline run",
)
parser.add_argument(
    "--run_id",
    type=str,
    help="Training run ID",
)
parser.add_argument(
    "--model_name",
    type=str,
    help="Name of the Model",
    default="sklearn_regression_model.pkl",
)

args = parser.parse_args()
if (args.build_id is not None):
    build_id = args.build_id
if (args.run_id is not None):
    run_id = args.run_id
if (run_id == 'amlcompute'):
    run_id = run.parent.id
model_name = args.model_name
metric_eval = "mse"
run.tag("BuildId", value=build_id)

# Paramaterize the matrices on which the models should be compared
# Add golden data set on which all the model performance can be evaluated
try:
    model_list = Model.list(ws)
    if (len(model_list) > 0):
        production_model = next(
            filter(
                lambda x: x.created_time == max(
                    model.created_time for model in model_list),
                model_list,
            )
        )
        production_model_run_id = production_model.run_id

        # Get the run history for both production model and
        # newly trained model and compare mse
        production_model_run = Run(exp, run_id=production_model_run_id)
        new_model_run = run.parent
        print("Production model run is", production_model_run)

        production_model_mse = \
            production_model_run.get_metrics().get(metric_eval)
        new_model_mse = new_model_run.get_metrics().get(metric_eval)
        if (production_model_mse is None or new_model_mse is None):
            print("Unable to find", metric_eval, "metrics, "
                  "exiting evaluation")
            run.parent.cancel()
        else:
            print(
                "Current Production model mse: {}, "
                "New trained model mse: {}".format(
                    production_model_mse, new_model_mse
                )
            )

        if (new_model_mse < production_model_mse):
            print("New trained model performs better, "
                  "thus it should be registered")
        else:
            print("New trained model metric is less than or equal to "
                  "production model so skipping model registration.")
            run.parent.cancel()
    else:
        print("This is the first model, "
              "thus it should be registered")
except Exception:
    traceback.print_exc(limit=None, file=None, chain=True)
    print("Something went wrong trying to evaluate. Exiting.")
    raise
