import azureml.core
from azureml.core.workspace import Workspace
from azureml.core.project import Project
from azureml.core.run import Run
from azureml.core.runconfig import RunConfiguration

import numpy as np
import os
import shutil

import helpers

print('Azure ML Core SDK Version:', azureml.core.VERSION)

project_folder = '/tmp/e2e-test/02'
train_script = 'train-sklearn.py'
run_history_name = 'e2e-02'

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

print('load run config')
# Editing a run configuration property on-fly.
run_config = RunConfiguration.load(project_object = project, run_config_name = "local")

# You can choose a specific Python environment by pointing to a Python path 
#run_config.environment.python.interpreter_path = '/home/ninghai/miniconda3/envs/sdk2/bin/python'

print()
print('##################################################')
print('submitting {} for a local run...'.format(train_script))
print('##################################################')
print()
run = Run.submit(project_object = project,
                 run_config = run_config,
                 script_to_run = train_script)

print(helpers.get_run_history_url_2(run))

# Shows output of the run on stdout.
run.wait_for_completion(show_output = True)

# Editing a run configuration property on-fly.
run_config = RunConfiguration.load(project_object = project, run_config_name = "local")

# Use a new conda environment that is to be created from the conda_dependencies.yml file
run_config.environment.python.user_managed_dependencies = False

# Automatically create the conda environment before the run
run_config.prepare_environment = True

from azureml.core.conda_dependencies import CondaDependencies
cd = CondaDependencies()
cd.add_conda_package('scikit-learn')
cd.save_to_file(project_dir = project_folder, file_name='conda_dependencies.yml')

print()
print('##################################################')
print("Submitting {} for a local conda run...".format(train_script))
print('##################################################')
print()
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
