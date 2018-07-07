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

project_folder = '/tmp/e2e-test/05'
train_script = 'train-spark.py'
run_history_name = 'e2e-05'

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

print('copy {} and iris.csv to the project folder.'.format(train_script))
shutil.copy(train_script, os.path.join(project_folder, train_script))
shutil.copy('iris.csv', os.path.join(project_folder, 'iris.csv'))

print('create an ACI run config.')

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
run_config.environment.docker.base_image = azureml.core.runconfig.DEFAULT_MMLSPARK_CPU_IMAGE
print('base image is', run_config.environment.docker.base_image)
#run_config.environment.docker.base_image = 'microsoft/mmlspark:plus-0.9.9'

# use conda_dependencies.yml to create a conda environment in the Docker image for execution
# please update this file if you need additional packages.
run_config.environment.python.user_managed_dependencies = False

cd = CondaDependencies()
cd.add_conda_package('numpy')
# overwrite the default conda_dependencies.yml file
cd.save_to_file(project_dir = project_folder, file_name='conda_dependencies.yml')

# auto-prepare the Docker image when used for execution (if it is not already prepared)
run_config.prepare_environment = True

print()
print('##################################################')
print('submitting {} for a Spark run on ACI...'.format(train_script))
print('##################################################')
print()

run = Run.submit(project_object = project, 
                 run_config = run_config, 
                 script_to_run = "train-spark.py")

print(helpers.get_run_history_url(run))

# Shows output of the run on stdout.
run.wait_for_completion(show_output = True)

print('attach a VM target:')

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

print('Load the cpu-dsvm config and make it run Spark:')
# Load the "cpu-dsvm.runconfig" file (created by the above attach operation) in memory
run_config = RunConfiguration.load(project_object = project, run_config_name = "cpu-dsvm")

# set framework to PySpark
run_config.framework = "PySpark"

# Use Docker in the remote VM
run_config.environment.docker.enabled = True

# Use the MMLSpark CPU based image.
# https://hub.docker.com/r/microsoft/mmlspark/
run_config.environment.docker.base_image = azureml.core.runconfig.DEFAULT_MMLSPARK_CPU_IMAGE
print('base image is:', run_config.environment.docker.base_image)

# signal use the user-managed environment
# do NOT provision a new one based on the conda.yml file
run_config.environment.python.user_managed_dependencies = False

# Prepare the Docker and conda environment automatically when execute for the first time.
run_config.prepare_environment = True

print()
print('##################################################')
print('submitting {} for a Spark run on Docker in VM...'.format(train_script))
print('##################################################')
print()
run = Run.submit(project_object = project,
                 run_config = run_config,
                 script_to_run = train_script)

print(helpers.get_run_history_url(run))

# Shows output of the run on stdout.
run.wait_for_completion(show_output = True)

print('attach HDI')
from azureml.core.compute_target import HDIClusterTarget

try:
    # Attaches a HDI cluster as a compute target.
    project.attach_legacy_compute_target(HDIClusterTarget(name = "myhdi",
                                                          address = "sparkhai-ssh.azurehdinsight.net", 
                                                          username = "ninghai", 
                                                          password = "Password123!"))
except UserErrorException as e:
    print("Caught = {}".format(e.message))
    print("Compute config already attached.")

print('Load HDI run config.')
# load the runconfig object from the "myhdi.runconfig" file generated by the attach operaton above.
run_config = RunConfiguration.load(project_object = project, run_config_name = 'myhdi')

# ask system to prepare the conda environment automatically when executed for the first time
run_config.prepare_environment = True

print()
print('##################################################')
print('submitting {} for a HDI run...'.format(train_script))
print('##################################################')
print()

run = Run.submit(project_object = project,
                 run_config = run_config,
                 script_to_run = train_script)

print(helpers.get_run_history_url(run))

# Shows output of the run on stdout.
run.wait_for_completion(show_output = True)

# get all metris logged in the run
metrics = run.get_metrics()
print(metrics)