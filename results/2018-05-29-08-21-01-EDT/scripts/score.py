import pickle
import json
import numpy
from sklearn.externals import joblib
from sklearn.linear_model import Ridge

def init():
    global model
    model = joblib.load("best_model.pkl")

def run(raw_data):
    try:
        data = json.loads(raw_data)['data']
        data = numpy.array(data)
        result = model.predict(data)
    except Exception as e:
        result = str(e)
    return json.dumps({"result": result.tolist()})
