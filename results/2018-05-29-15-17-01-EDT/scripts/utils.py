from azureml.core import Workspace
import sys
import subprocess


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
