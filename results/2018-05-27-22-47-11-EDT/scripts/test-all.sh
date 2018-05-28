set -x 

#python ./00.config.py
python ./01.interactive.e2e.py
python ./02.local.py
python ./03.aci.py
python ./04.dsvm.py
python ./05.spark.py
python ./07.sklearn.hd.py
python ./08.tf.hd.py
python ./10.o16n.py
python ./20.dask.py