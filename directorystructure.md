# Directory Structure

High level directory structure for this repository:

```bash
├── .pipelines            <- Azure DevOps YAML pipelines for CI, PR and model training and deployment.
├── bootstrap             <- Python script to create a re-usbale code template to bootstrap.
├── charts                <- Helm charts to deploy resources on Azure Kubernetes Service(AKS).
├── data                  <- Initial set of data to train and evaluate model.
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
├── experimentation       <- Jupyter notebooks with ML experimentation code.
├── ml_service            <- The top-level folder for all Azure Machine Learning resources.
│   ├── pipelines         <- Python script that builds Azure Machine Learning pipelines.
│   ├── util              <- Python script for various utility operations specific to Azure Machine Learning.
├── .env.example          <- Example .env file with environment for local development experience.  
├── .gitignore            <- A gitignore file specifies intentionally un-tracked files that Git should ignore.  
├── LICENSE               <- License document for this project.
├── README.md             <- The top-level README for developers using this project.  
```
