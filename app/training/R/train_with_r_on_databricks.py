import os
import argparse

parser = argparse.ArgumentParser("train")
parser.add_argument(
    "--AZUREML_SCRIPT_DIRECTORY_NAME",
    type=str,
    help="folder",
)

args, unknown = parser.parse_known_args()
folder = args.AZUREML_SCRIPT_DIRECTORY_NAME

os.system("cd " + "/dbfs/" + folder
          + " && Rscript r_train.r && ls -ltr model.rds")
