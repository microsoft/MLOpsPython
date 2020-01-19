FROM conda/miniconda3

LABEL org.label-schema.vendor = "Microsoft" \
      org.label-schema.url = "https://hub.docker.com/r/microsoft/mlopspython" \
      org.label-schema.vcs-url = "https://github.com/microsoft/MLOpsPython"

RUN apt-get update && apt-get install -y \
    gcc


# Install Python modules
COPY requirements.txt  /setup/
RUN pip install --upgrade -r /setup/requirements.txt
