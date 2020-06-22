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

from azure.storage.blob import ContainerClient
from ml_service.util.env_variables import Env
from azureml.core import Experiment, Workspace
from azureml.pipeline.core import PublishedPipeline
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline_id", type=str, default=None)
    return parser.parse_args()


def get_pipeline(pipeline_id, ws: Workspace, env: Env):
    if pipeline_id is not None:
        scoringpipeline = PublishedPipeline.get(ws, pipeline_id)
    else:
        pipelines = PublishedPipeline.list(ws)
        scoringpipelinelist = [
            pl for pl in pipelines if pl.name == env.scoring_pipeline_name
        ]  # noqa E501

        if scoringpipelinelist.count == 0:
            raise Exception(
                "No pipeline found matching name:{}".format(env.scoring_pipeline_name)  # NOQA: E501
            )
        else:
            # latest published
            scoringpipeline = scoringpipelinelist[0]

    return scoringpipeline


def copy_output(step_id: str, env: Env):
    accounturl = "https://{}.blob.core.windows.net".format(
        env.scoring_datastore_storage_name
    )

    srcblobname = "azureml/{}/{}_out/parallel_run_step.txt".format(
        step_id, env.scoring_datastore_storage_name
    )

    srcbloburl = "{}/{}/{}".format(
        accounturl, env.scoring_datastore_output_container, srcblobname
    )

    containerclient = ContainerClient(
        accounturl,
        env.scoring_datastore_output_container,
        env.scoring_datastore_access_key,
    )
    srcblobproperties = containerclient.get_blob_client(
        srcblobname
    ).get_blob_properties()  # noqa E501

    destfolder = srcblobproperties.last_modified.date().isoformat()
    filetime = (
        srcblobproperties.last_modified.time()
        .isoformat("milliseconds")
        .replace(":", "_")
        .replace(".", "_")
    )  # noqa E501
    destfilenameparts = env.scoring_datastore_output_filename.split(".")
    destblobname = "{}/{}_{}.{}".format(
        destfolder, destfilenameparts[0], filetime, destfilenameparts[1]
    )

    destblobclient = containerclient.get_blob_client(destblobname)
    destblobclient.start_copy_from_url(srcbloburl)


def run_batchscore_pipeline():
    try:
        env = Env()

        args = parse_args()

        aml_workspace = Workspace.get(
            name=env.workspace_name,
            subscription_id=env.subscription_id,
            resource_group=env.resource_group,
        )

        scoringpipeline = get_pipeline(args.pipeline_id, aml_workspace, env)

        experiment = Experiment(workspace=aml_workspace, name=env.experiment_name)  # NOQA: E501

        run = experiment.submit(
            scoringpipeline,
            pipeline_parameters={
                "model_name": env.model_name,
                "model_tag_name": " ",
                "model_tag_value": " ",
            },
        )

        run.wait_for_completion(show_output=True)

        if run.get_status() == "Finished":
            copy_output(list(run.get_steps())[0].id, env)

    except Exception as ex:
        print("Error: {}".format(ex))


if __name__ == "__main__":
    run_batchscore_pipeline()
