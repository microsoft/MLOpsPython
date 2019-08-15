import sys
import os
import json
import requests
from azure.common.credentials import ServicePrincipalCredentials


tenant_id = os.environ.get("TENANT_ID")
app_id = os.environ.get("SP_APP_ID")
app_secret = os.environ.get("SP_APP_SECRET")

try:
    with open("train_pipeline.json") as f:
        train_pipeline_json = json.load(f)
except Exception:
    print("No pipeline json found")
    sys.exit(0)

experiment_name = os.environ.get("EXPERIMENT_NAME")
model_name = os.environ.get("MODEL_NAME")

credentials = ServicePrincipalCredentials(
    client_id=app_id,
    secret=app_secret,
    tenant=tenant_id
)

token = credentials.token['access_token']
print("token", token)
auth_header = {"Authorization": "Bearer " + token}

rest_endpoint = train_pipeline_json["rest_endpoint"]

response = requests.post(
    rest_endpoint, headers=auth_header,
    json={"ExperimentName": experiment_name,
          "ParameterAssignments": {"model_name": model_name}}
)

run_id = response.json()["Id"]
print("Pipeline run initiated ", run_id)
