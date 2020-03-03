# Bootstrap from MLOpsPython repository

To use this existing project structure and scripts for your new ML project, you can quickly get started from the existing repository, bootstrap and create a template that works for your ML project. Bootstrapping will prepare a similar directory structure for your project which includes renaming files and folders, deleting and cleaning up some directories and fixing imports and absolute path based on your project name. This will enable reusing various resources like pre-built pipelines and scripts for your new project.

## Generating the project structure

To bootstrap from the existing MLOpsPython repository clone this repository, ensure Python is installed locally, and run bootstrap.py script as below

`python bootstrap.py --d [dirpath] --n [projectname]`

Where `[dirpath]` is the absolute path to the root of your directory where MLOps repo is cloned and `[projectname]` is the name of your ML project.

The script renames folders, files and files' content from the base project name `diabetes` to your project name. However, you might need to manually rename variables defined in a variable group and their values.

[This article](https://docs.microsoft.com/azure/machine-learning/tutorial-convert-ml-experiment-to-production#use-your-own-model-with-mlopspython-code-template) will also assist to use this code template for your own ML project.

### Using an existing dataset

The training ML pipeline uses a [sample diabetes dataset](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_diabetes.html) as training data. To use your own data, you need to [create a Dataset](https://docs.microsoft.com/azure/machine-learning/how-to-create-register-datasets) in your workspace and add a DATASET_NAME variable in the ***devopsforai-aml-vg*** variable group with the Dataset name. You'll also need to modify the test cases in the **ml_service/util/smoke_test_scoring_service.py** script to match the schema of the training features in your dataset.

## Customizing the CI and AML environments

In your project you will want to customize your own Docker image and Conda environment to use only the dependencies and tools required for your use case. This requires you to edit the following environment definition files:

- The Azure ML training and scoring Conda environment defined in [conda_dependencies.yml](diabetes_regression/conda_dependencies.yml).
- The CI Docker image and Conda environment used by the Azure DevOps build agent. See [instructions for customizing the Azure DevOps job container](../docs/custom_container.md).

You will want to synchronize dependency versions as appropriate between both environment definitions (for example, ML libraries used both in training and in unit tests).
