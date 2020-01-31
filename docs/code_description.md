## Repo Details

### Environment Setup

- `environment_setup/install_requirements.sh` : This script prepares a local conda environment i.e. install the Azure ML SDK and the packages specified in environment definitions.

- `environment_setup/iac-*.yml, arm-templates` : Infrastructure as Code piplines to create and delete required resources along with corresponding arm-templates.

- `environment_setup/Dockerfile` : Dockerfile of a build agent containing Python 3.6 and all required packages.

- `environment_setup/docker-image-pipeline.yml` : An AzDo pipeline for building and pushing [microsoft/mlopspython](https://hub.docker.com/_/microsoft-mlops-python) image. 

### Pipelines

- `.pipelines/azdo-base-pipeline.yml` : a pipeline template used by ci-build-train pipeline and pr-build-train pipelines. It contains steps performing linting, data and unit testing.  
- `.pipelines/diabetes_regression-ci-build-train.yml` : a pipeline triggered when the code is merged into **master**. It performs linting, data integrity testing, unit testing, building and publishing an ML pipeline.
- `.pipelines/azdo-pr-build-train.yml` : a pipeline triggered when a **pull request** to the **master** branch is created. It performs linting, data integrity testing and unit testing only.

### ML Services

- `ml_service/pipelines/diabetes_regression_build_train_pipeline.py` : builds and publishes an ML training pipeline. It uses Python on ML Compute.
- `ml_service/pipelines/diabetes_regression_build_train_pipeline_with_r.py` : builds and publishes an ML training pipeline. It uses R on ML Compute.
- `ml_service/pipelines/diabetes_regression_build_train_pipeline_with_r_on_dbricks.py` : builds and publishes an ML training pipeline. It uses R on Databricks Compute.
- `ml_service/pipelines/run_train_pipeline.py` : invokes a published ML training pipeline (Python on ML Compute) via REST API.
- `ml_service/pipelines/diabetes_regression_verify_train_pipeline.py` : determines whether the evaluate_model.py step of the training pipeline registered a new model.
- `ml_service/pipelines/deploy_web_service.py` : deploys the model to ACI or AKS. Also contains the deployment configuration for the environments (e.g. CPU, memory, number of replicas in AKS).
- `ml_service/util` : contains common utility functions used to build and publish an ML training pipeline.

### Environment Definitions

- `diabetes_regression/training_dependencies.yml` : Conda environment definition for the training environment (Docker image in which train.py is run).
- `diabetes_regression/scoring_dependencies.yml` : Conda environment definition for the scoring environment (Docker image in which score.py is run).
- `diabetes_regression/ci_dependencies.yml` : Conda environment definition for the CI environment.

### Code

- `diabetes_regression/training/train.py` : a training step of an ML training pipeline.
- `diabetes_regression/evaluate/evaluate_model.py` : an evaluating step of an ML training pipeline which registers a new trained model if evaluation shows the new model is more performant than the previous one.
- `diabetes_regression/evaluate/register_model.py` : (LEGACY) registers a new trained model if evaluation shows the new model is more performant than the previous one.
- `diabetes_regression/training/R/r_train.r` : training a model with R basing on a sample dataset (weight_data.csv).
- `diabetes_regression/training/R/train_with_r.py` : a python wrapper (ML Pipeline Step) invoking R training script on ML Compute 
- `diabetes_regression/training/R/train_with_r_on_databricks.py` : a python wrapper (ML Pipeline Step) invoking R training script on Databricks Compute
- `diabetes_regression/training/R/weight_data.csv` : a sample dataset used by R script (r_train.r) to train a model

### Scoring
- `diabetes_regression/scoring/score.py` : a scoring script which is about to be packed into a Docker Image along with a model while being deployed to QA/Prod environment.
