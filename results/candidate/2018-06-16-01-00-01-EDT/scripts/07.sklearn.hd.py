import azureml.core
from azureml.core.workspace import Workspace
from azureml.core.project import Project
from azureml.core.run import Run
from azureml.core.runconfig import RunConfiguration
from azureml.core.compute import BatchAiCompute
from azureml.train.hyperdrive import RandomParameterSampling, BanditPolicy, PrimaryMetricGoal, HyperDriveRunConfig, search, uniform

import numpy as np
import os
import shutil

import helpers

print('Azure ML Core SDK Version:', azureml.core.VERSION)

project_folder = '/tmp/e2e-test/07'
train_script = 'train-sklearn-one-model.py'
run_history_name = 'e2e-07'

ws = Workspace.from_config()

print('Workspace details:')
print(ws.resource_group, ws.name, ws.location)

if os.path.isdir(project_folder):
    print('{} already exists, remove it.'.format(project_folder))
    shutil.rmtree(project_folder)

project = Project.attach(workspace_object = ws,
                         history_name = run_history_name,
                         directory = project_folder)

print(project.project_directory, project.history.name, sep = '\n')

print('copy {} to the project folder.'.format(train_script))
shutil.copy(train_script, os.path.join(project_folder, train_script))


# choose a name for your cluster
batchai_cluster_name = "cpucluster"

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
    provisioning_config = BatchAiCompute.provisioning_configuration(vm_size = "STANDARD_D2_V2", # for GPU, use "STANDARD_NC6"
                                                                #vm_priority = 'lowpriority', # optional
                                                                autoscale_enabled = True,
                                                                cluster_min_nodes = 1, 
                                                                cluster_max_nodes = 4)

    # create the cluster
    compute_target = BatchAiCompute.create(workspace = ws, name = batchai_cluster_name, provisioning_configuration = provisioning_config)
    compute_target.wait_for_provisioning(show_output = True)


print('create generic estimator.')
from azureml.train.estimator import Estimator
script_params = {
    '--alpha': 0.1
}

sk_est = Estimator(project = project,
                   script_params = script_params,
                   compute_target = compute_target,
                   entry_script = train_script,
                   conda_packages = ['scikit-learn'])
                   #custom_docker_base_image = 'ninghai/azureml:0.3') # use a custom image here

print()
print('##################################################')
print('Batch AI run...')
print('##################################################')
print()

# start the job
run = sk_est.fit()
print(helpers.get_run_history_url(run))
run.wait_for_completion(show_output = True)


print('configure hyperdrive.')


# parameter space to sweep over
ps = RandomParameterSampling(
    {
        "alpha": uniform(0.0, 1.0)
    }
)

# early termniation policy
# check every 2 iterations and if the primary metric (epoch_val_acc) falls
# outside of the range of 10% of the best recorded run so far, terminate it.
etp = BanditPolicy(slack_factor = 0.1, evaluation_interval = 2)

# Hyperdrive run configuration
hrc = HyperDriveRunConfig(
    ".",
    estimator = sk_est,
    hyperparameter_sampling = ps,
    policy = etp,
    # metric to watch (for early termination)
    primary_metric_name = 'mse',
    # terminate if metric falls below threshold
    primary_metric_goal = PrimaryMetricGoal.MINIMIZE,
    max_total_runs = 20,
    max_concurrent_runs = 4,
    compute_target = compute_target
)

print()
print('##################################################')
print('Hyperdrive run on Batch AI...')
print('##################################################')
print()
# Start Hyperdrive run# Start  
hr = search(hrc, "sklearn-hyperdrive")
print(helpers.get_run_history_url(hr))
#best_run = hr.get_best_run_by_primary_metric()