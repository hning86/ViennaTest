# Check core SDK version number for debugging purposes
import azureml.core
print("SDK Version:", azureml.core.VERSION)

subscription_id = "fac34303-435d-4486-8c3f-7094d82a0b60"
resource_group = "aml-notebooks"
workspace_name = "haieastus2ws3"
workspace_region = 'eastus2' # or eastus2euap

# import the Workspace class and check the azureml SDK version
from azureml.core.workspace import Workspace, WorkspaceException

ws = Workspace.create(name = workspace_name,
                      subscription_id = subscription_id,
                      resource_group = resource_group, 
                      location = workspace_region)
ws.get_details()

ws.write_config()

# load workspace configuratio from ./aml_config/config.json file.  
my_workspace = Workspace.from_config()

print(my_workspace.get_details())
