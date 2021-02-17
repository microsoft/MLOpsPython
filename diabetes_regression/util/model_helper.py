"""
model_helper.py
"""
from azureml.core import Run
from azureml.core import Workspace
from azureml.core.model import Model as AMLModel
from utils.logger.logger_interface import Severity
from utils.logger.observability import Observability

observability = Observability()


def get_current_workspace() -> Workspace:
    """
    Retrieves and returns the current workspace.
    Will not work when ran locally.

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
    Retrieves and returns a model from the workspace by its name
    and (optional) tag.

    Parameters:
    aml_workspace (Workspace): aml.core Workspace that the model lives.
    model_name (str): name of the model we are looking for
    (optional) model_version (str): model version. Latest if not provided.
    (optional) tag (str): the tag value & name the model was registered under.

    Return:
    A single aml model from the workspace that matches the name and tag, or
    None.
    """
    if aml_workspace is None:
        observability.log("No workspace defined - "
                          "using current experiment workspace.")
        aml_workspace = get_current_workspace()

    tags = None
    if tag_name is not None or tag_value is not None:
        # Both a name and value must be specified to use tags.
        if tag_name is None or tag_value is None:

            error = "model_tag_name and model_tag_value should " \
                     "both be supplied or excluded"
            observability.log(description=error, severity=Severity.ERROR)
            raise ValueError(error)
        tags = [[tag_name, tag_value]]

    model = None
    if model_version is not None:
        # TODO(tcare): Finding a specific version currently expects exceptions
        # to propagate in the case we can't find the model. This call may
        # result in a WebserviceException that may or may not be due to the
        # model not existing.
        model = AMLModel(
            aml_workspace,
            name=model_name,
            version=model_version,
            tags=tags)
    else:
        models = AMLModel.list(
            aml_workspace, name=model_name, tags=tags, latest=True)
        if len(models) == 1:
            model = models[0]
        elif len(models) > 1:
            error = "Expected only one model"
            observability.log(description=error, severity=Severity.ERROR)
            raise Exception(error)

    return model
