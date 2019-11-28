# Getting Started with this Repo

## Clone or fork this repository

## Create an Azure DevOps account

We use Azure DevOps for running our build(CI), retraining trigger and release
(CD) pipelines. If you don't already have an Azure DevOps account, create one by
following the instructions [here](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/create-organization?view=azure-devops).

If you already have Azure DevOps account, create a [new project](https://docs.microsoft.com/en-us/azure/devops/organizations/projects/create-project?view=azure-devops).

## Create an ARM Service Connection to deploy resources

The repository includes a DevOps pipeline to deploy the Azure ML workspace and associated resources through Azure Resource Manager.

The pipeline requires an **Azure Resource Manager**
[service connection](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml#create-a-service-connection).
Given this service connection, you will be able to run the IaC pipeline
and have the required permissions to generate resources.

![create service connection](./images/create-rm-service-connection.png)

Use **``AzureResourceConnection``** as the connection name, since it is used
in the IaC pipeline definition. Leave the **``Resource Group``** field empty.

**Note:** Creating the ARM service connection scope requires 'Owner' or 'User Access Administrator' permissions on the subscription.
You must also have sufficient permissions to register an application with
your Azure AD tenant, or receive the ID and secret of a service principal
from your Azure AD Administrator. That principal must have 'Contributor'
permissions on the subscription.

## Create a Variable Group for your Pipelines

We make use of variable group inside Azure DevOps to store variables and their
values that we want to make available across multiple pipelines. You can either
store the values directly in [Azure DevOps](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=designer#create-a-variable-group)
or connect to an Azure Key Vault in your subscription. Please refer to the
documentation [here](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=designer#create-a-variable-group) to
learn more about how to create a variable group and
[link](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=designer#use-a-variable-group) it to your pipeline.
Click on **Library** in the **Pipelines** section as indicated below:

![library_variable groups](./images/library_variable_groups.png)

Please name your variable group **``devopsforai-aml-vg``** as we are using this
name within our build yaml file.

The variable group should contain the following required variables:

| Variable Name               | Suggested Value                    |
| --------------------------- | -----------------------------------|
| BASE_NAME                   | [unique base name]                 |
| LOCATION                    | centralus                          |
| RESOURCE_GROUP              |                                    |
| WORKSPACE_NAME              | mlops-AML-WS                       |
| WORKSPACE_SVC_CONNECTION    | aml-workspace-connection           | 

**Note:** 

The **WORKSPACE_NAME** parameter is used for the Azure Machine Learning Workspace creation. You can provide here an existing AML Workspace if you have one.

The **BASE_NAME** parameter is used throughout the solution for naming
Azure resources. When the solution is used in a shared subscription, there can
be naming collisions with resources that require unique names like azure blob
storage and registry DNS naming. Make sure to give a unique value to the
BASE_NAME variable (e.g. MyUniqueML), so that the created resources will have
unique names (e.g. MyUniqueML-AML-RG, MyUniqueML-AML-KV, etc.). The length of
the BASE_NAME value should not exceed 10 characters. 

Make sure to select the **Allow access to all pipelines** checkbox in the
variable group configuration.

## More variable options

There are more variables used in the project. They're defined in two places one for local execution one for using Azure DevOps Pipelines

### Local configuration

In order to configure the project locally you have to create a copy from `.env.example` to the root and name it `.env`. Fill out all missing values and adjust the existing ones to your needs. 

For local development, you will also need to [install the Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli). Azure CLI will be used to log you in interactively.
Please be aware that the local environment also needs access to the Azure subscription so you have to have Contributor access on the Azure ML Workspace.

### Azure DevOps configuration

For using Azure DevOps Pipelines all other variables are stored in the file `.pipelines/azdo-variables.yml`. Adjust as needed the variables, also the defaults will give you an easy jump start.

Up until now you should have:

* Forked (or cloned) the repo
* Created a devops account or use an existing one
* A variable group with all configuration values

## Create Resources with Azure Pipelines

The easiest way to create all required resources (Resource Group, ML Workspace,
Container Registry, Storage Account, etc.) is to leverage an
"Infrastructure as Code" [pipeline in this repository](../environment_setup/iac-create-environment.yml). This **IaC** pipeline takes care of setting up
all required resources based on these [ARM templates](../environment_setup/arm-templates/cloud-environment.json).

To set up this pipeline, you will need to do the following steps:

1. Create an Azure Resource Manager Service Connection
1. Create a Build IaC Pipeline

### Create a Build IaC Pipeline

In your DevOps project, create a build pipeline from your forked **GitHub**
repository:

![build connnect step](./images/build-connect.png)

Then, refer to an **Existing Azure Pipelines YAML file**:

![configure step](./images/select-iac-pipeline.png)

Having done that, run the pipeline:

![iac run](./images/run-iac-pipeline.png)

Check out created resources in the [Azure Portal](portal.azure.com):

![created resources](./images/created-resources.png)

Alternatively, you can also use a [cleaning pipeline](../environment_setup/iac-remove-environment.yml) that removes resources created for this project or
you can just delete a resource group in the [Azure Portal](portal.azure.com).

## Create an Azure DevOps Azure ML Workspace Service Connection
Install the **Azure Machine Learning** extension to your organization from the
[marketplace](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.vss-services-azureml),
so that you can set up a service connection to your AML workspace.

Create a service connection to your ML workspace via the [Azure DevOps Azure ML task instructions](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.vss-services-azureml) to be able to execute the Azure ML training pipeline. The connection name specified here needs to be used for the value of the `WORKSPACE_SVC_CONNECTION` set in the variable group below.

**Note:** Creating service connection with Azure Machine Learning workspace scope requires 'Owner' or 'User Access Administrator' permissions on the Workspace.
You must also have sufficient permissions to register an application with
your Azure AD tenant, or receive the ID and secret of a service principal
from your Azure AD Administrator. That principal must have Contributor
permissions on the Azure ML Workspace.

## Set up Build, Release Trigger, and Release Deployment Pipelines

Now that you have all the required resources created from the IaC pipeline,
you can set up the rest of the pipelines necessary for deploying your ML model
to production. These are the pipelines that you will be setting up:

1. **Build pipeline:** triggered on code change to master branch on GitHub,
performs linting, unit testing, publishing a training pipeline, and runs the published training pipeline to train, evaluate, and register a model.
1. **Release Deployment pipeline:** deploys a model to QA (ACI) and Prod (AKS)
environments.

### Set up a Build Training Pipeline

In your [Azure DevOps](https://dev.azure.com) project create and run a new build
pipeline referring to the [azdo-ci-build-train.yml](../.pipelines/azdo-ci-build-train.yml)
pipeline in your forked **GitHub** repository:

![configure ci build pipeline](./images/ci-build-pipeline-configure.png)

Name the pipeline **ci-build**. Once the pipline is finished, explore the
execution logs:

![ci build logs](./images/ci-build-logs.png)

and checkout a published training pipeline in the **mlops-AML-WS** workspace in
[Azure Portal](https://ms.portal.azure.com/):

![training pipeline](./images/training-pipeline.png)

Great, you now have the build pipeline set up which automatically triggers every time there's a change in the master
branch. The pipeline performs linting, unit testing, builds and publishes and executes a 
**ML Training Pipeline** in a **ML Workspace**.

**Note:** The build pipeline contains disabled steps to build and publish ML
pipelines using R to train a model. Enable these steps if you want to play with
this approach by changing the `build-train-script` pipeline variable to either `build_train_pipeline_with_r.py`, or `build_train_pipeline_with_r_on_dbricks.py`. For the pipeline training a model with R on Databricks you have
to manually create a Databricks cluster and attach it to the ML Workspace as a
compute (Values DB_CLUSTER_ID and DATABRICKS_COMPUTE_NAME variables shoud be
specified).

![running training pipeline](./images/running-training-pipeline.png)

The training pipeline will train, evaluate, and register a new model. Wait until
it is finished and make sure there is a new model in the **ML Workspace**:

![trained model](./images/trained-model.png)

To disable the automatic trigger of the training pipeline, change the `auto-trigger-training` variable as listed in the `.pipelines\azdo-ci-build-train.yml` pipeline to `false`.  This can also be overridden at runtime execution of the pipeline.

### Set up a Release Deployment Pipeline to Deploy the Model

The final step is to deploy the model across environments with a release
pipeline. There will be a **``QA``** environment running on
[Azure Container Instances](https://azure.microsoft.com/en-us/services/container-instances/)
and a **``Prod``** environment running on
[Azure Kubernetes Service](https://azure.microsoft.com/en-us/services/kubernetes-service).
This is the final picture of what your release pipeline should look like:

![deploy model](./images/deploy-model.png)

The pipeline consumes two artifacts:

1. the result of the **Build Pipeline** as it contains configuration files
1. the **model** trained and registered by the ML training pipeline

Add an artifact to the pipeline and select **AzureML Model Artifact** source
type. Select the **Service Endpoint** and **Model Names** from the drop down
lists. **Service Endpoint** refers to the **Service connection** created in
the previous step:

![model artifact](./images/model-artifact.png)

Go to the new **Releases Pipelines** section, and click new to create a new
release pipeline. A first stage is automatically created and choose
**start with an Empty job**. Name the stage **QA (ACI)** and add a single task
to the job **Azure ML Model Deploy**. Make sure that the Agent Specification
is ubuntu-16.04 under the Agent Job:

![deploy aci](./images/deploy-aci.png)

Specify task parameters as it is shown in the table below:

| Parameter                     | Value                                                                                                |
| ----------------------------- | ---------------------------------------------------------------------------------------------------- |
| Display Name                  | Azure ML Model Deploy                                                                                |
| Azure ML Workspace            | mlops-AML-WS                                                                                         |
| Inference config Path         | `$(System.DefaultWorkingDirectory)/_ci-build/mlops-pipelines/code/scoring/inference_config.yml`<br>_(The `_ci-build` part of the path is the source alias of your CI artifact)_ |
| Model Deployment Target       | Azure Container Instance                                                                             |
| Deployment Name               | mlopspython-aci                                                                                      |
| Deployment Configuration file | `$(System.DefaultWorkingDirectory)/_ci-build/mlops-pipelines/code/scoring/deployment_config_aci.yml`<br>_(The `_ci-build` part of the path is the source alias of your CI artifact)_ |
| Overwrite existing deployment | X                                                                                                    |

In a similar way, create a stage **Prod (AKS)** and add a single task to the job
**Azure ML Model Deploy**. Make sure that the Agent Specification is
ubuntu-16.04 under the Agent Job:

![deploy aks](./images/deploy-aks.png)

Specify task parameters as it is shown in the table below:

| Parameter                         | Value                                                                                                |
| --------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Display Name                      | Azure ML Model Deploy                                                                                |
| Azure ML Workspace                | mlops-AML-WS                                                                                         |
| Inference config Path             | `$(System.DefaultWorkingDirectory)/_ci-build/mlops-pipelines/code/scoring/inference_config.yml`<br>_(The `_ci-build` part of the path is the source alias of your CI artifact)_ |
| Model Deployment Target           | Azure Kubernetes Service                                                                             |
| Select AKS Cluster for Deployment | YOUR_DEPLOYMENT_K8S_CLUSTER                                                                          |
| Deployment Name                   | mlopspython-aks                                                                                      |
| Deployment Configuration file     | `$(System.DefaultWorkingDirectory)/_ci-build/mlops-pipelines/code/scoring/deployment_config_aks.yml`<br>_(The `_ci-build` part of the path is the source alias of your CI artifact)_ |
| Overwrite existing deployment     | X                                                                                                    |

**Note:** Creating of a Kubernetes cluster on AKS is out of scope of this
tutorial, but you can find set up information in the docs
[here](https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough-portal#create-an-aks-cluster).

Similarly to the **Invoke Training Pipeline** release pipeline, previously
created, in order to trigger a coutinuous integration, click on the lightning
bolt icon, make sure the **Continuous deployment trigger** is checked and
save the trigger:

![Automate Deploy Model Pipeline](./images/automate_deploy_model_pipeline.png)

Congratulations! You have three pipelines set up end to end:

* **Build pipeline:** triggered on code change to master branch on GitHub,
performs linting, unit testing and publishing a training pipeline.
* **Release Trigger pipeline:** runs a published training pipeline to train,
evaluate and register a model.
* **Release Deployment pipeline:** deploys a model to QA (ACI) and Prod (AKS)
environments.

## Deploy the trained model to Azure Web App for containers

Note: This is an optional step and can be used only if you are deploying your
scoring service on Azure Web Apps.

[Create Image Script](../ml_service/util/create_scoring_image.py)
can be used to create a scoring image from the release pipeline. The image
created by this script will be registered under Azure Container Registry (ACR)
instance that belongs to Azure Machine Learning Service. Any dependencies that
scoring file depends on can also be packaged with the container with Image
config. To learn more on how to create a container with AML SDK click
[here](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.image.image.image?view=azure-ml-py#create-workspace--name--models--image-config-).

Below is release pipeline with two tasks one to create an image using the above
script and second is the deploy the image to Web App for containers.

![release_webapp](./images/release-webapp-pipeline.PNG)

In the Variables tab, link the pipeline to your variable group (`devopsforai-aml-vg`). In the variable group definition, add the following variables:

| Variable Name               | Suggested Value                    |
| --------------------------- | -----------------------------------|
| MODEL_NAME                  | sklearn_regression_model.pkl       |
| IMAGE_NAME                  | diabetes                           |

Add as an artifact to the pipeline the result of the **Build Pipeline** as it contains the necessary scripts.

Use an Agent of type `ubuntu-16.04`.

For the Azure CLI task to invoke the [Create Image Script](../ml_service/util/create_scoring_image.py), specify the following task parameters:

| Parameter          | Value                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------- |
| Display name       | Create Scoring Image                                                                                |
| Azure subscription | aml-workspace-connection                                                                            |
| Script Path        | `$(System.DefaultWorkingDirectory)/_ci-build/mlops-pipeline/ml_service/util/create_scoring_image.sh`<br>_(The `_ci-build` part of the path is the source alias of your CI artifact)_ |
| Working directory  | `$(System.DefaultWorkingDirectory)/_ci-build/mlops-pipelines`<br>_(The `_ci-build` part of the path is the source alias of your CI artifact)_ |

![release_createimage](./images/release-task-createimage.PNG)

Finally, for the Azure Web App for Containers Task, specify the following task
parameters as it is shown in the table below:

| Parameter          | Value                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------- |
| Azure subscription | Subscription used to deploy Web App                                                                 |
| App name           | Web App for Containers name                                                                         |
| Image name         | Specify the fully qualified container image name. For example, 'myregistry.azurecr.io/nginx:latest' |

![release_webapp](./images/release-task-webappdeploy.PNG)

Save the pipeline and create a release to trigger it manually. To create the
trigger, click on the "Create release" button on the top right of your screen,
leave the fields blank and click on **Create** at the bottom of the screen.
Once the pipeline execution is finished, check out deployments in the
**mlops-AML-WS** workspace.
