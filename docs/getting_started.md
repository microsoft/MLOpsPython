
# Getting Started with MLOpsPython <!-- omit in toc -->

This guide shows how to get MLOpsPython working with a sample ML project ***diabetes_regression***. The project creates a linear regression model to predict diabetes. You can adapt this example to use with your own project.

We recommend working through this guide completely to ensure everything is working in your environment. After the sample is working, follow the [bootstrap instructions](../bootstrap/README.md) to convert the ***diabetes_regression*** sample into a starting point for your project.

- [Setting up Azure DevOps](#setting-up-azure-devops)
- [Get the code](#get-the-code)
- [Create a Variable Group for your Pipeline](#create-a-variable-group-for-your-pipeline)
  - [Variable Descriptions](#variable-descriptions)
- [Provisioning resources using Azure Pipelines](#provisioning-resources-using-azure-pipelines)
  - [Create an Azure DevOps Service Connection for the Azure Resource Manager](#create-an-azure-devops-service-connection-for-the-azure-resource-manager)
  - [Create the IaC Pipeline](#create-the-iac-pipeline)
- [Create an Azure DevOps Service Connection for the Azure ML Workspace](#create-an-azure-devops-service-connection-for-the-azure-ml-workspace)
- [Set up Build, Release Trigger, and Release Multi-Stage Pipeline](#set-up-build-release-trigger-and-release-multi-stage-pipeline)
  - [Set up the Pipeline](#set-up-the-pipeline)
- [Further Exploration](#further-exploration)
  - [Deploy the Model to Azure Kubernetes Service](#deploy-the-model-to-azure-kubernetes-service)
  - [Deploy the Model to Azure App Service (Azure Web App for containers)](#deploy-the-model-to-azure-app-service-azure-web-app-for-containers)
  - [Example pipelines using R](#example-pipelines-using-r)
  - [Observability and Monitoring](#observability-and-monitoring)
  - [Clean up the example resources](#clean-up-the-example-resources)
- [Next Steps: Integrating your project](#next-steps-integrating-your-project)
  - [Additional Variables and Configuration](#additional-variables-and-configuration)
    - [More variable options](#more-variable-options)
    - [Local configuration](#local-configuration)

## Setting up Azure DevOps

We'll use Azure DevOps for running the multi-stage pipeline with build (CI), ML training, and scoring service release (CD) stages. If you don't already have an Azure DevOps organization, create one by following the instructions [here](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/create-organization?view=azure-devops).

If you already have an Azure DevOps organization, create a [new project](https://docs.microsoft.com/en-us/azure/devops/organizations/projects/create-project?view=azure-devops).

## Get the code

If you intend to contribute back to this repository, fork the project. Otherwise use the [code template](https://github.com/microsoft/MLOpsPython/generate), which copies the entire code base to your own GitHub location with the git commit history restarted. You can use this for experimentation and following this guide.

## Create a Variable Group for your Pipeline

We'll create a *variable group* inside Azure DevOps to store values that we need across multiple pipelines or pipeline stages. You can either store the values directly in [Azure DevOps](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=designer#create-a-variable-group) or connect to an Azure Key Vault in your subscription. Check out the documentation [here](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=designer#create-a-variable-group) to learn more about how to create a variable group and [link](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=designer#use-a-variable-group) it to your pipeline.

Navigate to **Library** in the **Pipelines** section as indicated below:

![Library Variable Groups](./images/library_variable_groups.png)

Create a variable group named **``devopsforai-aml-vg``**. The YAML pipeline definitions in this repository refer to this variable group by name.

The variable group should contain the following required variables:

| Variable Name            | Suggested Value           | Short description                                                                                                            |
| ------------------------ | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| BASE_NAME                | [unique base name]        | Naming prefix                                                                                                                |
| LOCATION                 | centralus                 | Azure location                                                                                                               |
| RESOURCE_GROUP           | mlops-RG                  | Azure Resource Group                                                                                                         |
| WORKSPACE_NAME           | mlops-AML-WS              | Azure ML Workspace name                                                                                                      |
| AZURE_RM_SVC_CONNECTION  | azure-resource-connection | [Azure Resource Manager Service Connection](#create-an-azure-devops-service-connection-for-the-azure-resource-manager) name |
| WORKSPACE_SVC_CONNECTION | aml-workspace-connection  | [Azure ML Workspace Service Connection](#create-an-azure-devops-azure-ml-workspace-service-connection) name                  |
| ACI_DEPLOYMENT_NAME      | diabetes-aci              | Azure Container Interface                                                                                                    |

Make sure you select the **Allow access to all pipelines** checkbox in the variable group configuration.

### Variable Descriptions

**WORKSPACE_NAME** is used for creating the Azure Machine Learning Workspace. You can provide an existing AML Workspace here if you've got one.

**BASE_NAME** is used as a prefix for naming Azure resources. When sharing an Azure subscription, the prefix allows us to avoid naming collisions for resources that require unique names, for example, Azure Blob Storage and Registry DNS names. Make sure to set BASE_NAME to a unique name so that created resources will have unique names (for example, MyUniqueMLamlcr, MyUniqueML-AML-KV, and so on.) The length of the BASE_NAME value should not exceed 10 characters and must contain numbers and letters only.

**RESOURCE_GROUP** is used as the name for the resource group that will hold the Azure resources for the solution. If providing an existing AML Workspace, set this value to the corresponding resource group name.

**AZURE_RM_SVC_CONNECTION** is used by the [Azure DevOps pipeline]((../environment_setup/iac-create-environment-pipeline.yml)) that creates the Azure ML workspace and associated resources through Azure Resource Manager. We'll create the connection in a [step below](#create-an-azure-devops-service-connection-for-the-azure-resource-manager).

**WORKSPACE_SVC_CONNECTION** is used to reference a [service connection for the Azure ML workspace](#create-an-azure-devops-azure-ml-workspace-service-connection). You'll create the connection after [provisioning the workspace](#provisioning-resources-using-azure-pipelines) in a [step below](#create-an-azure-devops-service-connection-for-the-azure-ml-workspace).

## Provisioning resources using Azure Pipelines

The easiest way to create all required Azure resources (Resource Group, ML Workspace, Container Registry, Storage Account, etc.) is to use the **Infrastructure as Code (IaC)** [pipeline in this repository](../environment_setup/iac-create-environment-pipeline.yml). The pipeline takes care of setting up all required resources based on these [ARM templates](../environment_setup/arm-templates/cloud-environment.json).

### Create an Azure DevOps Service Connection for the Azure Resource Manager

The [IaC provisioning pipeline]((../environment_setup/iac-create-environment-pipeline.yml)) requires an **Azure Resource Manager** [service connection](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml#create-a-service-connection).

![Create service connection](./images/create-rm-service-connection.png)

Leave the **``Resource Group``** field empty.

**Note:** Creating the ARM service connection scope requires 'Owner' or 'User Access Administrator' permissions on the subscription.
You must also have sufficient permissions to register an application with your Azure AD tenant, or receive the ID and secret of a service principal from your Azure AD Administrator. That principal must have 'Contributor' permissions on the subscription.

### Create the IaC Pipeline

In your Azure DevOps project, create a build pipeline from your forked repository:

![Build connect step](./images/build-connect.png)

Select the **Existing Azure Pipelines YAML file** option and set the path to [/environment_setup/iac-create-environment-pipeline.yml](../environment_setup/iac-create-environment-pipeline.yml):

![Configure step](./images/select-iac-pipeline.png)

Having done that, run the pipeline:

![IaC run](./images/run-iac-pipeline.png)

Check that the newly created resources appear in the [Azure Portal](https://portal.azure.com):

![Created resources](./images/created-resources.png)

## Create an Azure DevOps Service Connection for the Azure ML Workspace

At this point, you should have an Azure ML Workspace created. Similar to the Azure Resource Manager service connection, we need to create an additional one for the workspace.

Install the **Azure Machine Learning** extension to your Azure DevOps organization from the [Marketplace](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.vss-services-azureml). The extension is required for the service connection.

Create a new service connection to your ML workspace using the [Azure DevOps Azure ML task instructions](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.vss-services-azureml) to enable executing the Azure ML training pipeline. The connection name needs to match `WORKSPACE_SVC_CONNECTION` that you set in the variable group above.

![Created resources](./images/ml-ws-svc-connection.png)

**Note:** Similar to the ARM service connection we created earlier, creating a service connection with Azure Machine Learning workspace scope requires 'Owner' or 'User Access Administrator' permissions on the Workspace.
You must also have sufficient permissions to register an application with your Azure AD tenant, or receive the ID and secret of a service principal from your Azure AD Administrator. That principal must have Contributor permissions on the Azure ML Workspace.

## Set up Build, Release Trigger, and Release Multi-Stage Pipeline

Now that you've provisioned all the required Azure resources and service connections, you can set up the pipeline for deploying your ML model to production. The pipeline has a sequence of stages for:

1. **Model Code Continuous Integration:** triggered on code changes to master branch on GitHub. Runs linting, unit tests, code coverage and publishes a training pipeline.
1. **Train Model**: invokes the Azure ML service to trigger the published training pipeline to train, evaluate, and register a model.
1. **Release Deployment:** deploys a model to either [Azure Container Instances (ACI)](https://azure.microsoft.com/en-us/services/container-instances/), [Azure Kubernetes Service (AKS)](https://azure.microsoft.com/en-us/services/kubernetes-service), or [Azure App Service](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-deploy-app-service) environments. For simplicity, we're going to initially focus on ACI. See [Further Exploration](#further-exploration) for other deployment types.
   1. **Note:** Edit the pipeline definition to remove unused stages. For example, if you're deploying to ACI and AKS only, delete the unused `Deploy_Webapp` stage.

### Set up the Pipeline

In your Azure DevOps project, create and run a new build pipeline based on the  [diabetes_regression-ci.yml](../.pipelines/diabetes_regression-ci.yml)
pipeline definition in your forked repository.

![Configure CI build pipeline](./images/ci-build-pipeline-configure.png)

Once the pipeline is finished, check the execution result:

![Build](./images/multi-stage-aci.png)

Also check the published training pipeline in the **mlops-AML-WS** workspace in [Azure Portal](https://portal.azure.com/):

![Training pipeline](./images/training-pipeline.png)

Great, you now have the build pipeline set up which automatically triggers every time there's a change in the master branch!

* The first stage of the pipeline, **Model CI**, does linting, unit testing, code coverage, building, and publishes an **ML Training Pipeline** in an **ML Workspace**.

* The second stage of the pipeline, **Train model**, triggers the run of the ML Training Pipeline. The training pipeline will train, evaluate, and register a new model. The actual computation happens on an [Azure Machine Learning Compute cluster](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-set-up-training-targets#amlcompute). In Azure DevOps, the stage runs an agentless job that waits for the completion of the Azure ML job. This allows the pipeline to wait for training completion for hours or even days without using agent resources.

If  model evaluation determines that the new model does not perform better than the previous one, the new model will not be registered and the pipeline will be canceled.

* The third stage of the pipeline, **Deploy to ACI**, deploys the model to the QA environment in [Azure Container Instances](https://azure.microsoft.com/en-us/services/container-instances/). After deployment, it runs a *smoke test* for validation by sending a sample query to the scoring web service and verifies that it returns an expected response.

The pipeline uses a Docker container on the Azure Pipelines agents to accomplish the pipeline steps. The image of the container ***mcr.microsoft.com/mlops/python:latest*** is built with this [Dockerfile](../environment_setup/Dockerfile) and it has all necessary dependencies installed for the purposes of this repository. This image is an example of a custom Docker image with a pre-baked environment. The environment is guaranteed to be the same on any building agent, VM, or local machine. In your project, you'll want to build your own Docker image that only contains the dependencies and tools required for your use case. Your image will probably be smaller and faster, and it will be maintained by your team.

After the pipeline is finished, you'll see a new model in the **ML Workspace**:

![Trained model](./images/trained-model.png)

To disable the automatic trigger of the training pipeline, change the `auto-trigger-training` variable as listed in the `.pipelines\diabetes_regression-ci.yml` pipeline to `false`.  You can also override the variable at runtime execution of the pipeline.

To skip model training and registration, and deploy a model successfully registered by a previous build (for testing changes to the score file or inference configuration), add the variable `MODEL_BUILD_ID` when the pipeline is queued, and set the value to the id of the previous build.

## Further Exploration

You should now have a working pipeline that can get you started with MLOpsPython. Below are some additional features offered that might suit your scenario.

### Deploy the Model to Azure Kubernetes Service

MLOpsPython also can deploy to [Azure Kubernetes Service](https://azure.microsoft.com/en-us/services/kubernetes-service).

Creating a Kubernetes cluster on AKS is out of scope of this tutorial, but you can find set up information [here](https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough-portal#create-an-aks-cluster).

**Note:** If your target deployment environment is a K8s cluster and you want to implement Canary and/or A/B testing deployment strategies, check out this [tutorial](./canary_ab_deployment.md).

We'll keep the ACI deployment active because it is a lightweight way to validate changes before deploying to AKS.

In the Variables tab, edit your variable group (`devopsforai-aml-vg`). In the variable group definition, add these variables:

| Variable Name       | Suggested Value |
| ------------------- | --------------- |
| AKS_COMPUTE_NAME    | aks             |
| AKS_DEPLOYMENT_NAME | diabetes-aks    |

Set **AKS_COMPUTE_NAME** to the *Compute name* of the Inference Cluster that references the AKS cluster in your Azure ML Workspace.

After successfully deploying to Azure Container Instances, the next stage will deploy the model to Kubernetes and run a smoke test.

![build](./images/multi-stage-aci-aks.png)

Consider enabling [manual approvals](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/approvals) before the deployment stages.

### Deploy the Model to Azure App Service (Azure Web App for containers)

If you want to deploy your scoring service as an [Azure App Service](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-deploy-app-service) instead of ACI and AKS, follow these additional steps.

In the Variables tab, edit your variable group (`devopsforai-aml-vg`) and add a variable:

| Variable Name          | Suggested Value        |
| ---------------------- | ---------------------- |
| WEBAPP_DEPLOYMENT_NAME | _name of your web app_ |

Set **WEBAPP_DEPLOYMENT_NAME** to the name of your Azure Web App. This app must exist before you can deploy the model to it.

Delete the **ACI_DEPLOYMENT_NAME** variable.

The pipeline uses the [Create Image Script](../ml_service/util/create_scoring_image.py) to create a scoring image. The image will be registered under an Azure Container Registry (ACR) instance that belongs to Azure Machine Learning Service. Any dependencies that scoring file depends on can also be packaged with the container with Image config.
[Learn more on how to create a container with AML SDK](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.image.image.image?view=azure-ml-py#create-workspace--name--models--image-config-).

Make sure your webapp has the credentials to pull the image from the Azure Container Registry created by the Infrastructure as Code pipeline. Instructions can be found on: [Configure registry credentials in web app](https://docs.microsoft.com/en-us/azure/devops/pipelines/targets/webapp-on-container-linux?view=azure-devops&tabs=dotnet-core%2Cyaml#configure-registry-credentials-in-web-app). You'll need to run the pipeline once (including the Deploy to Webapp stage up to the `Create scoring image` step) so an image is present in the registry. After that, you can connect the Webapp to the Azure Container Registry in the Azure Portal.

![build](./images/multi-stage-webapp.png)

### Example pipelines using R

The build pipeline also supports building and publishing ML pipelines using R to train a model. You can enable it by changing the `build-train-script` pipeline variable to either of:

* `diabetes_regression_build_train_pipeline_with_r.py` to train a model with R on Azure ML Compute. You'll also need to uncomment (include) the `r-essentials` Conda packages in the environment definition `diabetes_regression/conda_dependencies.yml`.
* `diabetes_regression_build_train_pipeline_with_r_on_dbricks.py` to train a model with R on Databricks. You'll need to manually create a Databricks cluster and attach it to the ML Workspace as a compute resource. Set the DB_CLUSTER_ID and DATABRICKS_COMPUTE_NAME variables.

Example ML pipelines using R have a single step to train a model. They don't demonstrate how to evaluate and register a model. The evaluation and registering techniques are shown only in the Python implementation.

### Observability and Monitoring

* You can explore aspects of model observability in the solution, such as:
  * **Logging**: navigate to the Application Insights instance linked to the Azure ML Portal,
    then to the Logs (Analytics) pane. The following sample query correlates HTTP requests with custom logs
    generated in `score.py`, and can be used, for example, to analyze query duration vs. scoring batch size:

        let Traceinfo=traces
        | extend d=parse_json(tostring(customDimensions.Content))
        | project workspace=customDimensions.["Workspace Name"],
            service=customDimensions.["Service Name"],
            NumberOfPredictions=tostring(d.NumberOfPredictions),
            id=tostring(d.RequestId),
            TraceParent=tostring(d.TraceParent);
        requests
        | project timestamp, id, success, resultCode, duration
        | join kind=fullouter Traceinfo on id
        | project-away id1

  * **Distributed tracing**: The smoke test client code sets an HTTP `traceparent` header (per the [W3C Trace Context proposed specification](https://www.w3.org/TR/trace-context-1)), and the `score.py` code logs the header. The query above shows how to surface this value. You can adapt it to your tracing framework.
  * **Monitoring**: You can use [Azure Monitor for containers](https://docs.microsoft.com/en-us/azure/azure-monitor/insights/container-insights-overview) to monitor the Azure ML scoring containers' performance.

### Clean up the example resources

To remove the resources created for this project, you can use the [/environment_setup/iac-remove-environment-pipeline.yml](../environment_setup/iac-remove-environment-pipeline.yml) definition or you can just delete the resource group in the [Azure Portal](https://portal.azure.com).

## Next Steps: Integrating your project

* Follow the [bootstrap instructions](../bootstrap/README.md) to create a starting point for your project use case. This guide includes information on bringing your own code to this template.
* You may want to use [Azure DevOps self-hosted agents](https://docs.microsoft.com/en-us/azure/devops/pipelines/agents/agents?view=azure-devops&tabs=browser#install) to speed up your ML pipeline execution. The Docker container image for the ML pipeline is sizable, and having it cached on the agent between runs can trim several minutes from your runs.

### Additional Variables and Configuration

#### More variable options

There are more variables used in the project. They're defined in two places: one for local execution and one for using Azure DevOps Pipelines.

For using Azure DevOps Pipelines, all other variables are stored in the file `.pipelines/diabetes_regression-variables-template.yml`. Using the default values as a starting point, adjust the variables to suit your requirements.

In that folder, you'll also find the `config.json` file that we recommend using to provide parameters for training, evaluation, and scoring scripts. The sample parameter that `diabetes_regression`  uses is the ridge regression [*alpha* hyperparameter](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html). We don't provide any serializers for this config file.

#### Local configuration

For instructions on how to set up a local development environment, refer to the [Development environment setup instructions](development_setup.md).
