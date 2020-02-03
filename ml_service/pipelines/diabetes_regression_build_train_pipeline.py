from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline
from azureml.core import Workspace, Environment
from azureml.core.runconfig import RunConfiguration
from azureml.core import Dataset, Datastore
from ml_service.util.attach_compute import get_compute
from ml_service.util.env_variables import Env


def main():
    e = Env()
    # Get Azure machine learning workspace
    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group
    )
    print("get_workspace:")
    print(aml_workspace)

    # Get Azure machine learning cluster
    aml_compute = get_compute(
        aml_workspace,
        e.compute_name,
        e.vm_size)
    if aml_compute is not None:
        print("aml_compute:")
        print(aml_compute)

    # Create a reusable run configuration environment
    environment = Environment.load_from_directory(e.sources_directory_train)
    if (e.collection_uri is not None and e.teamproject_name is not None):
        builduri_base = e.collection_uri + e.teamproject_name
        builduri_base = builduri_base + "/_build/results?buildId="
        environment.environment_variables["BUILDURI_BASE"] = builduri_base
    environment.register(aml_workspace)

    run_config = RunConfiguration()
    run_config.environment = environment

    model_name_param = PipelineParameter(
        name="model_name", default_value=e.model_name)
    build_id_param = PipelineParameter(
        name="build_id", default_value=e.build_id)

    dataset_name = ""
    if (e.datastore_name is not None and e.datafile_name is not None):
        dataset_name = e.dataset_name
        datastore = Datastore.get(aml_workspace, e.datastore_name)
        data_path = [(datastore, e.datafile_name)]
        dataset = Dataset.Tabular.from_delimited_files(path=data_path)
        dataset.register(workspace=aml_workspace,
                         name=e.dataset_name,
                         description="dataset with training data",
                         create_new_version=True)

    train_step = PythonScriptStep(
        name="Train Model",
        script_name=e.train_script_path,
        compute_target=aml_compute,
        source_directory=e.sources_directory_train,
        arguments=[
            "--build_id", build_id_param,
            "--model_name", model_name_param,
            "--dataset_name", dataset_name,
        ],
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Step Train created")

    evaluate_step = PythonScriptStep(
        name="Evaluate Model ",
        script_name=e.evaluate_script_path,
        compute_target=aml_compute,
        source_directory=e.sources_directory_train,
        arguments=[
            "--build_id", build_id_param,
            "--model_name", model_name_param,
            "--allow_run_cancel", e.allow_run_cancel,
        ],
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Step Evaluate created")

    register_step = PythonScriptStep(
        name="Register Model ",
        script_name=e.register_script_path,
        compute_target=aml_compute,
        source_directory=e.sources_directory_train,
        arguments=[
            "--build_id", build_id_param,
            "--model_name", model_name_param,
        ],
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Step Register created")
    # Check run_evaluation flag to include or exclude evaluation step.
    if ((e.run_evaluation).lower() == 'true'):
        print("Include evaluation step before register step.")
        evaluate_step.run_after(train_step)
        register_step.run_after(evaluate_step)
        steps = [train_step, evaluate_step, register_step]
    else:
        print("Exclude evaluation step and directly run register step.")
        register_step.run_after(train_step)
        steps = [train_step, register_step]

    train_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    train_pipeline._set_experiment_name
    train_pipeline.validate()
    published_pipeline = train_pipeline.publish(
        name=e.pipeline_name,
        description="Model training/retraining pipeline",
        version=e.build_id
    )
    print(f'Published pipeline: {published_pipeline.name}')
    print(f'for build {published_pipeline.version}')


if __name__ == '__main__':
    main()
