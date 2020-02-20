# Bootstrap from MLOpsPython repository

To use this existing project structure and scripts for your new ML project, you can quickly get started from the existing repository, bootstrap and create a template that works for your ML project. Bootstrapping will prepare a similar directory structure for your project which includes renaming files and folders, deleting and cleaning up some directories and fixing imports and absolute path based on your project name. This will enable reusing various resources like pre-built pipelines and scripts for your new project. 

To bootstrap from the existing MLOpsPython repository clone this repository, ensure Python is installed locally, and run bootstrap.py script as below

`python bootstrap.py --d [dirpath] --n [projectname]`

Where `[dirpath]` is the absolute path to the root of your directory where MLOps repo is cloned and `[projectname]` is the name of your ML project.

The script renames folders, files and files' content from the base project name `diabetes` to your project name. However, you might need to manually rename variables defined in a variable group and their values. 

[This article](https://docs.microsoft.com/azure/machine-learning/tutorial-convert-ml-experiment-to-production#use-your-own-model-with-mlopspython-code-template) will also assist to use this code template for your own ML project.
