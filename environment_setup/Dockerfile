FROM conda/miniconda3

COPY . /setup

RUN ["apt", "update"]
RUN apt install gcc -y && pip install -r /setup/requirements.txt
RUN pip install azure-cli==2.0.65 && pip install --upgrade azureml-sdk[cli]