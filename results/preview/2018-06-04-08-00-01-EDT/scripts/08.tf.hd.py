import azureml.core
from azureml.core.workspace import Workspace
from azureml.core.project import Project
from azureml.core.run import Run
from azureml.core.runconfig import RunConfiguration
from azureml.core.compute import BatchAiCompute
from azureml.train.hyperdrive import *
from azureml.train.dnn import TensorFlow

import numpy as np
import os
import shutil

import helpers

print('Azure ML Core SDK Version:', azureml.core.VERSION)

project_folder = '/tmp/e2e-test/08'
train_script = 'mnist_tf.py'
run_history_name = 'e2e-08'

ws = Workspace.from_config()

print('Workspace details:')
print(ws.resource_group, ws.name, ws.location)

if os.path.isdir(project_folder):
    print('{} already exists, remove it.'.format(project_folder))
    shutil.rmtree(project_folder)

project = Project.attach(workspace_object = ws,
                         run_history_name = run_history_name,
                         directory = project_folder)

print(project.project_directory, project.run_history.name, sep = '\n')

print('copy {} to the project folder.'.format(train_script))
shutil.copy(train_script, os.path.join(project_folder, train_script))


# choose a name for your cluster
batchai_cluster_name = "gpucluster"

print('create or load BatchAI compute {}...'.format(batchai_cluster_name))

found = False
# see if this compute target already exists in the workspace
for ct in ws.list_compute_targets():
    print(ct.name, ct.type)
    if (ct.name == batchai_cluster_name and ct.type == 'BatchAI'):
        found = True
        print('found compute target. just use it.')
        compute_target = ct
        break
        
if not found:
    print('creating a new compute target...')
    provisioning_config = BatchAiCompute.provisioning_configuration(vm_size = "STANDARD_NC6", # for CPU, use "STANDARD_D2_V2"
                                                                #vm_priority = 'lowpriority', # optional
                                                                autoscale_enabled = True,
                                                                cluster_min_nodes = 1, 
                                                                cluster_max_nodes = 4)

    # create the cluster
    compute_target = ws.create_compute_target(batchai_cluster_name, provisioning_config)
    compute_target.wait_for_provisioning(show_output = True)


print('create TensorFlow estimator.')
from azureml.train.dnn import TensorFlow
script_params = {
    '--batch-size': 50,
    '--first-layer-neurons': 300,
    '--second-layer-neurons': 100,
    '--learning-rate': 0.01
}

tfe = TensorFlow(project = project,
                 script_params = script_params,
                 compute_target = compute_target,
                 entry_script = 'mnist_tf.py',
                 use_gpu = True,
                 conda_packages = ['scikit-learn'])

print()
print('##################################################')
print('submitting {} for a Batch AI run...'.format(train_script))
print('##################################################')
print()

# start the job
run = tfe.fit()
print(helpers.get_run_history_url(run))
run.wait_for_completion(show_output = True)


print('configure hyperdrive.')
# parameter space to sweep over
ps = RandomParameterSampling(
    {
        "batch-size": choice(10, 25, 50, 75, 100),
        "first-layer-neurons": choice(10, 50, 100, 200),
        "second-layer-neurons": choice(10, 50, 100, 200),
        "learning-rate": uniform(0.05, 0.5)
    }
)

# early termniation policy
# check every 2 iterations and if the primary metric (epoch_val_acc) falls
# outside of the range of 10% of the best recorded run so far, terminate it.
etp = BanditPolicy(slack_factor = 0.1, evaluation_interval = 2)

# Hyperdrive run configuration
hrc = HyperDriveRunConfig(
    ".",
    estimator = tfe,
    hyperparameter_sampling = ps,
    policy = etp,
    # metric to watch (for early termination)
    primary_metric_name = 'epoch_val_acc',
    # terminate if metric falls below threshold
    primary_metric_goal = PrimaryMetricGoal.MAXIMIZE,
    max_total_runs = 200,
    max_concurrent_runs = 4,
    compute_target = compute_target
)

print()
print('##################################################')
print('submitting {} for a hyperdrive run on Batch AI...'.format(train_script))
print('##################################################')
print()
# Start Hyperdrive run# Start  
hr = search(hrc, "sklearn-hyperdrive")
print(helpers.get_run_history_url(hr))
