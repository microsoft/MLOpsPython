## Development environment setup

### Setup

Please be aware that the local environment also needs access to the Azure subscription so you have to have Contributor access on the Azure ML Workspace.

In order to configure the project locally, create a copy of `.env.example` in the root directory and name it `.env`. Fill out all missing values and adjust the existing ones to suit your requirements. 

### Installation

[Install the Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli). The Azure CLI will be used to log you in interactively.

Create a virtual environment using [venv](https://docs.python.org/3/library/venv.html), [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) or [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv). 

Here is an example for setting up and activating a `venv` environment with Python 3:

```
python3 -mvenv .venv
source .venv/bin/activate
```

Install the required Python modules in your virtual environment.

```
pip install -r environment_setup/requirements.txt 
```

### Running local code

To run your local ML pipeline code on Azure ML, run a command such as the following (in bash, all on one line):

```
export BUILD_BUILDID=$(uuidgen); python ml_service/pipelines/build_train_pipeline.py && python ml_service/pipelines/run_train_pipeline.py
```

BUILD_BUILDID is a variable used to uniquely identify the ML pipeline between the
`build_train_pipeline.py` and `run_train_pipeline.py` scripts. In Azure DevOps it is
set to the current build number. In a local environment, we can use a command such as
`uuidgen` so set a different random identifier on each run, ensuring there are 
no collisions.
