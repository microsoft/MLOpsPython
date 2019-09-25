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

#os.system("Rscript "+"dbfs:/"+folder+"/r_train.r")
os.system("ls -ltr "+"dbfs:/"+folder)
# os.system("pwd")
# os.system("env")
# os.system("ls -ltr /local_disk0")
# os.system("ls -ltr /local_disk0/tmp")
# os.system("ls -ltr /databricks")
# os.system("ls -ltr /databricks/spark")
# os.system("ls -ltr /databricks/spark/scripts")
# os.system("ls -ltr /databricks/spark/python")


