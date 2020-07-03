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
from azureml.pipeline.steps import ParallelRunConfig, ParallelRunStep
from ml_service.util.manage_environment import get_environment
from ml_service.pipelines.load_sample_data import create_sample_data_csv
from ml_service.util.env_variables import Env
from ml_service.util.attach_compute import get_compute
from azureml.core import (
    Workspace,
    Dataset,
    Datastore,
    RunConfiguration,
)
from azureml.pipeline.core import Pipeline, PipelineData, PipelineParameter
from azureml.core.compute import ComputeTarget
from azureml.data.datapath import DataPath
from azureml.pipeline.steps import PythonScriptStep
from typing import Tuple

from utils.logger.logger_interface import Severity
from utils.logger.observability import Observability

observability = Observability()


def get_or_create_datastore(
        datastorename: str, ws: Workspace, env: Env, input: bool = True
) -> Datastore:
    """
    Obtains a datastore with matching name. Creates it if none exists.

    :param datastorename: Name of the datastore
    :param ws: Current AML Workspace
    :param env: Environment variables
    :param input: Datastore points to the input container if
    this is True(default) or the output storage container otherwise

    :returns: Datastore

    :raises: ValueError
    """
    if datastorename is None:
        error = "Datastore name is required."
        observability.log(description=error, severity=Severity.ERROR)
        raise ValueError(error)

    containername = (
        env.scoring_datastore_input_container
        if input
        else env.scoring_datastore_output_container
    )

    if datastorename in ws.datastores:

        datastore = ws.datastores[datastorename]

    # the datastore is not registered but we have all details to register it
    elif (
            env.scoring_datastore_access_key is not None
            and containername is not None  # NOQA: E501
    ):  # NOQA:E501

        datastore = Datastore.register_azure_blob_container(
            workspace=ws,
            datastore_name=datastorename,
            account_name=env.scoring_datastore_storage_name,
            account_key=env.scoring_datastore_access_key,
            container_name=containername,
        )
    else:
        error = "No existing datastore named {} nor was enough " \
                "information supplied to create one.".format(datastorename)
        observability.log(description=error, severity=Severity.ERROR)
        raise ValueError(error)

    return datastore


def get_input_dataset(ws: Workspace, ds: Datastore, env: Env) -> Dataset:
    """
    Gets an input dataset wrapped around an input data file. The input
    data file is assumed to exist in the supplied datastore.


    :param ws: AML Workspace
    :param ds: Datastore containing the data file
    :param env: Environment variables

    :returns: Input Dataset
    """

    scoringinputds = Dataset.Tabular.from_delimited_files(
        path=DataPath(ds, env.scoring_datastore_input_filename)
    )

    scoringinputds = scoringinputds.register(
        ws,
        name=env.scoring_dataset_name,
        tags={"purpose": "scoring input", "format": "csv"},
        create_new_version=True,
    ).as_named_input(env.scoring_dataset_name)

    return scoringinputds


def get_fallback_input_dataset(ws: Workspace, env: Env) -> Dataset:
    """
    Called when an input datastore does not exist or no input data file exists
    at that location. Create a sample dataset using the diabetes dataset from
    scikit-learn. Useful when debugging this code in the absence of the input
    data location Azure blob.


    :param ws: AML Workspace
    :param env: Environment Variables

    :returns: Fallback input dataset

    :raises: FileNotFoundError
    """
    # This call creates an example CSV from sklearn sample data. If you
    # have already bootstrapped your project, you can comment this line
    # out and use your own CSV.
    create_sample_data_csv(
        file_name=env.scoring_datastore_input_filename, for_scoring=True
    )

    if not os.path.exists(env.scoring_datastore_input_filename):
        error_message = (
                "Could not find CSV dataset for scoring at {}. "
                + "No alternate data store location was provided either."
                .format(env.scoring_datastore_input_filename)
        )
        observability.log(description=error_message, severity=Severity.ERROR)
        raise FileNotFoundError(error_message)

    # upload the input data to the workspace default datastore
    default_datastore = ws.get_default_datastore()
    scoreinputdataref = default_datastore.upload_files(
        [env.scoring_datastore_input_filename],
        target_path="scoringinput",
        overwrite=False,
    )

    scoringinputds = (
        Dataset.Tabular.from_delimited_files(scoreinputdataref).register(
            ws,
            env.scoring_dataset_name,
            create_new_version=True).as_named_input(
            env.scoring_dataset_name)
    )

    return scoringinputds


def get_output_location(
        ws: Workspace, env: Env, outputdatastore: Datastore = None
) -> PipelineData:
    """
    Returns a Datastore wrapped as a PipelineData instance suitable
    for passing into a pipeline step. Represents the location where
    the scoring output should be written. Uses the default workspace
    blob store if no output datastore is supplied.


    :param ws: AML Workspace
    :param env: Environment Variables
    :param outputdatastore: AML Datastore, optional, default is None

    :returns: PipelineData wrapping the output datastore
    """

    if outputdatastore is None:
        output_loc = PipelineData(
            name="defaultoutput", datastore=ws.get_default_datastore()
        )
    else:
        output_loc = PipelineData(
            name=outputdatastore.name, datastore=outputdatastore
        )  # NOQA: E501

    return output_loc


def get_inputds_outputloc(
        ws: Workspace, env: Env
) -> Tuple[Dataset, PipelineData]:  # NOQA: E501
    """
    Prepare the input and output for the scoring step. Input is a tabular
    dataset wrapped around the scoring data. Output is PipelineData
    representing a location to write the scores down.

    :param ws: AML Workspace
    :param env: Environment Variables

    :returns: Input dataset and output location
    """

    if env.scoring_datastore_storage_name is None:
        # fall back to default
        scoringinputds = get_fallback_input_dataset(ws, env)
        output_loc = get_output_location(ws, env)
    else:
        inputdatastore = get_or_create_datastore(
            "{}_in".format(env.scoring_datastore_storage_name), ws, env
        )
        outputdatastore = get_or_create_datastore(
            "{}_out".format(env.scoring_datastore_storage_name),
            ws,
            env,
            input=False,  # NOQA: E501
        )
        scoringinputds = get_input_dataset(ws, inputdatastore, env)
        output_loc = get_output_location(ws, env, outputdatastore)

    return (scoringinputds, output_loc)


def get_run_configs(
        ws: Workspace, computetarget: ComputeTarget, env: Env
) -> Tuple[ParallelRunConfig, RunConfiguration]:
    """
    Creates the necessary run configurations required by the
    pipeline to enable parallelized scoring.

    :param ws: AML Workspace
    :param computetarget: AML Compute target
    :param env: Environment Variables

    :returns: Tuple[Scoring Run configuration, Score copy run configuration]
    """

    # get a conda environment for scoring
    environment = get_environment(
        ws,
        env.aml_env_name_scoring,
        conda_dependencies_file=env.aml_env_score_conda_dep_file,
        enable_docker=True,
        use_gpu=env.use_gpu_for_scoring,
        create_new=env.rebuild_env_scoring,
    )

    score_run_config = ParallelRunConfig(
        entry_script=env.batchscore_script_path,
        source_directory=env.sources_directory_train,
        error_threshold=10,
        output_action="append_row",
        compute_target=computetarget,
        node_count=env.max_nodes_scoring,
        environment=environment,
        run_invocation_timeout=300,
    )

    copy_run_config = RunConfiguration()
    copy_run_config.environment = get_environment(
        ws,
        env.aml_env_name_score_copy,
        conda_dependencies_file=env.aml_env_scorecopy_conda_dep_file,
        enable_docker=True,
        use_gpu=env.use_gpu_for_scoring,
        create_new=env.rebuild_env_scoring,
    )
    return (score_run_config, copy_run_config)


def get_scoring_pipeline(
        scoring_dataset: Dataset,
        output_loc: PipelineData,
        score_run_config: ParallelRunConfig,
        copy_run_config: RunConfiguration,
        computetarget: ComputeTarget,
        ws: Workspace,
        env: Env,
) -> Pipeline:
    """
    Creates the scoring pipeline.

    :param scoring_dataset: Data to score
    :param output_loc: Location to save the scoring results
    :param score_run_config: Parallel Run configuration to support
    parallelized scoring
    :param copy_run_config: Script Run configuration to support
    score copying
    :param computetarget: AML Compute target
    :param ws: AML Workspace
    :param env: Environment Variables

    :returns: Scoring pipeline instance
    """
    # To help filter the model make the model name, model version and a
    # tag/value pair bindable parameters so that they can be passed to
    # the pipeline when invoked either over REST or via the AML SDK.
    model_name_param = PipelineParameter(
        "model_name", default_value=env.model_name
    )  # NOQA: E501
    model_version_param = PipelineParameter(
        "model_version", default_value=env.model_version
    )  # NOQA: E501
    model_tag_name_param = PipelineParameter(
        "model_tag_name", default_value=" "
    )  # NOQA: E501
    model_tag_value_param = PipelineParameter(
        "model_tag_value", default_value=" "
    )  # NOQA: E501

    scoring_step = ParallelRunStep(
        name="scoringstep",
        inputs=[scoring_dataset],
        output=output_loc,
        arguments=[
            "--model_name",
            model_name_param,
            "--model_version",
            model_version_param,
            "--model_tag_name",
            model_tag_name_param,
            "--model_tag_value",
            model_tag_value_param,
        ],
        parallel_run_config=score_run_config,
        allow_reuse=False,
    )

    copying_step = PythonScriptStep(
        name="scorecopystep",
        script_name=env.batchscore_copy_script_path,
        source_directory=env.sources_directory_train,
        arguments=[
            "--output_path",
            output_loc,
            "--scoring_output_filename",
            env.scoring_datastore_output_filename
            if env.scoring_datastore_output_filename is not None
            else "",
            "--scoring_datastore",
            env.scoring_datastore_storage_name
            if env.scoring_datastore_storage_name is not None
            else "",
            "--score_container",
            env.scoring_datastore_output_container
            if env.scoring_datastore_output_container is not None
            else "",
            "--scoring_datastore_key",
            env.scoring_datastore_access_key
            if env.scoring_datastore_access_key is not None
            else "",
        ],
        inputs=[output_loc],
        allow_reuse=False,
        compute_target=computetarget,
        runconfig=copy_run_config,
    )
    return Pipeline(workspace=ws, steps=[scoring_step, copying_step])


def build_batchscore_pipeline():
    """
    Main method that builds and publishes a scoring pipeline.
    """

    try:
        env = Env()

        # Get Azure machine learning workspace
        aml_workspace = Workspace.get(
            name=env.workspace_name,
            subscription_id=env.subscription_id,
            resource_group=env.resource_group,
        )

        # Get Azure machine learning cluster
        aml_compute_score = get_compute(
            aml_workspace,
            env.compute_name_scoring,
            env.vm_size_scoring,
            for_batch_scoring=True,
        )

        input_dataset, output_location = get_inputds_outputloc(
            aml_workspace, env
        )  # NOQA: E501

        scoring_runconfig, score_copy_runconfig = get_run_configs(
            aml_workspace, aml_compute_score, env
        )

        scoring_pipeline = get_scoring_pipeline(
            input_dataset,
            output_location,
            scoring_runconfig,
            score_copy_runconfig,
            aml_compute_score,
            aml_workspace,
            env,
        )

        published_pipeline = scoring_pipeline.publish(
            name=env.scoring_pipeline_name,
            description="Diabetes Batch Scoring Pipeline",
        )
        pipeline_id_string = "##vso[task.setvariable variable=pipeline_id;isOutput=true]{}".format(  # NOQA: E501
            published_pipeline.id
        )
        observability.log(pipeline_id_string)
    except Exception as e:
        observability.log(description=e, severity=Severity.ERROR)
        exit(1)


if __name__ == "__main__":
    build_batchscore_pipeline()
