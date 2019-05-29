# MLOps with Azure ML


[![Build Status](https://dev.azure.com/customai/DevopsForAI-AML/_apis/build/status/Microsoft.DevOpsForAI?branchName=master)](https://dev.azure.com/customai/DevopsForAI-AML/_build/latest?definitionId=1&branchName=master)

### Author: Praneet Solanki | Richin Jain

MLOps will help you to understand how to build the Continuous Integration and Continuous Delivery pipeline for a ML/AI project. We will be using the Azure DevOps Project for build and release/deployment pipelines along with Azure ML services for model retraining pipeline, model management and operationalization. 

![ML lifecycle](/docs/images/ml-lifecycle.png)

This template contains code and pipeline definition for a machine learning project demonstrating how to automate an end to end ML/AI workflow. The build pipelines include DevOps tasks for data sanity test, unit test, model training on different compute targets, model version management, model evaluation/model selection, model deployment as realtime web service, staged deployment to QA/prod and integration testing.


## Prerequisite
- Active Azure subscription
- At least contributor access to Azure subscription

## Getting Started:

To deploy this solution in your subscription, follow the manual instructions in the [getting started](docs/getting_started.md) doc


## Architecture Diagram

This reference architecture shows how to implement continuous integration (CI), continuous delivery (CD), and retraining pipeline for an AI application using Azure DevOps and Azure Machine Learning. The solution is built on the scikit-learn diabetes dataset but can be easily adapted for any AI scenario and other popular build systems such as Jenkins and Travis. 

![Architecture](/docs/images/Architecture_DevOps_AI.png)


## Architecture Flow

### Train Model
1. Data Scientist writes/updates the code and push it to git repo. This triggers the Azure DevOps build pipeline (continuous integration).
2. Once the Azure DevOps build pipeline is triggered, it runs following types of tasks:
    - Run for new code: Every time new code is committed to the repo, the build pipeline performs data sanity tests and unit tests on the new code.
    - One-time run: These tasks runs only for the first time the build pipeline runs. It will programatically create an [Azure ML Service Workspace](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#workspace), provision [Azure ML Compute](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-set-up-training-targets#amlcompute) (used for model training compute), and publish an [Azure ML Pipeline](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-ml-pipelines). This published Azure ML pipeline is the model training/retraining pipeline.

    > Note: The Publish Azure ML pipeline task currently runs for every code change

3. The Azure ML Retraining pipeline is triggered once the Azure DevOps build pipeline completes. All the tasks in this pipeline runs on Azure ML Compute created earlier. Following are the tasks in this pipeline:

    - **Train Model** task executes model training script on Azure ML Compute. It outputs a [model](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#model) file which is stored in the [run history](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#run).

    - **Evaluate Model** task evaluates the performance of newly trained model with the model in production. If the new model performs better than the production model, the following steps are executed. If not, they will be skipped.

    - **Register Model** task takes the improved model and registers it with the [Azure ML Model registry](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#model-registry). This allows us to version control it.

### Deploy Model

Once you have registered your ML model, you can use Azure ML + Azure DevOps to deploy it.

The **Package Model** task packages the new model along with the scoring file and its python dependencies into a [docker image](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#image) and pushes it to [Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-intro). This image is used to deploy the model as [web service](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#web-service).
    
The **Deploy Model** task handles deploying your Azure ML model to the cloud (ACI or AKS).
This pipeline deploys the model scoring image into Staging/QA and PROD environments.

 In the Staging/QA environment, one task creates an [Azure Container Instance](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-overview) and deploys the scoring image as a [web service](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#web-service) on it. 
    
The second task invokes the web service by calling its REST endpoint with dummy data.
    
5. The deployment in production is a [gated release](https://docs.microsoft.com/en-us/azure/devops/pipelines/release/approvals/gates?view=azure-devops). This means that once the model web service deployment in the Staging/QA environment is successful, a notification is sent to approvers to manually review and approve the release. Once the release is approved, the model scoring web service is deployed to [Azure Kubernetes Service(AKS)](https://docs.microsoft.com/en-us/azure/aks/intro-kubernetes) and the deployment is tested.

### Repo Details

You can find the details of the code and scripts in the repository [here](/docs/code_description.md)

### References
- [Azure Machine Learning(Azure ML) Service Workspace](https://docs.microsoft.com/en-us/azure/machine-learning/service/overview-what-is-azure-ml)
- [Azure ML CLI](https://docs.microsoft.com/en-us/azure/machine-learning/service/reference-azure-machine-learning-cli)
- [Azure ML Samples](https://docs.microsoft.com/en-us/azure/machine-learning/service/samples-notebooks)
- [Azure ML Python SDK Quickstart](https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-create-workspace-with-python)
- [Azure DevOps](https://docs.microsoft.com/en-us/azure/devops/?view=vsts)

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
