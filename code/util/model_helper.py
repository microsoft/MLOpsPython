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


def _get_model_by_build_id(
    model_name: str,
    build_id: str,
    aml_workspace: Workspace = None
) -> AMLModel:
    """
    Retrieves and returns the latest model from the workspace
    by its name and tag.

    Parameters:
    aml_workspace (Workspace): aml.core Workspace that the model lives.
    model_name (str): name of the model we are looking for
    build_id (str): the build id the model was registered under.

    Return:
    A single aml model from the workspace that matches the name and tag.
    """
    # Validate params. cannot be None.
    if model_name is None:
        raise ValueError("model_name[:str] is required")
    if build_id is None:
        raise ValueError("build_id[:str] is required")
    if aml_workspace is None:
        aml_workspace = get_current_workspace()

    # get model by tag.
    model_list = AMLModel.list(
        aml_workspace, name=model_name,
        tags=[["BuildId", build_id]], latest=True
    )

    # latest should only return 1 model, but if it does, then maybe
    # internal code was accidentally changed or the source code has changed.
    should_not_happen = ("THIS SHOULD NOT HAPPEN: found more than one model "
                         "for the latest with {{model_name: {model_name},"
                         "BuildId: {build_id}. Models found: {model_list}}}")\
        .format(model_name=model_name, build_id=build_id,
                model_list=model_list)
    if len(model_list) > 1:
        raise ValueError(should_not_happen)

    return model_list


def get_model_by_build_id(
    model_name: str,
    build_id: str,
    aml_workspace: Workspace = None
) -> AMLModel:
    """
    Wrapper function for get_model_by_id that throws an error if model is none
    """
    model_list = _get_model_by_build_id(model_name, build_id, aml_workspace)

    if model_list:
        return model_list[0]

    no_model_found = ("Model not found with model_name: {model_name} "
                      "BuildId: {build_id}.")\
        .format(model_name=model_name, build_id=build_id)
    raise Exception(no_model_found)
