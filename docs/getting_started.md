## Getting Started with this Repo

### 1. Get the source code
- Either clone the repository to your workspace and create your own repo with the code in GitHub.
- An easier way is to just fork the project, so you have the repoitory under your username on GitHub itslef.


### 2. Create Azure DevOps account
We use Azure DevOps for running our build(CI), retraining trigger and release (CD) pipelines. If you don't already have Azure DevOps account, create one by following the instructions [here](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/create-organization?view=azure-devops)

If you already have Azure DevOps account, create a new project.

**Note:** Make sure you have the right permissions in Azure DevOps to do so.

### 3. Create Service Principal to Login to Azure and create resources

To create service principal, register an application entity in Azure Active Directory (Azure AD) and grant it the Contributor or Owner role of the subscription or the resource group where the web service belongs to. See [how to create service principal](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal) and assign permissions to manage Azure resource

**Note:** You must have sufficient permissions to register an application with your Azure AD tenant, and assign the application to a role in your Azure subscription. Contact your subscription adminstator if you don't have the permissions. Normally a subscription admin will create a Service principal and will provide you the details.




