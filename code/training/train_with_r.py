import os

os.system("Rscript r_train.r")
os.system("ls -ltr")
os.system("pwd")
os.system("env")
os.system("ls -ltr /local_disk0")
os.system("ls -ltr /local_disk0/tmp")
os.system("ls -ltr /databricks")
os.system("ls -ltr /databricks/spark")
os.system("ls -ltr /databricks/spark/scripts")
os.system("ls -ltr /databricks/spark/python")
os.system("whereis train_with_r.py")
os.system("ls -ltr dbfs/143eb546-b32d-4e42-8194-f43c9d9f9e5f")