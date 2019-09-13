import os
from dotenv import load_dotenv
from azureml.core import Workspace
from azureml.core.compute import AmlCompute
from azureml.core.compute import ComputeTarget
from azureml.exceptions import ComputeTargetException


def get_compute(
    workspace: Workspace,
    compute_name: str,
    vm_size: str
):
    # Load the environment variables from .env in case this script
    # is called outside an existing process
    load_dotenv()
    # Verify that cluster does not exist already
    try:
        if compute_name in workspace.compute_targets:
            compute_target = workspace.compute_targets[compute_name]
            if compute_target and type(compute_target) is AmlCompute:
                print('Found existing compute target ' + compute_name
                      + ' so using it.')
        else:
            compute_config = AmlCompute.provisioning_configuration(
                vm_size=vm_size,
                vm_priority=os.environ.get("AML_CLUSTER_PRIORITY",
                                           'lowpriority'),
                min_nodes=int(os.environ.get("AML_CLUSTER_MIN_NODES", 0)),
                max_nodes=int(os.environ.get("AML_CLUSTER_MAX_NODES", 4)),
                idle_seconds_before_scaledown="300"
                #    #Uncomment the below lines for VNet support
                #    vnet_resourcegroup_name=vnet_resourcegroup_name,
                #    vnet_name=vnet_name,
                #    subnet_name=subnet_name
            )
            compute_target = ComputeTarget.create(workspace, compute_name,
                                                  compute_config)
            compute_target.wait_for_completion(
                show_output=True,
                min_node_count=None,
                timeout_in_minutes=10)
        return compute_target
    except ComputeTargetException as e:
        print(e)
        print('An error occurred trying to provision compute.')
        exit()
