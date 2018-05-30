import os
from azureml.core.workspace import Workspace
from azureml.core.project import Project
from azureml.core.run import Run


def get_project(workspace, parent_folder, project_folder, run_history_name):

    # parent folder must already exists
    if not os.path.isdir(parent_folder):
        raise OSError("project parent folder {} doesn't exist".format(parent_folder))
    
    project_full_path = os.path.join(parent_folder, project_folder)
    
    # create project folder if it doesn't already exist
    if not os.path.isdir(project_full_path):
        os.mkdir(project_full_path)

    try:    
        # try loading the project folder it is already initialized (with a valid aml_config folder etc.)
        proj = Project(directory = project_full_path)
        print('Existing project loaded from:', project_full_path)
    except:
        # create a new project and attach it to a run history container
        proj = Project.attach(workspace_object = workspace,
                              run_history_name = run_history_name,
                              directory = project_full_path)
        
        print('new project created in:', project_full_path)
    return proj

def get_workspace_url(workspace):
    url = "https://portal.azure.com/?feature.customPortal=false&feature.showassettypes=Microsoft_Azure_MLTeamAccounts_MachineLearningServices&feature.canmodifystamps=true&Microsoft_Azure_MLWorkspaces=dev&Microsoft_Azure_MLCommitmentPlans=dev&Microsoft_Azure_MLWebservices=dev&Microsoft_Azure_MLHostingAccounts=dev&Microsoft_Azure_MLCompute=dev&Microsoft_Azure_MLTeamAccounts=dev&Microsoft_Azure_MLTeamAccounts_MachineLearningServices=dev&microsoft_azure_marketplace_ItemHideKey=Hidden_MLServices#@microsoft.onmicrosoft.com/resource/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/overview"
    return url.format(workspace.subscription_id,
                      workspace.resource_group, 
                      workspace.name)

# https://aka.ms/mlextensions_dev
def get_run_history_url(run):
    url = 'https://mlworkspace.azureml-test.net/home/%2Fsubscriptions%2F{0}%2FresourceGroups%2F{1}%2Fproviders%2FMicrosoft.MachineLearningServices%2Fworkspaces%2F{2}/projects/{3}/run-history/run-details/{4}'
    rh = run.history
    wso = rh.workspace_object
    return url.format(wso.subscription_id, 
                      wso.resource_group, 
                      wso.name,
                      rh.name,
                      run.id)
