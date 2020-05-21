"""Env dataclass to load and hold all environment variables
"""
from dataclasses import dataclass
import os
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Env:
    """Loads all environment variables into a predefined set of properties
    """
    # to load .env file into environment variables for local execution
    load_dotenv()
    workspace_name: Optional[str] = os.environ.get("WORKSPACE_NAME")
    resource_group: Optional[str] = os.environ.get("RESOURCE_GROUP")
    subscription_id: Optional[str] = os.environ.get("SUBSCRIPTION_ID")
    tenant_id: Optional[str] = os.environ.get("TENANT_ID")
    app_id: Optional[str] = os.environ.get("SP_APP_ID")
    app_secret: Optional[str] = os.environ.get("SP_APP_SECRET")
    vm_size: Optional[str] = os.environ.get("AML_COMPUTE_CLUSTER_CPU_SKU")
    compute_name: Optional[str] = os.environ.get("AML_COMPUTE_CLUSTER_NAME")
    vm_priority: Optional[str] = os.environ.get("AML_CLUSTER_PRIORITY",
                                                'lowpriority')
    min_nodes: int = int(os.environ.get("AML_CLUSTER_MIN_NODES", 0))
    max_nodes: int = int(os.environ.get("AML_CLUSTER_MAX_NODES", 4))
    build_id: Optional[str] = os.environ.get("BUILD_BUILDID")
    pipeline_name: Optional[str] = os.environ.get("TRAINING_PIPELINE_NAME")
    sources_directory_train: Optional[str] = os.environ.get(
        "SOURCES_DIR_TRAIN")
    train_script_path: Optional[str] = os.environ.get("TRAIN_SCRIPT_PATH")
    evaluate_script_path: Optional[str] = os.environ.get(
        "EVALUATE_SCRIPT_PATH")
    register_script_path: Optional[str] = os.environ.get(
        "REGISTER_SCRIPT_PATH")
    model_name: Optional[str] = os.environ.get("MODEL_NAME")
    experiment_name: Optional[str] = os.environ.get("EXPERIMENT_NAME")
    model_version: Optional[str] = os.environ.get('MODEL_VERSION')
    image_name: Optional[str] = os.environ.get('IMAGE_NAME')
    db_cluster_id: Optional[str] = os.environ.get("DB_CLUSTER_ID")
    score_script: Optional[str] = os.environ.get("SCORE_SCRIPT")
    build_uri: Optional[str] = os.environ.get("BUILD_URI")
    dataset_name: Optional[str] = os.environ.get("DATASET_NAME")
    datastore_name: Optional[str] = os.environ.get("DATASTORE_NAME")
    dataset_version: Optional[str] = os.environ.get("DATASET_VERSION")
    run_evaluation: Optional[str] = os.environ.get("RUN_EVALUATION", "true")
    allow_run_cancel: Optional[str] = os.environ.get("ALLOW_RUN_CANCEL",
                                                     "true")
    aml_env_name: Optional[str] = os.environ.get("AML_ENV_NAME")
    rebuild_env: Optional[bool] = os.environ.get(
        "AML_REBUILD_ENVIRONMENT", "false").lower().strip() == "true"
