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

project_folder = '/tmp/e2e-test/04'
train_script = 'train-sklearn.py'
run_history_name = 'e2e-04'

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

from azureml.exceptions.azureml_exception import UserErrorException
from azureml.core.compute_target import RemoteTarget

try:
    # Attaches a remote docker on a remote vm as a compute target.
    project.attach_legacy_compute_target(RemoteTarget(name = "cpu-dsvm",
                                                   address = "hai2.eastus2.cloudapp.azure.com:5022", 
                                                   username = "ninghai", 
                                                   password = 'Spark888*123'))
except UserErrorException as e:
    print("Caught = {}".format(e.message))
    print("Compute config already attached.")


print()
print('##################################################')
print('Bare VM run')
print('##################################################')
print()

print('Load the cpu-dsvm config from aml_config directory...')

# Load the "cpu-dsvm.runconfig" file (created by the above attach operation) in memory
run_config = RunConfiguration.load(project_object = project, run_config_name =  "cpu-dsvm")

# replace with your path to the python interpreter in the remote VM found earlier
run_config.environment.python.interpreter_path = '/anaconda/envs/myenv/bin/python'

run_config.environment.python.user_managed_dependencies = True

print('submit run...')
run = Run.submit(project_object = project,
                 run_config = run_config,
                 script_to_run = train_script)

print(helpers.get_run_history_url(run))

# Shows output of the run on stdout.
run.wait_for_completion(show_output = True)

print()
print('##################################################')
print('DSVM Docker run...')
print('##################################################')
print()

print('Load cpu-dsvm run config and make it to use Docker.')
# Load the "cpu-dsvm.runconfig" file (created by the above attach operation) in memory
run_config = RunConfiguration.load(project_object = project, run_config_name = "cpu-dsvm")

# Use Docker in the remote VM
run_config.environment.docker.enabled = True

# Use the MMLSpark CPU based image.
run_config.environment.docker.base_image = azureml.core.runconfig.DEFAULT_CPU_IMAGE
#run_config.environment.docker.base_image = 'microsoft/mmlspark:plus-0.9.9'
print('Base Docker image is:', run_config.environment.docker.base_image )

# Ask system to provision a new one based on the conda_dependencies.yml file
run_config.environment.python.user_managed_dependencies = False

# create a new CondaDependencies obj
cd = CondaDependencies()

# add scikit-learn as a conda dependency
cd.add_conda_package('scikit-learn')

# overwrite the default conda_dependencies.yml file
cd.save_to_file(project_dir = project_folder, file_name='conda_dependencies.yml')

# Prepare the Docker and conda environment automatically when executingfor the first time.
run_config.prepare_environment = True

print('submitting run...')
run = Run.submit(project_object = project,
                 run_config = run_config,
                 script_to_run = train_script)

print(helpers.get_run_history_url(run))

# Shows output of the run on stdout.
run.wait_for_completion(show_output = True)

print('load cpu-dsvm run config and make it use a custom Docker image.')

# Load the "cpu-dsvm.runconfig" file (created by the above attach operation) in memory
run_config = RunConfiguration.load(project_object = project, run_config_name = "cpu-dsvm")

# Use Docker in the remote VM
run_config.environment.docker.enabled = True

# Use a custom Docker image hosted in Docker Hub
# https://hub.docker.com/r/ninghai/azureml
run_config.environment.docker.base_image = 'ninghai/azureml:0.3'
print('base image:', run_config.environment.docker.base_image)
# Use the existing Python environment. Do not provision a new conda environment.
run_config.environment.python.user_managed_dependencies = True

# Prepare the Docker and conda environment automatically when executing for the first time.
run_config.prepare_environment = True

print()
print('##################################################')
print('submitting {} for a Custom Docker run on VM...'.format(train_script))
print('##################################################')
print()
run = Run.submit(project_object = project,
                 run_config = run_config,
                 script_to_run = train_script)

print(helpers.get_run_history_url(run))

# Shows output of the run on stdout.
run.wait_for_completion(show_output = True)

run.get_metrics()
metrics = run.get_metrics()

print('When alpha is {1:0.2f}, we have min MSE {0:0.2f}.'.format(
    min(metrics['mse']), 
    metrics['alpha'][np.argmin(metrics['mse'])]
))