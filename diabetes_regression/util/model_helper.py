"""
model_helper.py
"""
from azureml.core import Run
from azureml.core import Workspace
from azureml.core.model import Model as AMLModel


def get_current_workspace() -> Workspace:
    """
    Retrieves and returns the latest model from the workspace
    by its name and tag. Will not work when ran locally.

    Parameters:
    None

    Return:
    The current workspace.
    """
    run = Run.get_context(allow_offline=False)
    experiment = run.experiment
    return experiment.workspace


def get_model(
    model_name: str,
    model_version: int = None,  # If none, return latest model
    tag_name: str = None,
    tag_value: str = None,
    aml_workspace: Workspace = None
) -> AMLModel:
    """
    Retrieves and returns the latest model from the workspace
    by its name and (optional) tag.

    Parameters:
    aml_workspace (Workspace): aml.core Workspace that the model lives.
    model_name (str): name of the model we are looking for
    (optional) model_version (str): model version. Latest if not provided.
    (optional) tag (str): the tag value & name the model was registered under.

    Return:
    A single aml model from the workspace that matches the name and tag.
    """
    if aml_workspace is None:
        print("No workspace defined - using current experiment workspace.")
        aml_workspace = get_current_workspace()

    try:
        if tag_name is not None and tag_value is not None:
            model = AMLModel(
                aml_workspace,
                name=model_name,
                version=model_version,
                tags=[[tag_name, tag_value]])
        elif (tag_name is None and tag_value is not None) or (
            tag_value is None and tag_name is not None
        ):
            raise ValueError(
                "model_tag_name and model_tag_value should both be supplied"
                + "or excluded"  # NOQA: E501
            )
        else:
            model = AMLModel(aml_workspace, name=model_name, version=model_version)  # NOQA: E501
    except Exception:
        return None
    return model
