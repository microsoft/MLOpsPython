# Bring your own code with the MLOpsPython repository template

This document provides steps to follow when using this repository as a template to train models and deploy the models with real-time inference in Azure ML with your own scripts and data.

1. Follow the MLOpsPython [Getting Started](getting_started.md) guide
1. Bootstrap the project
1. Configure training data
1. [If necessary] Convert your ML experimental code into production ready code
1. Replace the training code
1. [Optional] Update the evaluation code
1. Customize the build agent environment
1. [If appropriate] Replace the score code
1. [If appropriate] Configure batch scoring data

## Follow the Getting Started guide

Follow the [Getting Started](getting_started.md) guide to set up the infrastructure and pipelines to execute MLOpsPython.

Take a look at the [Repo Details](code_description.md) document for a description of the structure of this repository.

## Bootstrap the project

Bootstrapping will prepare the directory structure to be used for your project name which includes:

* renaming files and folders from the base project name `diabetes_regression` to your project name
* fixing imports and absolute path based on your project name
* deleting and cleaning up some directories

**Note:** Since the bootstrap script will rename the `diabetes_regression` folder to the project name of your choice, we'll refer to your project as `[project name]` when paths are involved.

To bootstrap from the existing MLOpsPython repository:

1. Ensure Python 3 is installed locally
1. From a local copy of the code, run the `bootstrap.py` script in the `bootstrap` folder
`python bootstrap.py -d [dirpath] -n [projectname]`
    * `[dirpath]` is the absolute path to the root of the directory where MLOpsPython is cloned
    * `[projectname]` is the name of your ML project

# Configure Custom Training

## Configure training data

The training ML pipeline uses a [sample diabetes dataset](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_diabetes.html) as training data.

**Important** Convert the template to use your own Azure ML Dataset for model training via these steps:

1. [Create a Dataset](https://docs.microsoft.com/azure/machine-learning/how-to-create-register-datasets) in your Azure ML workspace
1. Update the `DATASET_NAME` and `DATASTORE_NAME` variables in `.pipelines/[project name]-variables-template.yml`

## Convert your ML experimental code into production ready code

The MLOpsPython template creates an Azure Machine Learning (ML) pipeline that invokes a set of [Azure ML pipeline steps](https://docs.microsoft.com/python/api/azureml-pipeline-steps/azureml.pipeline.steps) (see `ml_service/pipelines/[project name]_build_train_pipeline.py`). If your experiment is currently in a Jupyter notebook, it will need to be refactored into scripts that can be run independently and dropped into the template which the existing Azure ML pipeline steps utilize.

1. Refactor your experiment code into scripts
1. [Recommended] Prepare unit tests

Examples of all these scripts are provided in this repository.
See the [Convert ML experimental code to production code tutorial](https://docs.microsoft.com/azure/machine-learning/tutorial-convert-ml-experiment-to-production) for a step by step guide and additional details.

## Replace training code

The template contains three scripts in the `[project name]/training` folder. Update these scripts for your experiment code.

* `train.py` contains the platform-agnostic logic required to do basic data preparation and train the model. This script can be invoked against a static data file for local development.
* `train_aml.py` is the entry script for the ML pipeline step. It invokes the functions in `train.py` in an Azure ML context and adds logging. `train_aml.py` loads parameters for training from `[project name]/parameters.json` and passes them to the training function in `train.py`. If your experiment code can be refactored to match the function signatures in `train.py`, this file shouldn't need many changes.
* `test_train.py` contains tests that guard against functional regressions in `train.py`. Remove this file if you have no tests for your own code.

Add any dependencies required by training to `[project name]/conda_dependencies.yml]`. This file will be used to generate the environment that the pipeline steps will run in.

## Update evaluation code

The MLOpsPython template uses the evaluate_model script to compare the performance of the newly trained model and the current production model based on Mean Squared Error. If the performance of the newly trained model is better than the current production model, then the pipelines continue. Otherwise, the pipelines are canceled.

To keep the evaluation step, replace all instances of `mse` in `[project name]/evaluate/evaluate_model.py` with the metric that you want.

To disable the evaluation step, either:

* set the DevOps pipeline variable `RUN_EVALUATION` to `false`
* uncomment `RUN_EVALUATION` in `.pipelines/[project name]-variables-template.yml` and set the value to `false`

## Customize the build agent environment

The DevOps pipeline definitions in the MLOpsPython template run several steps in a Docker container that contains the dependencies required to work through the Getting Started guide. These dependencies may change over time and may not suit your project's needs. To manage your own dependencies, there are a few options:

* Add a pipeline step to install dependencies required by unit tests to `.pipelines/code-quality-template.yml`. Recommended if you only have a small number of test dependencies.
* Create a new Docker image containing your dependencies. See [docs/custom_container.md](custom_container.md). Recommended if you have a larger number of dependencies, or if the overhead of installing additional dependencies on each run is too high.
* Remove the container references from the pipeline definition files and run the pipelines on self hosted agents with dependencies pre-installed.

# Configure Custom Scoring

## Replace score code

For the model to provide real-time inference capabilities, the score code needs to be replaced. The MLOpsPython template uses the score code to deploy the model to do real-time scoring on ACI, AKS, or Web apps.

If you want to keep scoring:

1. Update or replace `[project name]/scoring/score.py`
1. Add any dependencies required by scoring to `[project name]/conda_dependencies.yml`
1. Modify the test cases in the `ml_service/util/smoke_test_scoring_service.py` script to match the schema of the training features in your data

# Configure Custom Batch Scoring

## Configure input and output data

The batch scoring pipeline is configured to use the default datastore for input and output. It will use sample data for scoring.

In order to configure your own input datastore and output datastores, you will need to specify an Azure Blob Storage Account and set up input and output containers.

Configure the variables below in your variable group. 

**Note: The datastore storage resource, input/output containers, and scoring data is not created automatically. Make sure that you have manually provisioned these resources and placed your scoring data in your input container with the proper name.**


| Variable Name            | Suggested Value           | Short description                                                                                                           |
| ------------------------ | ------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| SCORING_DATASTORE_STORAGE_NAME    |                  | [Azure Blob Storage Account](https://docs.microsoft.com/en-us/azure/storage/blobs/) name.                                     |
| SCORING_DATASTORE_ACCESS_KEY      |                  | [Azure Storage Account Key](https://docs.microsoft.com/en-us/rest/api/storageservices/authorize-requests-to-azure-storage). You may want to consider linking this variable to Azure KeyVault to avoid storing the access key in plain text. |
| SCORING_DATASTORE_INPUT_CONTAINER |                  | The name of the container for input data. Defaults to `input` if not set.  |
| SCORING_DATASTORE_OUTPUT_CONTAINER|                  | The name of the container for output data. Defaults to `output` if not set.  |
| SCORING_DATASTORE_INPUT_FILENAME  |                  | The filename of the input data in your container Defaults to `diabetes_scoring_input.csv` if not set.  |
| SCORING_DATASET_NAME              |                  | The AzureML Dataset name to use. Defaults to `diabetes_scoring_ds` if not set (optional).  |
| SCORING_DATASTORE_OUTPUT_FILENAME |                  | The filename to use for the output data. The pipeline will create this file. Defaults to `diabetes_scoring_output.csv` if not set (optional).  |

