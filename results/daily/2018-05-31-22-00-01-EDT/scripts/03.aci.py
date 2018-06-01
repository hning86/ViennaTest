import azureml.core
from azureml.core.workspace import Workspace
from azureml.core.project import Project
from azureml.core.run import Run
from azureml.core.runconfig import RunConfiguration
from azureml.core.conda_dependencies import CondaDependencies

import numpy as np
import os
import shutil

import helpers

print('Azure ML Core SDK Version:', azureml.core.VERSION)

project_folder = '/tmp/e2e-test/03'
train_script = 'train-sklearn.py'
run_history_name = 'e2e-03'

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

print()
print('##################################################')
print('ACI run...')
print('##################################################')
print()

print('Create a run config object for ACI')
# create a new runconfig object
run_config = RunConfiguration(project_object = project, run_config_name = 'my-aci-run-config')

# signal that you want to use ACI to execute script.
run_config.target = "containerinstance"

# ACI container group is only supported in certain regions, which can be different than the region the Workspace is in.
run_config.container_instance.region = 'eastus'

# set the ACI CPU and Memory 
run_config.container_instance.cpu_cores = 1
run_config.container_instance.memory_gb = 2

# enable Docker 
run_config.environment.docker.enabled = True

# set Docker base image to the default CPU-based image
run_config.environment.docker.base_image = azureml.core.runconfig.DEFAULT_CPU_IMAGE
# run_config.environment.docker.base_image = 'microsoft/mmlspark:plus-0.9.9'
print('base image is', run_config.environment.docker.base_image)

# create a new CondaDependencies obj
cd = CondaDependencies()

# add scikit-learn as a conda dependency
cd.add_conda_package('scikit-learn')

# overwrite the default conda_dependencies.yml file
cd.save_to_file(project_dir = project_folder, file_name='conda_dependencies.yml')

# use conda_dependencies.yml to create a conda environment in the Docker image for execution
# please update this file if you need additional packages.
run_config.environment.python.user_managed_dependencies = False

# auto-prepare the Docker image when used for execution (if it is not already prepared)
run_config.prepare_environment = True

print("submitting run...")
run = Run.submit(project_object = project,
                 run_config = run_config,
                 script_to_run = train_script)

print(helpers.get_run_history_url(run))

# Shows output of the run on stdout.
run.wait_for_completion(show_output = True)

# get all metris logged in the run# get al 
run.get_metrics()
metrics = run.get_metrics()

print('When alpha is {1:0.2f}, we have min MSE {0:0.2f}.'.format(
    min(metrics['mse']), 
    metrics['alpha'][np.argmin(metrics['mse'])]
))