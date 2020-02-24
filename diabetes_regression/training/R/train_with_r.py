import subprocess

subprocess.check_call(["bash", "-c", "Rscript r_train.r && ls -ltr model.rds"])
