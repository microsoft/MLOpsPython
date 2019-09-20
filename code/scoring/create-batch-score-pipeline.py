from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import PipelineData
from azureml.pipeline.steps import PythonScriptStep

import os

release_id = os.environ.get("RELEASE_DEPLOYMENTID")
model_name = os.environ.get("MODEL_NAME")

input_dir = DataReference(datastore=batchscore_blob, 
                             data_reference_name="input_images",
                             path_on_datastore="batchscoring/images",
                             mode="download"
                            )

label_dir = DataReference(datastore=batchscore_blob, 
                          data_reference_name="input_labels",
                          path_on_datastore="batchscoring/labels",
                          mode="download"                          
                         )

output_dir = PipelineData(name="scores", 
                          datastore=def_data_store, 
                          output_path_on_compute="batchscoring/results")

compute_target = AmlCompute()

run_config = RunConfiguration(conda_dependencies=CondaDependencies.create(
    conda_packages=['numpy', 'pandas',
                    'scikit-learn', 'tensorflow', 'keras'],
    pip_packages=['azure', 'azureml-core',
                  'azure-storage',
                  'azure-storage-blob'])
)

score_step = PythonScriptStep(
    name="batch_score",
    script_name="score.py",
    arguments=["--input_dir", input_dir, 
               "--model_name", model_name,
               "--label_dir", label_dir, 
               "--output_dir", output_dir],
    compute_target=compute_target,
    inputs=[input_images, label_dir],
    outputs=[output_dir],
    runconfig=run_config
)

score_pipeline = Pipeline(workspace=ws, steps=[score_step])
score_pipeline.validate()

published_pipeline = score_pipeline.publish(
        name=pipeline_name,
        description="Model training/retraining pipeline",
        version=release_id
    )

print(f'Published pipeline: {published_pipeline.name}')
print(f'for release {published_pipeline.version}')
