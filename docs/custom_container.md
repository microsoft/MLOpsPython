# Customizing the Azure DevOps job container

The Model training and deployment pipeline uses a Docker container
on the Azure Pipelines agents to provide a reproducible environment
to run test and deployment code.
 The image of the container
`mcr.microsoft.com/mlops/python:latest` is built with this
[Dockerfile](../environment_setup/Dockerfile).

Additionally mcr.microsoft.com/mlops/python image is also tagged with below tags.

| Image Tags                                      | Description                                                                               |
| ----------------------------------------------- | :---------------------------------------------------------------------------------------- |
| mcr.microsoft.com/mlops/python:latest           | latest image                                                                              |
| mcr.microsoft.com/mlops/python:build-[id]       | where [id] is Azure Devops build id e.g.  mcr.microsoft.com/mlops/python:build-20200325.1 |
| mcr.microsoft.com/mlops/python:amlsdk-[version] | where [version] is aml sdk version e.g.  mcr.microsoft.com/mlops/python:amlsdk-1.1.5.1    |
| mcr.microsoft.com/mlops/python:release-[id]     | where [id] is github release id e.g.  mcr.microsoft.com/mlops/python:release-3.0.0        |  |

In your project you will want to build your own
Docker image that only contains the dependencies and tools required for your
use case. This image will be more likely smaller and therefore faster, and it
will be totally maintained by your team.

## Provision an Azure Container Registry

An Azure Container Registry is deployed along your Azure ML Workspace to manage models.
You can use that registry instance to store your MLOps container image as well, or
provision a separate instance.

## Create a Registry Service Connection

[Create a service connection](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml#sep-docreg) to your Azure Container Registry:

- As *Connection type*, select *Docker Registry*
- As *Registry type*, select *Azure Container Registry*
- As *Azure container registry*, select your Container registry instance
- As *Service connection name*, enter `acrconnection`

## Update the environment definition

Modify the [Dockerfile](../environment_setup/Dockerfile) and/or the
[ci_dependencies.yml](../diabetes_regression/ci_dependencies.yml) CI Conda
environment definition to tailor your environment.
Conda provides a [reusable environment for training and deployment with Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-environments).
The Conda environment used for CI should use the same package versions as the Conda environment
used for the Azure ML training and scoring environments (defined in [conda_dependencies.yml](../diabetes_regression/conda_dependencies.yml)).
This enables you to run unit and integration tests using the exact same dependencies as used in the ML pipeline.

If a package is available in a Conda package repository, then we recommend that
you use the Conda installation rather than the pip installation. Conda packages
typically come with prebuilt binaries that make installation more reliable.

## Create a container build pipeline

In your [Azure DevOps](https://dev.azure.com) project create a new build
pipeline referring to the
[environment_setup/docker-image-pipeline.yml](../environment_setup/docker-image-pipeline.yml)
pipeline definition in your forked repository.

Edit the [environment_setup/docker-image-pipeline.yml](../environment_setup/docker-image-pipeline.yml) file
and modify the string `'public/mlops/python'` with an name suitable to describe your environment,
e.g. `'mlops/diabetes_regression'`.

Save and run the pipeline. This will build and push a container image to your Azure Container Registry with
the name you have just edited. The next step is to modify the build pipeline to run the CI job on a container
run from that image.

## Modify the model pipeline

Modify the model pipeline file [diabetes_regression-ci.yml](../.pipelines/diabetes_regression-ci.yml) by replacing this section:

```
resources:
  containers:
  - container: mlops
    image: mcr.microsoft.com/mlops/python:latest
```

with (using the image name previously defined):

```
resources:
  containers:
  - container: mlops
    image: mlops/diabetes_regression
    endpoint: acrconnection
```

Run the pipeline and ensure your container has been used.

## Addressing conflicting dependencies

Especially when working in a team, it's possible for environment changes across branches to interfere with one another.

For example, if the master branch is using scikit-learn and you create a branch to use Tensorflow instead, and you
decide to remove scikit-learn from the
[ci_dependencies.yml](../diabetes_regression/ci_dependencies.yml) Conda environment definition
and run the [docker-image-pipeline.yml](../environment_setup/docker-image-pipeline.yml) Docker image,
then the master branch will stop building.

You could leave scikit-learn in addition to Tensorflow in the environment, but that is not ideal, as you would have to take an extra step to remove scikit-learn after merging your branch to master.

A better approach would be to use a distinct name for your modified environment, such as `mlops/diabetes_regression/tensorflow`.
By changing the name of the image in your branch in both the container build pipeline
[environment_setup/docker-image-pipeline.yml](../environment_setup/docker-image-pipeline.yml)
and the model pipeline file
[diabetes_regression-ci.yml](../.pipelines/diabetes_regression-ci.yml),
and running both pipelines in sequence on your branch,
you avoid any branch conflicts, and the name does not have to be changed after merging to master.
