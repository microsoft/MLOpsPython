import sys
import os
import json
import requests
from azureml.core.authentication import AzureCliAuthentication
# from azure.common.credentials import ServicePrincipalCredentials


try:
    with open("train_pipeline.json") as f:
        train_pipeline_json = json.load(f)
except Exception:
    print("No pipeline json found")
    sys.exit(0)

experiment_name = os.environ.get("EXPERIMENT_NAME")
model_name = os.environ.get("MODEL_NAME")

# credentials = ServicePrincipalCredentials(
#     client_id = $(SP_APP_ID),
#     secret = KEY,
#     tenant = TENANT_ID
# )
cli_auth = AzureCliAuthentication()
token = cli_auth.get_authentication_header()

rest_endpoint = train_pipeline_json["rest_endpoint"]
print("rest_endpoint ", rest_endpoint)

response = requests.post(
    rest_endpoint, headers=token,
    json={"ExperimentName": experiment_name,
          "ParameterAssignments": {"model_name": model_name}}
)

print("response ", response)
run_id = response.json()["Id"]
print("Pipeline run initiated ", run_id)
