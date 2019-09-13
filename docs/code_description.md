## Repo Details

### Environment Setup

- `environment_setup/requirements.txt` : It consists of a list of python packages which are needed by the train.py to run successfully on host agent (locally).

- `environment_setup/install_requirements.sh` : This script prepares the python environment i.e. install the Azure ML SDK and the packages specified in requirements.txt

- `environment_setup/iac-*.yml, arm-templates` : Infrastructure as Code piplines to create and delete required resources along with corresponding arm-templates.

- `environment_setup/Dockerfile` : Dockerfile of a build agent containing Python 3.6 and all required packages.

- `environment_setup/docker-image-pipeline.yml` : An AzDo pipeline for building and pushing [microsoft/mlopspython](https://hub.docker.com/_/microsoft-mlops-python) image. 

### Pipelines

- `.pipelines/azdo-base-pipeline.yml` : a pipeline template used by ci-build-train pipeline and pr-build-train pipelines. It contains steps performing linting, data and unit testing.  
- `.pipelines/azdo-ci-build-train.yml` : a pipeline triggered when the code is merged into **master**. It performs linting, data integrity testing, unit testing, building and publishing an ML pipeline.
- `.pipelines/azdo-pr-build-train.yml` : a pipeline triggered when a **pull request** to the **master** branch is created. It performs linting, data integrity testing and unit testing only.

### ML Services

- `ml_service/pipelines/build_train_pipeline.py` : builds and publishes an ML training pipeline.
- `ml_service/pipelines/run_train_pipeline.py` : invokes a published ML training pipeline via REST API.
- `ml_service/util` : contains common utility functions used to build and publish an ML training pipeline.

### Code

- `code/training/train.py` : a training step of an ML training pipeline.
- `code/evaluate/evaluate_model.py` : an evaluating step of an ML training pipeline which registers a new trained model if evaluation shows the new model is more performant than the previous one.
- `code/evaluate/register_model.py` : (LEGACY) registers a new trained model if evaluation shows the new model is more performant than the previous one.

### Scoring
- code/scoring/score.py : a scoring script which is about to be packed into a Docker Image along with a model while being deployed to QA/Prod environment.
- code/scoring/conda_dependencies.yml : contains a list of dependencies required by sore.py to be installed in a deployable Docker Image 
- code/scoring/inference_config.yml, deployment_config_aci.yml, deployment_config_aks.yml : configuration files for the [AML Model Deploy](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.private-vss-services-azureml&ssr=false#overview) pipeline task for ACI and AKS deployment targets.


