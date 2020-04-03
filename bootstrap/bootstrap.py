import os
import sys
import platform
import argparse
import re


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

    def rename_files(self):
        # Rename all files starting with diabetes_regression with project name
        strtoreplace = "diabetes_regression"
        dirs = [".pipelines", r"ml_service/pipelines"]
        for dir in dirs:
            normDir = os.path.normpath(dir)
            dirpath = os.path.join(self._project_directory, normDir)
            for filename in os.listdir(dirpath):
                if(filename.find(strtoreplace) != -1):
                    src = os.path.join(self._project_directory, normDir, filename)  # NOQA: E501
                    dst = os.path.join(self._project_directory,
                                       normDir,
                                       filename.replace(strtoreplace, self._project_name, 1))  # NOQA: E501
                    os.rename(src, dst)

    def rename_dir(self):
        dir = "diabetes_regression"
        src = os.path.join(self._project_directory, dir)
        for path, subdirs, files in os.walk(src):
            for name in files:
                newPath = path.replace(dir, self._project_name)
                if (not (os.path.exists(newPath))):
                    os.mkdir(newPath)
                file_path = os.path.join(path, name)
                new_name = os.path.join(newPath, name)
                os.rename(file_path, new_name)

    def delete_dir(self):
        # Delete unwanted directories
        dirs = ["docs", r"diabetes_regression"]
        if (platform.system() == "Windows"):
            cmd = 'rmdir /S /Q "{}"'
        else:
            cmd = 'rm -r "{}"'
        for dir in dirs:
            os.system(cmd.format(os.path.join(self._project_directory, os.path.normpath(dir))))  # NOQA: E501

    def clean_dir(self):
        # Clean up directories
        dirs = ["data", "experimentation"]
        for dir in dirs:
            for root, dirs, files in os.walk(os.path.join(self._project_directory, dir)):  # NOQA: E501
                for file in files:
                    os.remove(os.path.join(root, file))

    def validate_args(self):
        # Validate arguments
        if (os.path.isdir(self._project_directory) is False):
            raise Exception("Not a valid directory. Please provide an absolute directory path.")  # NOQA: E501
        if (len(self._project_name) < 3 or len(self._project_name) > 15):
            raise Exception("Invalid project name length. Project name should be 3 to 15 chars long, letters and underscores only.")  # NOQA: E501
        if (not re.search("^[\\w_]+$", self._project_name)):
            raise Exception("Invalid characters in project name. Project name should be 3 to 15 chars long, letters and underscores only.")  # NOQA: E501


def replace_project_name(project_dir, project_name, rename_name):
    # Replace instances of rename_name within files with project_name
    files = [r".env.example",
            r".pipelines/code-quality-template.yml",
            r".pipelines/pr.yml",
            r".pipelines/diabetes_regression-ci.yml",
            r".pipelines/abtest.yml",
            r".pipelines/diabetes_regression-ci-image.yml",
            r".pipelines/diabetes_regression-get-model-version-template.yml",  # NOQA: E501
            r".pipelines/diabetes_regression-variables-template.yml",
            r"environment_setup/Dockerfile",
            r"environment_setup/install_requirements.sh",
            r"ml_service/pipelines/diabetes_regression_build_train_pipeline_with_r_on_dbricks.py",  # NOQA: E501
            r"ml_service/pipelines/diabetes_regression_build_train_pipeline_with_r.py",  # NOQA: E501
            r"ml_service/pipelines/diabetes_regression_build_train_pipeline.py",  # NOQA: E501
            r"ml_service/pipelines/diabetes_regression_verify_train_pipeline.py",  # NOQA: E501
            r"ml_service/util/create_scoring_image.py",
            r"diabetes_regression/conda_dependencies.yml",
            r"diabetes_regression/evaluate/evaluate_model.py",
            r"diabetes_regression/register/register_model.py",
            r"diabetes_regression/training/test_train.py"]

    for file in files:
        path = os.path.join(project_dir, os.path.normpath(file))
        try:
            with open(path, "rt", encoding="utf8") as f_in:
                data = f_in.read()
            data = data.replace(rename_name, project_name)
            with open(os.path.join(project_dir, file), "wt", encoding="utf8") as f_out:  # NOQA: E501
                f_out.write(data)
        except IOError as e:
            print("Could not modify \"%s\". Is the MLOpsPython repo already cloned at \"%s\"?" % (path, project_dir))  # NOQA: E501
            raise e


def main(args):
    parser = argparse.ArgumentParser(description='New Template')
    parser.add_argument("-d",
                        "--directory",
                        type=str,
                        required=True,
                        help="Absolute path to new project direcory")
    parser.add_argument("-n",
                        "--name",
                        type=str,
                        required=True,
                        help="Name of the project [3-15 chars, letters and underscores only]")  # NOQA: E501
    try:
        args = parser.parse_args()

        project_directory = args.directory
        project_name = args.name

        helper = Helper(project_directory, project_name)
        helper.validate_args()
        helper.clean_dir()

        replace_project_name(project_directory, project_name, "diabetes_regression")  # NOQA: E501
        replace_project_name(project_directory, project_name, "diabetes")

        helper.rename_files()
        helper.rename_dir()
        helper.delete_dir()
    except Exception as e:
        print(e)

    return 0


if '__main__' == __name__:
    sys.exit(main(sys.argv))
