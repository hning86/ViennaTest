import azureml.core
from azureml.core.workspace import Workspace
from azureml.core.project import Project
from azureml.core.run import Run
from azureml.core.runconfig import RunConfiguration
from azureml.core.compute import BatchAiCompute
from azureml.core.conda_dependencies import CondaDependencies

import helpers
import numpy as np
import os
import shutil

import helpers

print('Azure ML Core SDK Version:', azureml.core.VERSION)

project_folder = '/tmp/e2e-test/20'
train_script = 'monte-carlo.py'
run_history_name = 'e2e-20'

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
batchai_cluster_name = "cpucluster"

print('create or load BatchAI compute {}...'.format(batchai_cluster_name))

found = False
# see if this compute target already exists in the workspace
for ct in ws.list_compute_targets():
    print(ct.name, ct.cluster_type)
    if (ct.name == batchai_cluster_name and ct.cluster_type == 'BatchAI'):
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
    compute_target = ws.create_compute_target(batchai_cluster_name, provisioning_config)
    compute_target.wait_for_provisioning(show_output = True)

print('create Batch AI run config')

rc = RunConfiguration(project, "dask_run_config")
rc.environment.docker.enabled = True
rc.prepare_environment = True
rc.target = batchai_cluster_name
rc.environment.python.user_managed_dependencies = False
rc.batchai.node_count = 2

# create a new CondaDependencies obj
cd = CondaDependencies()
# add scikit-learn as a conda dependency
cd.add_conda_package('dask')
cd.add_conda_package('joblib')
cd.add_pip_package('azureml-contrib-daskonbatch')

# overwrite the default conda_dependencies.yml file
cd.save_to_file(project_dir = project_folder, file_name='conda_dependencies.yml')

print()
print('##################################################')
print('submitting {} for a batch ai run...'.format(train_script))
print('##################################################')
print()

print("prepare run...")
prep = Run.prepare_compute_target(project_object = project, run_config = rc)

print(helpers.get_run_history_url(prep))

prep.wait_for_completion(show_output = True)

print('now run...')

run = Run.submit(project_object = project, 
                 run_config = rc, 
                 script_to_run = train_script)

print("run history URL is here:")
print(helpers.get_run_history_url(run))

run.wait_for_completion(show_output = True)
print(helpers.get_run_history_url(run))
