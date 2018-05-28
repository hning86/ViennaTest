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
    ws = Workspace.from_config(run_id)
    print(ws.name, ws.resource_group)
    from azureml.core.run import Run
    run = Run(workspace=ws, run_history_name='e2e-07', run_id = run_id)
    return run

delete_web_service('my-aci-svc-hai')

#wsn = Workspace.create(name='datastorews', subscription_id=ws.subscription_id, resource_group=ws.resource_group, location='eastus2euap')
#wsn.write_config()