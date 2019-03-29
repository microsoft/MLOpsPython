### Author: | Praneet Singh Solanki | Richin Jain |

# DevOps For AI

[![Build Status](https://dev.azure.com/customai/DevopsForAI-AML/_apis/build/status/Microsoft.DevOpsForAI?branchName=master)](https://dev.azure.com/customai/DevopsForAI-AML/_build/latest?definitionId=1&branchName=master)



DevOps for AI will help you to understand how to build the Continuous Integration and Continuous Delivery pipeline for a ML/AI project. We will be using the Azure DevOps Project for build and release/deployment pipelines along with Azure ML services for model retraining pipeline, model management and operationalization. 

This template contains code and pipeline definition for a machine learning project demonstrating how to automate the end to end ML/AI project. The build pipelines include DevOps tasks for data sanity test, unit test, model training on different compute targets, model version management, model evaluation/model selection, model deployment as realtime web service, staged deployment to QA/prod, integration testing and functional testing.


## Prerequisite
- Active Azure subscription
- At least contributor access to Azure subscription

## Getting Started:
Skip above step if already done.

Once the template is imported for personal Azure DevOps account using DevOps demo generator, you need to follow below steps to get the pipeline running:



## Architecture Diagram

This reference architecture shows how to implement continuous integration (CI), continuous delivery (CD), and retraining pipeline for an AI application using Azure DevOps and Azure Machine Learning. The solution is built on the scikit-learn diabetes dataset but can be easily adapted for any AI scenario and other popular build systems such as Jenkins and Travis. 

![Architecture](as/docs/images/Architecture_DevOps_AI.png)


## Architecture Flow

1. Data Scientist writes/updates the code and push it to git repo. This triggers the Azure DevOps build pipeline (contineous integration).
2. Once the Azure DevOps build pipeline is triggered, it runs following type of tasks:
    - Run for new code: Everytime new code is commited to the repo, build pipeline performs data sanity test and unit tests the new code.

    - One-time run: These tasks runs only for the first time build pipeline run, they create [Azure ML Service Workspace](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#workspace), [Azure ML Compute](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-set-up-training-targets#amlcompute) used as model training compute and publish a [Azure ML Pipeline](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-ml-pipelines) with code. This published Azure ML pipeline is the model training/retraining pipeline.

    `Note: The task Publish Azure ML pipeline currently runs for every code change`

3. The Azure ML Retraining pipeline is triggered once the Azure DevOps build pipeline completes. All the tasks in this pipeline runs on Azure ML Compute created earlier. Following are the tasks in this pipeline:

    - **Train Model** task executes model training script on Azure ML Compute. It outputs a [model](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#model) file which is stored in the [run history](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#run)

    - **Evaluate Model** task evaluates the performance of newly trained model with the model in production. If new trained model performs better than the production model, next steps are executed. Else next steps are skipped.

    - **Register Model** task takes the new trained better performing model and registers it with the [Azure ML Model registry](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#model-registry) to version control it.

    - **Package Model** task packages the new trained model along with scoring file and python dependencies into a docker [image](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#image) and pushes it to [Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-intro). This image is used to deploy model as [web service](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#web-service).
    
4. Once a new model scoring image is pushed to Azure Container Registry, Azure DevOps Release/Deployment pipeline is triggered. This pipeline deploys the model scoring image into Staging/QA and PROD environments.

    - In the Staging/QA, one task creates [Azure Container Instance](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-overview) and deploy scoring image as [web service](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#web-service) on it. 
    
    - The second task test this web service by calling its REST endpoint with dummy data.

    
5. 

### Repo Details

You can find the details of the code and scripts in the repository [here](/docs/code_description.md)

### References
- [Azure Machine Learning(Azure ML) Service Workspace](https://docs.microsoft.com/en-us/azure/machine-learning/service/overview-what-is-azure-ml)

- [Azure ML Samples](https://docs.microsoft.com/en-us/azure/machine-learning/service/samples-notebooks)
- [Azure ML Python SDK Quickstart](https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-create-workspace-with-python)
- [Azure DevOps](https://docs.microsoft.com/en-us/azure/devops/?view=vsts)
- [DevOps for AI template (Old Version)](https://azuredevopsdemogenerator.azurewebsites.net/?name=azure%20machine%20learning)

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
