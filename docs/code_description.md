## Repo Details

### Directory Structure

High level directory structure for this repository:

```bash
├── .pipelines            <- Azure DevOps YAML pipelines for CI, PR and model training and deployment.
├── bootstrap             <- Python script to initialize this repository with a custom project name.
├── charts                <- Helm charts to deploy resources on Azure Kubernetes Service(AKS).
├── data                  <- Initial set of data to train and evaluate model. Not for use to store data.
├── diabetes_regression   <- The top-level folder for the ML project.
│   ├── evaluate          <- Python script to evaluate trained ML model.
│   ├── register          <- Python script to register trained ML model with Azure Machine Learning Service.
│   ├── scoring           <- Python score.py to deploy trained ML model.
│   ├── training          <- Python script to train ML model.
│       ├── R             <- R script to train R based ML model.
│   ├── util              <- Python script for various utility operations specific to this ML project.
├── docs                  <- Extensive markdown documentation for entire project.
├── environment_setup     <- The top-level folder for everything related to infrastructure.
│   ├── arm-templates     <- Azure Resource Manager(ARM) templates to build infrastructure needed for this project. 
│   ├── tf-templates      <- Terraform templates to build infrastructure needed for this project.
├── experimentation       <- Jupyter notebooks with ML experimentation code.
├── ml_service            <- The top-level folder for all Azure Machine Learning resources.
│   ├── pipelines         <- Python script that builds Azure Machine Learning pipelines.
│   ├── util              <- Python script for various utility operations specific to Azure Machine Learning.
├── .env.example          <- Example .env file with environment for local development experience.  
├── .gitignore            <- A gitignore file specifies intentionally un-tracked files that Git should ignore.  
├── LICENSE               <- License document for this project.
├── README.md             <- The top-level README for developers using this project.  
```

The repository provides a template with folders structure suitable for maintaining multiple ML projects. There are common folders such as ***.pipelines***, ***environment_setup***, ***ml_service*** and folders containing the code base for each ML project. This repository contains a single sample ML project in the ***diabetes_regression*** folder. This folder is going to be automatically renamed to your project name if you follow the [bootstrap procedure](../bootstrap/README.md).

### Environment Setup

- `environment_setup/install_requirements.sh` : This script prepares a local conda environment i.e. install the Azure ML SDK and the packages specified in environment definitions.

- `environment_setup/iac-*-arm.yml, arm-templates` : Infrastructure as Code piplines to create required resources using ARM, along with corresponding arm-templates. Infrastructure as Code can be deployed with this template or with the Terraform template.

- `environment_setup/iac-*-tf.yml, tf-templates` : Infrastructure as Code piplines to create required resources using Terraform, along with corresponding tf-templates. Infrastructure as Code can be deployed with this template or with the ARM template.

- `environment_setup/iac-remove-environment.yml` : Infrastructure as Code piplines to delete the created required resources.

- `environment_setup/Dockerfile` : Dockerfile of a build agent containing Python 3.6 and all required packages.

- `environment_setup/docker-image-pipeline.yml` : An AzDo pipeline for building and pushing [microsoft/mlopspython](https://hub.docker.com/_/microsoft-mlops-python) image.

### Pipelines

- `.pipelines/abtest.yml` : a pipeline demonstrating [Canary deployment strategy](./docs/canary_ab_deployment.md).
- `.pipelines/code-quality-template.yml` : a pipeline template used by the CI and PR pipelines. It contains steps performing linting, data and unit testing.
- `.pipelines/diabetes_regression-ci-image.yml` : a pipeline building a scoring image for the diabetes regression model.
- `.pipelines/diabetes_regression-ci.yml` : a pipeline triggered when the code is merged into **master**. It performs linting, data integrity testing, unit testing, building and publishing an ML pipeline.
- `.pipelines/diabetes_regression-cd.yml` : a pipeline triggered when the code is merged into **master** and the `.pipelines/diabetes_regression-ci.yml` completes. Deploys the model to ACI, AKS or Webapp.
- `.pipelines/diabetes_regression-package-model-template.yml` : Pipeline template that creates a model package and adds the package location to the environment for subsequent tasks to use.
- `.pipelines/diabetes_regression-get-model-id-artifact-template.yml` : a pipeline template used by the `.pipelines/diabetes_regression-cd.yml` pipeline. It takes the model metadata artifact published by the previous pipeline and gets the model ID.
- `.pipelines/diabetes_regression-publish-model-artifact-template.yml` : a pipeline template used by the `.pipelines/diabetes_regression-ci.yml` pipeline. It finds out if a new model was registered and publishes a pipeline artifact containing the model metadata.
- `.pipelines/helm-*.yml` : pipeline templates used by the `.pipelines/abtest.yml` pipeline.
- `.pipelines/pr.yml` : a pipeline triggered when a **pull request** to the **master** branch is created. It performs linting, data integrity testing and unit testing only.

### ML Services

- `ml_service/pipelines/diabetes_regression_build_train_pipeline.py` : builds and publishes an ML training pipeline. It uses Python on ML Compute.
- `ml_service/pipelines/diabetes_regression_build_train_pipeline_with_r.py` : builds and publishes an ML training pipeline. It uses R on ML Compute.
- `ml_service/pipelines/diabetes_regression_build_train_pipeline_with_r_on_dbricks.py` : builds and publishes an ML training pipeline. It uses R on Databricks Compute.
- `ml_service/pipelines/run_train_pipeline.py` : invokes a published ML training pipeline (Python on ML Compute) via REST API.
- `ml_service/util` : contains common utility functions used to build and publish an ML training pipeline.

### Environment Definitions

- `diabetes_regression/conda_dependencies.yml` : Conda environment definition for the environment used for both training and scoring (Docker image in which train.py and score.py are run).
- `diabetes_regression/ci_dependencies.yml` : Conda environment definition for the CI environment.

### Training Step

- `diabetes_regression/training/train_aml.py`: a training step of an ML training pipeline.
- `diabetes_regression/training/train.py` : ML functionality called by train_aml.py
- `diabetes_regression/training/R/r_train.r` : training a model with R basing on a sample dataset (weight_data.csv).
- `diabetes_regression/training/R/train_with_r.py` : a python wrapper (ML Pipeline Step) invoking R training script on ML Compute
- `diabetes_regression/training/R/train_with_r_on_databricks.py` : a python wrapper (ML Pipeline Step) invoking R training script on Databricks Compute
- `diabetes_regression/training/R/weight_data.csv` : a sample dataset used by R script (r_train.r) to train a model
- `diabetes_regression/training/R/test_train.py` : a unit test for the training script(s)

### Evaluation Step

- `diabetes_regression/evaluate/evaluate_model.py` : an evaluating step which cancels the pipeline in case of non-improvement.

### Registering Step

- `diabetes_regression/register/register_model.py` : registers a new trained model if evaluation shows the new model is more performant than the previous one.

### Scoring

- `diabetes_regression/scoring/score.py` : a scoring script which is about to be packed into a Docker Image along with a model while being deployed to QA/Prod environment.
- `diabetes_regression/scoring/inference_config.yml`, `deployment_config_aci.yml`, `deployment_config_aks.yml` : configuration files for the [AML Model Deploy](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.private-vss-services-azureml&ssr=false#overview) pipeline task for ACI and AKS deployment targets.
- `diabetes_regression/scoring/scoreA.py`, `diabetes_regression/scoring/scoreB.py` : simplified scoring files for the [Canary deployment sample](./docs/canary_ab_deployment.md).
