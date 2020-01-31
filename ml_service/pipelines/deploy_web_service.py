import argparse
import os
from azureml.core import Workspace
from azureml.core.webservice import AciWebservice, AksWebservice
from azureml.core.model import InferenceConfig, Model
from ml_service.util.env_variables import Env
from ml_service.util.manage_environment import get_environment


def main():
    parser = argparse.ArgumentParser("deploy_web_service.py")

    parser.add_argument(
        "--type",
        type=str,
        choices=["AKS", "ACI"],
        required=True,
        help="type of service"
    )
    parser.add_argument(
        "--service",
        type=str,
        required=True,
        help="Name of the service to deploy"
    )
    parser.add_argument(
        "--compute_target",
        type=str,
        help="Name of the compute target. Only applicable if type = AKS"
    )
    args = parser.parse_args()

    if args.type == "AKS" and args.compute_target is None:
        raise ValueError("--compute_target is required")

    e = Env()
    # Get Azure machine learning workspace
    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group
    )
    print("get_workspace:")
    print(aml_workspace)

    # Create a reusable scoring environment
    environment = get_environment(
       aml_workspace, "diabetes_scoring",
       "diabetes_regression/scoring_dependencies.yml")

    inference_config = InferenceConfig(
        entry_script='score.py',
        source_directory=os.path.join(e.sources_directory_train, "scoring"),
        environment=environment,
    )

    service_description = f'Scoring model version {e.model_version}'

    if args.type == "AKS":

        deployment_config = AksWebservice.deploy_configuration(
            description=service_description,
            tags={"BuildId": e.build_id},
            compute_target_name=args.compute_target,
            autoscale_enabled=True,
            autoscale_min_replicas=1,
            autoscale_max_replicas=3,
            autoscale_refresh_seconds=10,
            autoscale_target_utilization=70,
            auth_enabled=True,
            cpu_cores=1,
            memory_gb=4,
            scoring_timeout_ms=5000,
            replica_max_concurrent_requests=2,
            max_request_wait_time=5000,
        )

    else:

        deployment_config = AciWebservice.deploy_configuration(
            description=service_description,
            tags={"BuildId": e.build_id},
            cpu_cores=1,
            memory_gb=4,
        )

    model = Model(aml_workspace, name=e.model_name, version=e.model_version)

    print(f'Deploying model {model} as service {args.service}')
    service = Model.deploy(
        workspace=aml_workspace,
        name=args.service,
        models=[model],
        inference_config=inference_config,
        deployment_config=deployment_config,
        overwrite=True,
    )
    service.wait_for_deployment(show_output=True)


if __name__ == '__main__':
    main()
