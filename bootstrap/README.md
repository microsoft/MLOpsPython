# Bootstrap from MLOpsPython repository

To use this existing project structure and scripts for your new ML project, you can quickly get started from the existing repository,  bootstrap and create a template that works for your ML project. Bootstraping will  prepare a similar directory structure for your project which includes renaming files and folders, deleting and cleaning up some directories and fixing imports and absolute path based on your project name.This will enable reusing various resources like pre-built pipelines and scripts for your new project.

To bootstrap from the existing MLOpsPython repository install and run bootstrap.py script as below
>pip install GitPython==3.0.5

>python bootstrap.py --d [dirpath] --n [projectname]

Where [dirpath] is the directory to download the repo and [projectname] is name of your ML project  
