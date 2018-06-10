from sklearn.datasets import load_diabetes
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

import azureml.core
from azureml.core.workspace import Workspace
from azureml.core.project import Project
from azureml.core.run import Run
from azureml.core.webservice import AciWebservice

from tqdm import tqdm
import numpy as np
import os
import shutil
import json


print('Azure ML Core SDK Version:', azureml.core.VERSION)

proj_path = '/tmp/e2e-test/10'
web_service_name =  "rrs02"
run_history_name = 'e2e-10-preview'

ws = Workspace.from_config('./aml_config/config.json')

print('Workspace details:')
print(ws.resource_group, ws.name, ws.location)

model = ws.register_model(model_path = "best_model.pkl",
                          model_name = "best_model.pkl",
                          tags = ["diabetes", "regression"],
                          description = "Ridge regression model to predict diabetes")

regression_models = ws.list_models(tag = "regression")
for m in regression_models:
    print("Name:", m.name,"\tVersion:", m.version, "\tDescription:", m.description, m.tags)

model = regression_models[-1]
print(model.description)

image = ws.create_image(name = "myimage",
                        models = [model],
                        runtime = "python",
                        driver_file = "score.py",
                        conda_file = "myenv.yml",
                        tags = ["diabetes","regression"],
                        description = "Image with ridge regression model")

image.wait_for_creation(show_output = True)

for i in ws.list_images(tag = "diabetes"):
    print('{}(v.{} [{}]) stored at {} with build log {}'.format(i.name, i.version, i.creation_state, i.image_location, i.image_build_log_uri))


aciconfig = AciWebservice.deploy_configuration(cpu_cores = 1, 
                                            memory_gb = 1, 
                                            tags = ['regression','diabetes'], 
                                            description = 'Predict diabetes using regression model')

service = ws.deploy_webservice(name = web_service_name,
                               deploy_config = aciconfig,
                               target = None,
                               image = image)
                               
service.wait_for_deployment(show_output = True)


import json

test_sample = json.dumps({'data': [
    [1,2,3,4,5,6,7,8,9,10], 
    [10,9,8,7,6,5,4,3,2,1]
]})
test_sample = bytes(test_sample,encoding = 'utf8')

prediction = service.run(input_data = test_sample)
print(prediction)

for w in ws.list_webservices():
    print(w.name, w.scoring_uri)

print("delete service.")
service.delete()
print("delete image")
image.delete()
print("delete model")
model.delete()