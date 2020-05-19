# Bootstrap from MLOpsPython repository

To use this existing project structure and scripts for your new ML project, you can quickly get started from the existing repository, bootstrap and create a template that works for your ML project.

Bootstrapping will prepare a directory structure for your project which includes:

* renaming files and folders from the base project name `diabetes_regression` to your project name
* fixing imports and absolute path based on your project name
* deleting and cleaning up some directories

To bootstrap from the existing MLOpsPython repository:

1. Ensure Python 3 is installed locally
1. Clone this repository locally
1. Run bootstrap.py script  
`python bootstrap.py -d [dirpath] -n [projectname]`
    * `[dirpath]` is the absolute path to the root of the directory where MLOpsPython is cloned
    * `[projectname]` is the name of your ML project
