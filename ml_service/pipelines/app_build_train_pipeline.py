from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.core import Workspace, Dataset, Datastore
from azureml.core.runconfig import RunConfiguration
from ml_service.util.attach_compute import get_compute
from ml_service.util.env_variables import Env
from ml_service.util.manage_environment import get_environment
from azureml.train.automl import AutoMLConfig
import os
import azureml.core

def main():
    e = Env()
    
    from azureml.core.authentication import InteractiveLoginAuthentication

    myten=os.environ.get("AZURE_TENANT_ID")
    interactive_auth = InteractiveLoginAuthentication(tenant_id=os.environ.get("AZURE_TENANT_ID"))
    subscription=os.environ.get("CSUBSCRIPTION")
    workspace_name=e.workspace_name
    resource_group=e.resource_group

    aml_workspace = Workspace.get(
        name = workspace_name,
        subscription_id = subscription,
        resource_group=resource_group,
        auth=interactive_auth
    )

    from ml_service.util.attach_compute import get_compute

    # Get Azure machine learning cluster
    # If not present then get_compute will create a compute based on environment variables

    aml_compute = get_compute(
        aml_workspace,
        e.compute_name,
        e.vm_size)
    if aml_compute is not None:
        print("aml_compute:")
        print(aml_compute)

    print("SDK version: ", azureml.core.VERSION)

    ## Variable names that can be passed in as parameter values
    from azureml.pipeline.core.graph import PipelineParameter
    from azureml.core import Datastore

    model_name_param = PipelineParameter(
        name="model_name", default_value=e.model_name)
    dataset_version_param = PipelineParameter(
        name="dataset_version", default_value=e.dataset_version)
    data_file_path_param = PipelineParameter(
        name="data_file_path", default_value="none")
    caller_run_id_param = PipelineParameter(
        name="caller_run_id", default_value="none")
    #model_path = PipelineParameter(
    #    name="model_path", default_value=e.model_path)    

    if (e.datastore_name):
        datastore_name = e.datastore_name
    else:
        datastore_name = aml_workspace.get_default_datastore().name

    # Get the datastore whether it is the default or named store
    datastore = Datastore.get(aml_workspace, datastore_name)
    dataset_name = e.dataset_name

    # Create a reusable Azure ML environment
    from ml_service.util.manage_environment import get_environment
    from azureml.core import Environment

    # RUN Configuration
    ## Must have this process to work with AzureML-SDK 1.0.85
    from azureml.core.runconfig import RunConfiguration, DEFAULT_CPU_IMAGE
    from azureml.core.conda_dependencies import CondaDependencies

    try:
        app_env=Environment(name="smartschedule_env")
        app_env.register(workspace=aml_workspace)
    except:
        print("Environment not found")
    
    # Create a new runconfig object
    aml_run_config = RunConfiguration()

    aml_run_config.environment.environment_variables["DATASTORE_NAME"] = e.datastore_name  # NOQA: E501

    # Use the aml_compute you created above. 
    aml_run_config.target = aml_compute

    # Enable Docker
    aml_run_config.environment.docker.enabled = True

    # Set Docker base image to the default CPU-based image
    aml_run_config.environment.docker.base_image = DEFAULT_CPU_IMAGE
    #aml_run_config.environment.docker.base_image = "mcr.microsoft.com/azureml/base:0.2.1"

    # Use conda_dependencies.yml to create a conda environment in the Docker image for execution
    aml_run_config.environment.python.user_managed_dependencies = False

    app_conda_deps=CondaDependencies.create(
        conda_packages=['pandas','scikit-learn', 'libgcc','pyodbc', 'sqlalchemy', 'py-xgboost==0.90'], 
        pip_packages=['azureml-sdk[automl,explain,contrib,interpret]==1.4.0', 'xgboost==0.90', 'azureml-dataprep==1.4.6', 'pyarrow', 'azureml-defaults==1.4.0', 'azureml-train-automl-runtime==1.4.0'], pin_sdk_version=False)

    # Specify CondaDependencies obj, add necessary packages
    aml_run_config.environment.python.conda_dependencies = app_conda_deps

    print ("Run configuration created.")
    from azure.common.credentials import ServicePrincipalCredentials
    #from azure.keyvault import KeyVaultClient, KeyVaultAuthentication

    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    import pandas as pd
    #import sqlalchemy as sql
    import pyodbc

    def get_data(sql_string, columns):
        credentials = None
        credential = DefaultAzureCredential()

        secret_client = SecretClient("https://smrtschd-aml-kv.vault.azure.net", credential=credential)    
        secret = secret_client.get_secret("database-connection")

        #client = KeyVaultClient(KeyVaultAuthentication(auth_callback))
        #secret_bundle = client.get_secret("https://smrtschd-aml-kv.vault.azure.net", "database-connection", "")

        server = 'starlims-sql.database.windows.net'
        database = 'QM12_DATA_AUTOMATION'
        username = 'starlims-admin'
        password = secret.value
        driver= '{ODBC Driver 17 for SQL Server}'
        conn = pyodbc.connect('Driver='+driver+';'+
                            'Server='+server+';'+
                            'Database='+database+';'+
                            'PORT=1433;'+
                            'UID='+username+';'+
                            'PWD='+password+'; MARS_Connection=Yes'
        )

        try:
            SQL_Query = pd.read_sql_query(sql_string, conn)

            df = pd.DataFrame(SQL_Query, columns=columns)
            return df
        except Exception as e:
            print(e)
            raise

    sql_str = "SELECT " \
            "  Dept " \
            ", Method " \
            ", Servgrp " \
            ", Runno " \
            ", TestNo " \
            ", Testcode " \
            ", Total_Duration_Min " \
            ", Total_Duration_Hr " \
            ", Usrnam " \
            ", Eqid " \
            ", Eqtype " \
        "FROM dbo.Draft " \
        "order by TESTCODE, RUNNO, dept, method;"

    columns = ["Dept", "Method", "Servgrp", "Runno", "TestNo", "Testcode", "Total_Duration_Min", "Total_Duration_Hr", "Usrnam", "Eqid","Eqtype"]

    from azureml.core import Dataset
    from sklearn.model_selection import train_test_split

    if (e.train_dataset_name not in aml_workspace.datasets):

        
        df = get_data(sql_str, columns)

        train_df, test_df=train_test_split(df, test_size=0.2)

        MY_DIR = "data"

        CHECK_FOLDER = os.path.isdir(MY_DIR)

        if not CHECK_FOLDER:
            os.makedirs(MY_DIR)
        else:
            print("Folder ", MY_DIR, " is already created")

        #files = ["data/analyst_tests.csv"]
        files = ["data/train_data.csv","data/test_data.csv"]

        def_file_store = Datastore(aml_workspace, "workspacefilestore")

        dtfrm = df.to_csv(files[0], header=True, index=False)

        train_dataframe=train_df.to_csv(files[0], header=True, index=False)
        test_dataframe=test_df.to_csv(files[1], header=True, index=False)
        datastore.upload_files(
            files=files,
            target_path='data/',
            overwrite=True
        )

        from azureml.data.data_reference import DataReference

        blob_input_data_test=DataReference(
            datastore=datastore,
            data_reference_name="smartschedulertest",
            path_on_datastore="data/test_data.csv"
        )
        test_data=Dataset.Tabular.from_delimited_files(blob_input_data_test)
        test_data.register(aml_workspace, e.test_dataset_name, create_new_version=True)

        blob_input_data_train=DataReference(
            datastore=datastore,
            data_reference_name="smartschedulertrain",
            path_on_datastore="data/train_data.csv"
        )
        train_data=Dataset.Tabular.from_delimited_files(blob_input_data_train)
        train_data.register(aml_workspace, e.train_dataset_name, create_new_version=True)

    else:
        from azureml.data.data_reference import DataReference
        print("getting from the datastore instead of uploading")

        train_data=Dataset.get_by_name(aml_workspace, name=e.train_dataset_name)
        test_data=Dataset.get_by_name(aml_workspace, name=e.test_dataset_name)

    # check the training dataset to make sure it has at least 50 records.
    tdf=train_data.to_pandas_dataframe().head(5)

    print(tdf.shape)
    print(tdf)

    # display the first five rows of the data
    # create a variable that can be used for other purposes
    df=train_data.to_pandas_dataframe().head()

    label_column="Total_Duration_Min"

    import random
    import string

    def randomString(stringLength=15):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    from azureml.core import Experiment

    experiment = Experiment(aml_workspace, "SmartScheduler_Pipeline")


    import logging

    aml_name = 'smart_scheduler_' + randomString(5)
    print(aml_name)

    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.ticker import StrMethodFormatter

    print(df.head(5))
    print(df.shape)
    print(df.dtypes)

    #df.hist(column='Dept')
    list(df.columns.values)

    # Remove Features that are not necessary.
    #df.hist(column="Servgrp", bins=4)
    train_data=train_data.drop_columns(["Runno","TestNo","Total_Duration_Hr"])
    test_data=test_data.drop_columns(["Runno","TestNo","Total_Duration_Hr"])

    print(train_data.to_pandas_dataframe())
    print(test_data.to_pandas_dataframe())

    from azureml.automl.core.featurization import FeaturizationConfig

    # some of the columns could be change to one hot encoding especially if the categorical column
    featurization_config=FeaturizationConfig()
    featurization_config.blocked_transformers=['LabelEncoder']
    featurization_config.add_column_purpose('Dept', 'CategoricalHash')
    featurization_config.add_transformer_params('HashOneHotEncoder',['Method'], {"number_of_bits":3})
    featurization_config.add_column_purpose('Servgrp', 'CategoricalHash')
    featurization_config.add_column_purpose('Testcode', 'Numeric')
    featurization_config.add_column_purpose('Usrnam', 'CategoricalHash')
    featurization_config.add_column_purpose('Eqid', 'CategoricalHash')
    featurization_config.add_column_purpose('Eqtype', 'CategoricalHash')

    from azureml.pipeline.core import Pipeline, PipelineData
    from azureml.pipeline.steps import PythonScriptStep

    #train_model_folder = './scripts/trainmodel'

    automl_settings = {
        "iteration_timeout_minutes": 5,
        "iterations": 5,
        "enable_early_stopping": True,
        "primary_metric": 'spearman_correlation',
        "verbosity": logging.INFO,
        "n_cross_validation":5
    }

    automl_config = AutoMLConfig(task="regression",
                    debug_log='automated_ml_errors.log',
                    #path = train_model_folder,
                    training_data=train_data,
                    featurization=featurization_config,
                    blacklist_models=['XGBoostRegressor'],
                    label_column_name=label_column,
                    compute_target=aml_compute,
                    **automl_settings)

    from azureml.pipeline.steps import AutoMLStep
    from azureml.pipeline.core import TrainingOutput

    metrics_output_name = 'metrics_output'
    best_model_output_name='best_model_output'

    metrics_data = PipelineData(name = 'metrics_data',
                    datastore = datastore,
                    pipeline_output_name=metrics_output_name,
                    training_output=TrainingOutput(type='Metrics'))

    model_data = PipelineData(name='model_data',
                datastore=datastore,
                pipeline_output_name=best_model_output_name,
                training_output=TrainingOutput(type='Model'))

    trainWithAutomlStep = AutoMLStep(
                        name=aml_name,
                        automl_config=automl_config,
                        passthru_automl_config=False,
                        outputs=[metrics_data, model_data],
                        allow_reuse=True
    )

    evaluate_step = PythonScriptStep(
        name="Evaluate Model",
        script_name='./evaluate/evaluate_model.py',
        #  e.evaluate_script_path,
        compute_target=aml_compute,
        source_directory='../app',
        arguments=[
            "--model_name", model_name_param,
            "--allow_run_cancel", e.allow_run_cancel
        ]
    )

    register_step = PythonScriptStep(
        name="Register Model ",
        script_name='register/register_model2.py', #e.register_script_path,
        compute_target=aml_compute,
        source_directory='../app',
        inputs=[model_data],
        arguments=[
            "--model_name", model_name_param,
            "--model_path", model_data,
            "--ds_name", e.train_dataset_name
        ],
        runconfig=aml_run_config,
        allow_reuse=False
    )

    if ((e.run_evaluation).lower() == 'true'):
        print("Include evaluation step before register step.")
        evaluate_step.run_after(trainWithAutomlStep)
        register_step.run_after(evaluate_step)
        pipeline_steps = [ trainWithAutomlStep, evaluate_step, register_step ]
    else:
        print("Exclude the evaluation step and run register step")
        register_step.run_after(trainWithAutomlStep)
        pipeline_steps = [ trainWithAutomlStep, register_step ]

    print( "this is the value for execute pipeline: {}".format(e.execute_pipeline))

    if( (e.execute_pipeline).lower() =='true' ):
        # Execute the pipe normally during testing and debugging
        print("Pipeline submitted for execution.")
        pipeline = Pipeline(workspace = aml_workspace, steps=pipeline_steps)
        pipeline_run = experiment.submit(pipeline)
        pipeline_run.wait_for_completion()
        print("Pipeline is built.")
    else:
        # Generates pipeline that will be called in ML Ops
        train_pipeline = Pipeline(workspace=aml_workspace, steps=pipeline_steps)
        train_pipeline._set_experiment_name
        train_pipeline.validate()
        published_pipeline = train_pipeline.publish(
            name=e.pipeline_name,
            description="Model training/retraining pipeline",
            version=e.build_id
        )
        print(f'Published pipeline: {published_pipeline.name}')
        print(f'for build {published_pipeline.version}')

    # How to get the conda environment dependencies...
    #pipeline_run.download_file('conda_env_v_1_0_0.yml')


if __name__=="__main__":
    main()
