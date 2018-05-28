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

show_all_models()
