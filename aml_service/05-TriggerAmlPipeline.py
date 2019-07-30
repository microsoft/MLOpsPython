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

import os, json, requests, datetime, sys
import argparse
from azureml.core.authentication import AzureCliAuthentication
from azureml.core import Workspace, Experiment
from azureml.pipeline.core import Pipeline, PublishedPipeline
from dotenv import load_dotenv

load_dotenv()

# Run a published pipeline
cli_auth = AzureCliAuthentication()
aad_token = cli_auth.get_authentication_header()
pipeline_name = os.environ['TRAINING_PIPELINE_NAME']
experiment_name = os.environ['EXPERIMENT_NAME']
model_name = os.environ['MODEL_NAME']

ws = Workspace.from_config()
experiment = Experiment(ws, experiment_name)
published_pipelines = PublishedPipeline.get_all(ws)
for p in published_pipelines:
    if(p.name == pipeline_name):
        pipeline = p

try:
    if pipeline is not None:
        pipeline_run = experiment.submit(
            pipeline,
            pipeline_parameters={'model_name': model_name}
        )

        run_id = pipeline_run.run_id
        print(run_id)
        print("Pipeline run initiated")
    else:
        raise FileNotFoundError

except FileNotFoundError:
    print('No pipeline with that name found')
