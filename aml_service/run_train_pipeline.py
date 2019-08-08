import sys, os, json, requests
from azureml.core.authentication import AzureCliAuthentication


try:
    with open("train_pipeline.json") as f:
        train_pipeline_json = json.load(f)
except:
    print("No pipeline json found")
    sys.exit(0)

experiment_name = os.environ.get("EXPERIMENT_NAME") 
model_name = os.environ.get("MODEL_NAME")

cli_auth = AzureCliAuthentication()
token = cli_auth.get_authentication_header()

rest_endpoint = train_pipeline_json["rest_endpoint"]

response = requests.post(
    rest_endpoint, headers=token, 
    json={"ExperimentName": experiment_name,
    "ParameterAssignments": {"model_name":model_name}}
)

run_id = response.json()["Id"]
print("Pipeline run initiated ", run_id)
