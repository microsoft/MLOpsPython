---
page_type: sample
languages:
- python
products:
- azure
- azure-machine-learning-service
- azure-devops
description: "Code which demonstrates how to set up and operationalize an MLOps flow leveraging Azure Machine Learning and Azure DevOps."
---

# MLOps with Azure ML

[![Build Status](https://aidemos.visualstudio.com/MLOps/_apis/build/status/microsoft.MLOpsPython?branchName=master)](https://aidemos.visualstudio.com/MLOps/_build/latest?definitionId=151&branchName=master)

MLOps will help you to understand how to build the Continuous Integration and Continuous Delivery pipeline for a ML/AI project. We will be using the Azure DevOps Project for build and release/deployment pipelines along with Azure ML services for model retraining pipeline, model management and operationalization.

![ML lifecycle](/docs/images/ml-lifecycle.png)

This template contains code and pipeline definition for a machine learning project demonstrating how to automate an end to end ML/AI workflow. The build pipelines include DevOps tasks for data sanity test, unit test, model training on different compute targets, model version management, model evaluation/model selection, model deployment as realtime web service, staged deployment to QA/prod and integration testing.

## Prerequisite

- Active Azure subscription
- At least contributor access to Azure subscription

## Getting Started

To deploy this solution in your subscription, follow the manual instructions in the [getting started](docs/getting_started.md) doc

## Architecture Diagram

This reference architecture shows how to implement continuous integration (CI), continuous delivery (CD), and retraining pipeline for an AI application using Azure DevOps and Azure Machine Learning. The solution is built on the scikit-learn diabetes dataset but can be easily adapted for any AI scenario and other popular build systems such as Jenkins and Travis.

![Architecture](/docs/images/main-flow.png)

## Architecture Flow

### Train Model

1. Data Scientist writes/updates the code and push it to git repo. This triggers the Azure DevOps build pipeline (continuous integration).
2. Once the Azure DevOps build pipeline is triggered, it performs code quality checks, data sanity tests, unit tests, builds an [Azure ML Pipeline](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-ml-pipelines) and publishes it in an [Azure ML Service Workspace](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#workspace).
3. The [Azure ML Pipeline](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-ml-pipelines) is triggered once the Azure DevOps build pipeline completes. All the tasks in this pipeline runs on Azure ML Compute. Following are the tasks in this pipeline:

    - **Train Model** task executes model training script on Azure ML Compute. It outputs a [model](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#models) file which is stored in the [run history](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#runs).

    - **Evaluate Model** task evaluates the performance of the newly trained model with the model in production. If the new model performs better than the production model, the following steps are executed. If not, they will be skipped.

    - **Register Model** task takes the improved model and registers it with the [Azure ML Model registry](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#model-registry). This allows us to version control it.

### Deploy Model

Once you have registered your ML model, you can use Azure ML + Azure DevOps to deploy it.

The [Azure DevOps multi-stage pipeline](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/stages?view=azure-devops&tabs=yaml) packages the new model along with the scoring file and its python dependencies into a [docker image](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#image) and pushes it to [Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-intro). This image is used to deploy the model as [web service](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#web-service) across QA and Prod environments. The QA environment is running on top of [Azure Container Instances (ACI)](https://azure.microsoft.com/en-us/services/container-instances/) and the Prod environment is built with [Azure Kubernetes Service (AKS)](https://docs.microsoft.com/en-us/azure/aks/intro-kubernetes).

### Repo Details

You can find the details of the code and scripts in the repository [here](/docs/code_description.md)

### References

- [Azure Machine Learning(Azure ML) Service Workspace](https://docs.microsoft.com/en-us/azure/machine-learning/service/overview-what-is-azure-ml)
- [Azure ML CLI](https://docs.microsoft.com/en-us/azure/machine-learning/service/reference-azure-machine-learning-cli)
- [Azure ML Samples](https://docs.microsoft.com/en-us/azure/machine-learning/service/samples-notebooks)
- [Azure ML Python SDK Quickstart](https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-create-workspace-with-python)
- [Azure DevOps](https://docs.microsoft.com/en-us/azure/devops/?view=vsts)

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit <https://cla.microsoft.com.>

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
