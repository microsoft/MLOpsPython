import os
import sys
import argparse
# from git import Repo


class Helper:

    def __init__(self, project_directory, project_name):
        self._project_directory = project_directory
        self._project_name = project_name
        self._git_repo = "https://github.com/microsoft/MLOpsPython.git"

    @property
    def project_directory(self):
        return self._project_directory

    @property
    def project_name(self):
        return self._project_name

    @property
    def git_repo(self):
        return self._git_repo

    def clonerepo(self):
        # Download MLOpsPython repo from git
        Repo.clone_from(
            self._git_repo, self._project_directory, branch="master", depth=1)
        print(self._project_directory)

    def renamefiles(self):
        # Rename all files starting with diabetes_regression with project name
        strtoreplace = "diabetes_regression"
        dirs = [".pipelines", r"ml_service\pipelines"]
        for dir in dirs:
            dirpath = os.path.join(self._project_directory, dir)
            for filename in os.listdir(dirpath):
                if(filename.find(strtoreplace) != -1):
                    src = os.path.join(self._project_directory, dir, filename)
                    dst = os.path.join(self._project_directory,
                                       dir, filename.replace(strtoreplace, self._project_name, 1))  # NOQA: E501
                    os.rename(src, dst)

    def renamedir(self):
        # Rename any directory with diabetes_regression with project name
        dirs = ["diabetes_regression"]
        for dir in dirs:
            src = os.path.join(self._project_directory, dir)
            dst = os.path.join(self._project_directory, self._project_name)
            os.rename(src, dst)

    def deletedir(self):
        # Delete unwanted directories
        dirs = ["docs", r"diabetes_regression\training\R"]
        for dir in dirs:
            os.system(
                'rmdir /S /Q "{}"'.format(os.path.join(self._project_directory, dir)))  # NOQA: E501

    def replaceimport(self):
        # Replace imports with new project name
        dirs = [r"diabetes_regression\training\test_train.py",
                r"ml_service\pipelines\diabetes_regression_verify_train_pipeline.py"]  # NOQA: E501
        for file in dirs:
            fin = open(os.path.join(self._project_directory, file), "rt")
            data = fin.read()
            newimport = "from " + self._project_name + "."
            data = data.replace("from diabetes_regression.", newimport)
            fin.close()
            fin = open(os.path.join(self._project_directory, file), "wt")
            fin.write(data)
            fin.close()

    def replaceprojectinstances(self):
        # Replace imports with new project name
        dirs = [r".env.example",
                r".pipelines\azdo-base-pipeline.yml",
                r".pipelines\azdo-pr-build-train.yml",
                r".pipelines\test-ci-build-train.yml",
                r".pipelines\test-ci-image.yml",
                r".pipelines\test-template-get-model-version.yml",
                r".pipelines\test-variables.yml",
                r"environment_setup\Dockerfile",
                r"environment_setup\install_requirements.sh",
                r"ml_service\pipelines\test_build_train_pipeline_with_r_on_dbricks.py",
                r"ml_service\pipelines\test_build_train_pipeline_with_r.py",
                r"ml_service\pipelines\test_build_train_pipeline.py",
                r"ml_service\pipelines\test_verify_train_pipeline.py",
                r"ml_service\util\create_scoring_image.py",
                r"test\azureml_environment.json",
                r"test\conda_dependencies.yml",
                r"test\evaluate\evaluate_model.py"]  # NOQA: E501

        for file in dirs:
            fin = open(os.path.join(self._project_directory, file), "rt")
            data = fin.read()
            data = data.replace("diabetes_regression", self.project_name)
            fin.close()
            fin = open(os.path.join(self._project_directory, file), "wt")
            fin.write(data)
            fin.close()

    def cleandir(self):
        # Clean up directories
        dirs = ["data", "experimentation"]
        for dir in dirs:
            for root, dirs, files in os.walk(os.path.join(self._project_directory, dir)):  # NOQA: E501
                for file in files:
                    os.remove(os.path.join(root, file))

    def validateargs(self):
        # Validate arguments
        if (os.path.isdir(self._project_directory) is False):
            raise Exception(
                "Not a valid directory. Please provide absolute directory path")  # NOQA: E501
        # if (len(os.listdir(self._project_directory)) > 0):
        #     raise Exception("Directory not empty. PLease empty directory")
        if(len(self._project_name) < 3 or len(self._project_name) > 15):
            raise Exception("Project name should be 3 to 15 chars long")


def main(args):
    # Run this script to create a template from mlopspython
    #  python bootstrap.py --d [dirpath] --n [projectname]
    parser = argparse.ArgumentParser(description='New Template')
    parser.add_argument("--d", type=str,
                        help="Absolute path to new project direcory")
    parser.add_argument(
        "--n", type=str, help="Name of the project[3-15 chars] ")
    try:
        args = parser.parse_args()
        project_directory = args.d
        project_name = args.n
        helper = Helper(project_directory, project_name)
        helper.validateargs()
        # helper.clonerepo()
        helper.cleandir()
        # helper.replaceimport()
        helper.replaceprojectinstances)
        helper.deletedir()
        helper.renamefiles()
        helper.renamedir()
    except Exception as e:
        print(e)
    return 0


if '__main__' == __name__:
    sys.exit(main(sys.argv))
