# Customizing the Azure DevOps job container

The Model training and deployment pipeline uses a Docker container
on the Azure Pipelines agents to provide a reproducible environment
to run test and deployment code.
 The image of the container
`mcr.microsoft.com/mlops/python:latest` is built with this
[Dockerfile](../environment_setup/Dockerfile).

In your project you will want to build your own
Docker image that only contains the dependencies and tools required for your
use case. This image will be more likely smaller and therefore faster, and it
will be totally maintained by your team. 

## Provision an Azure Container Registry 

An Azure Container Registry is deployed along your Azure ML Workspace to manage models.
You can use that registry instance to store your MLOps container image as well, or
provision a separate instance.

## Create a Registry Service Connection

Create a service connection to your Azure Container Registry:
- As *Connection type*, select *Docker Registry*
- As *Registry type*, select *Azure Container Registry*
- As *Azure container registry*, select your Container registry instance.
- As *Service connection name*, enter `acrconnection`.

## Update the environment definition

Modify the [Dockerfile](../environment_setup/Dockerfile) and/or the
[ci_dependencies.yml](../diabetes_regression/ci_dependencies.yml) Conda
environment definition to tailor your environment.

If a package is available in a Conda package repository, then we recommend that
you use the Conda installation rather than the pip installation. Conda packages
typically come with prebuilt binaries that make installation more reliable.

## Create a container build pipeline

In your [Azure DevOps](https://dev.azure.com) project create a new build
pipeline referring to the
[./environment_setup/docker-image-pipeline.yml](environment_setup/docker-image-pipeline.yml)
pipeline definition in your forked repository.

Create a pipeline variable named `agentImageName` and give it an appropriate
value to name your image with, e.g. `mlops/diabetes_regression`.

Save and run the pipeline.

## Modify the model pipeline

Modify the model pipeline file [diabetes_regression-ci-build-train.yml](../.pipelines/diabetes_regression-ci-build-train.yml) by replacing this section:

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

## Dealing with branch concurrency

Especially when working in a team, it's possible that multiple team members

For example, if the master branch is using scikit-learn and Alice creates a branch to use Tensorflow instead, and she removes scikit-learn from the 
[ci_dependencies.yml](../diabetes_regression/ci_dependencies.yml) Conda environment definition
and runs the [docker-image-pipeline.yml](environment_setup/docker-image-pipeline.yml) Docker image, the master branch will stop building.

Alice could leave scikit-learn in addition to Tensorflow in the environment, but that is not ideal, as she would have to take an extra step to remove scikit-learn after merging her branch to master.

A better approach would be for Alice to use a distinct name for her environment, such as mlops/diabetes_regression_tensorflow.
