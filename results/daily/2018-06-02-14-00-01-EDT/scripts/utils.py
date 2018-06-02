from azureml.core import Workspace, Project
from azureml.core.runconfig import RunConfiguration

import sys
import subprocess
import shutil


def delete_web_service(name):
    ws = Workspace.from_config()
    for svc in ws.list_webservices():
        print('found {}'.format(svc.name))
        if (svc.name == name):
            print('deleting {}...'.format(name))
            svc.delete()
            print('deleted.')

def pip_freeze():
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    print(sys.path)
    print()
    print(reqs)

def delete_compute():
    ws = Workspace.from_config()
    for ct in ws.list_compute_targets():
        print(ct.name, ct.cluster_type)
        #ct.delete()

#delete_compute()
def get_run(run_id):
    ws = Workspace.from_config()
    print(ws.name, ws.resource_group)
    from azureml.core.run import Run
    run = Run(workspace=ws, run_history_name='e2e-07', run_id = run_id)
    return run

def show_all_models():
    ws = Workspace.from_config()
    for m in ws.list_models():
        print(m.name)

def datastores():
    ws = Workspace.from_config()
    from azureml.core.datastore import Datastore
    #fs = Datastore.register_azure_file_share(workspace=ws, datastore_name='amlfiles', account_name='sparkstores', file_share_name='amlfiles', account_key='EIXQX9gqG9h28o6xjbo1O4WXo0322gp1Mxz83OP4ryRXcqGbKE6O4MM2Pqv8Crc9A5bNW0ykRoSif5uPEF0Smw==') # FILE
    #fs = Datastore.get(ws, 'amlfiles')

    #fs.upload(src_dir='./aml_config')

    #my_store = Datastore.register_azure_blob_container(workspace=ws, datastore_name='sparkstores', account_name='sparkstores', container_name='amldatastore', account_key='R5ihVsoLsPerg3l8qgJzNmZ0EezdwbAYfBNT5dwbcPl79rclfLbkBQxJpPkoEt/vuLaUXqtBQfyYBL+tUqm7ZA==')
    #my_store = Datastore.get(ws, 'sparkstores')
    #my_store.upload('./aml_config')

    for d in ws.datastores():
        print(d.datastore_name)

#from azureml.core.compute import AciCompute

from azureml.core.run import Run

def get_child_runs(run_history_name, parent_run_id):
    ws = Workspace.from_config()
    run = Run(ws, run_history_name, parent_run_id)
    print('parent:', run.id)
    print('children:')
    for c in run.get_children():
        print(c.id)
    
def del_all_ws():
    ws = Workspace.from_config()
    #print(ws.get_details())
    for img in ws.list_models():
        print(img.name)
        img.delete()
    
def submit_job():
    ws = Workspace.from_config()
    proj = Project.attach(ws, 'util', '/tmp/random_proj')
    rc = RunConfiguration(proj, "local")
    shutil.copy('./train-sklearn-one-model.py', '/tmp/random_proj/train-sklearn-one-model.py')
    #run = Run.submit(proj, rc, "train-sklearn-one-model.py", "--alpha 0.9")
    run = Run.submit(proj, rc, "train-sklearn-one-model.py", arguments_list=["--alpha", "0.9"])
    run.wait_for_completion(show_output=True)

ws = Workspace.from_config()
proj = Project.attach(ws, 'test_rh', '/tmp/randomproj1')
rc = RunConfiguration(proj, 'local')
#rc.environment.python.interpreter_path = '/Users/haining/miniconda3/envs/comet/bin/python'
with open('/tmp/randomproj1/test.py', 'w') as file:
    file.write('import sys; print(sys.version)')

r = Run.submit(proj, rc, 'test.py')
r.wait_for_completion(show_output=True)