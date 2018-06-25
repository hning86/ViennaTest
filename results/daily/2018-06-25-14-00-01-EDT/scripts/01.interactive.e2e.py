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

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import helpers
from sklearn.externals import joblib

print('Azure ML Core SDK Version:', azureml.core.VERSION)

web_service_name =  "rrs01-preview"
run_history_name = 'e2e-01'

ws = Workspace.from_config()

print('Workspace details:')
print(ws.resource_group, ws.name, ws.location)

# load diabetes dataset, a well-known built-in small dataset that comes with scikit-learn
X, y = load_diabetes(return_X_y = True)
columns = ['age', 'gender', 'bmi', 'bp', 's1', 's2', 's3', 's4', 's5', 's6']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)
data = {
    "train": {"X": X_train, "y": y_train },  
    "test": {"X": X_test, "y": y_test }
}
model_file_name = "model.pkl"

# start a training run
root_run = Run.start_logging(workspace = ws, history_name = run_history_name)

# list of numbers from 0.01 to 0.9 with a 0.05 interval
alphas = np.arange(0.0, 1.0, 0.05)

print('start sequential parameter sweep...')

# try a bunch of alpha values in a Linear Regression (Ridge) model
for alpha in alphas:
    print('try alpha value of {0:.2f}'.format(alpha))
    # create a bunch of child runs
    with root_run.child_run("alpha" + str(alpha)) as run:
        # More data science stuff
        reg = Ridge(alpha=alpha)
        reg.fit(data["train"]["X"], data["train"]["y"])
        # TODO save model
        preds = reg.predict(data["test"]["X"])
        mse = mean_squared_error(preds, data["test"]["y"])
        # End train and eval

        # log alpha, mean_squared_error and feature names in run history
        run.log("alpha", alpha)
        run.log("mse", mse)
        run.log_list("columns", columns)

        with open(model_file_name, "wb") as file:
            joblib.dump(value = reg, filename = file)
        
        # upload the serialized model into run history record
        run.upload_file(name = "outputs/" + model_file_name, path_or_stream = model_file_name)
        
        # now delete the serialized model from local folder
        os.remove(model_file_name)
        
# Declare run completed
root_run.complete()

print('Find the best run.')

# List all runs
child_runs = {}
child_run_metrics = {}

for r in root_run.get_children():
    child_runs[r.id] = r
    child_run_metrics[r.id] = r.get_metrics()

best_run_id = min(child_run_metrics, key = lambda k: child_run_metrics[k]['mse'])
best_run = child_runs[best_run_id]
print('Best run is:', best_run_id)
print('Metrics:', child_run_metrics[best_run_id])

print('Run history url:')
print(helpers.get_run_history_url(best_run))
print(helpers.get_run_history_url_2(best_run))

best_model_file_name = "best_model.pkl"
best_run.download_file(name = 'outputs/' + model_file_name, 
                       output_file_path = best_model_file_name)

print('plot mse_over_alpha.png')
best_alpha = child_run_metrics[best_run_id]['alpha']
min_mse = child_run_metrics[best_run_id]['mse']

alpha_mse = np.array([(child_run_metrics[k]['alpha'], child_run_metrics[k]['mse']) for k in child_run_metrics.keys()])

plt.plot(alpha_mse[:,0], alpha_mse[:,1], 'r--')
plt.plot(alpha_mse[:,0], alpha_mse[:,1], 'bo')

plt.xlabel('alpha', fontsize = 14)
plt.ylabel('mean squared error', fontsize = 14)
plt.title('MSE over alpha', fontsize = 16)

# plot arrow
plt.arrow(x = best_alpha, y = min_mse + 39, dx = 0, dy = -26, ls = '-', lw = 0.4,
          width = 0, head_width = .03, head_length = 8)

# plot "best run" text
plt.text(x = best_alpha - 0.08, y = min_mse + 50, s = 'Best Run', fontsize = 14)
plt.savefig('mse_over_alpha.png', format='png')

print('upload mse_over_alpha.png.')

root_run.upload_file(name = "outputs/mse_over_alpha.png", path_or_stream = "mse_over_alpha.png")

aciconfig = AciWebservice.deploy_configuration(cpu_cores = 1, memory_gb = 1, tags = ['e2e-01'], description = 'e2e test 01')

print('deploying to ACI...')
from azureml.core.webservice import Webservice

service = Webservice.deploy(name = web_service_name,
                            workspace = ws,
                            deployment_config = aciconfig,
                            model_paths = ['best_model.pkl'],
                            runtime = 'python',
                            conda_file = 'myenv.yml',
                            execution_script = 'score.py')

service.wait_for_deployment(show_output = True)

test_sample = json.dumps({'data':X_test[0:10,:].tolist()})
test_sample = bytes(test_sample, encoding='utf8')

# test result
print('test the web service.')
print(service.run(input_data=test_sample))

# claan up
print('delete ACI')
service.delete()
