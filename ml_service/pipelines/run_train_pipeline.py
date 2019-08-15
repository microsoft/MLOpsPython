import sys
import os
import json
import requests
from azureml.core.authentication import AzureCliAuthentication
from azure.common.credentials import ServicePrincipalCredentials


 try:
     with open("train_pipeline.json") as f:
#         train_pipeline_json = json.load(f)
# except Exception:
#     print("No pipeline json found")
#     sys.exit(0)

# experiment_name = os.environ.get("EXPERIMENT_NAME")
# model_name = os.environ.get("MODEL_NAME")

credentials = ServicePrincipalCredentials(
    client_id = '368aaecc-1df8-4132-914c-6c42f8aa0f8b',
    secret = 'e9ToDq-+0add3Oe6O=lwcqo=_Ppy*zim',
    tenant = '72f988bf-86f1-41af-91ab-2d7cd011db47'
)

# cli_auth = AzureCliAuthentication()
# token = cli_auth.get_authentication_header()
token = credentials.token['access_token']
print("token", token)

#rest_endpoint = train_pipeline_json["rest_endpoint"]

response = requests.post(
    rest_endpoint, headers=token,
    json={"ExperimentName": experiment_name,
          "ParameterAssignments": {"model_name": model_name}}
)

run_id = response.json()["Id"]
print("Pipeline run initiated ", run_id)
