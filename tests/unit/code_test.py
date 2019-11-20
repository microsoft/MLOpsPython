import sys
import os
sys.path.append(os.path.abspath("./ml_service/util"))  # NOQA: E402
from workspace import get_workspace
from env_variables import Env


# Just an example of a unit test against
# a utility function common_scoring.next_saturday
def test_get_workspace():
    e = Env()
    workspace_name = e.workspace_name
    resource_group = e.resource_group
    subscription_id = e.subscription_id
    tenant_id = e.tenant_id
    app_id = e.app_id
    app_secret = e.app_secret

    aml_workspace = get_workspace(
        workspace_name,
        resource_group,
        subscription_id,
        tenant_id,
        app_id,
        app_secret)

    assert aml_workspace.name == workspace_name
