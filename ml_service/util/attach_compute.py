
import traceback
from azureml.core import Workspace
from azureml.core.compute import AmlCompute
from azureml.core.compute import ComputeTarget
from azureml.exceptions import ComputeTargetException
from ml_service.util.env_variables import Env


def get_compute(workspace: Workspace, compute_name: str, vm_size: str, for_batch_scoring: bool = False):  # NOQA E501
    try:
        if compute_name in workspace.compute_targets:
            compute_target = workspace.compute_targets[compute_name]
            if compute_target and type(compute_target) is AmlCompute:
                print("Found existing compute target " + compute_name + " so using it.") # NOQA
        else:
            e = Env()
            compute_config = AmlCompute.provisioning_configuration(
                vm_size=vm_size,
                vm_priority=e.vm_priority if not for_batch_scoring else e.vm_priority_scoring,  # NOQA E501
                min_nodes=e.min_nodes if not for_batch_scoring else e.min_nodes_scoring,  # NOQA E501
                max_nodes=e.max_nodes if not for_batch_scoring else e.max_nodes_scoring,  # NOQA E501
                idle_seconds_before_scaledown="300"
                #    #Uncomment the below lines for VNet support
                #    vnet_resourcegroup_name=vnet_resourcegroup_name,
                #    vnet_name=vnet_name,
                #    subnet_name=subnet_name
            )
            compute_target = ComputeTarget.create(
                workspace, compute_name, compute_config
            )
            compute_target.wait_for_completion(
                show_output=True, min_node_count=None, timeout_in_minutes=10
            )
        return compute_target
    except ComputeTargetException:
        traceback.print_exc()
        print("An error occurred trying to provision compute.")
        exit(1)
