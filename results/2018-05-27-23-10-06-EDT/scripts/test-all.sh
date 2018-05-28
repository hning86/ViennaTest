set -x 

echo "###################################"
echo "Starting time: date +%F-%H-%M-%S-%Z"
echo "###################################"

source activate daily

#python ./00.config.py

echo "##### 01.interactive.e2e.py ######"
python ./01.interactive.e2e.py

echo "##### 02.lcoal.py ################"
python ./02.local.py

echo "##### 03.aci.py ##################"
python ./03.aci.py

echo "##### 04.dsvm ####################"
python ./04.dsvm.py

echo "##### 05.spark ###################"
python ./05.spark.py

echo "##### 07.sklearn.hd.py ###########"
python ./07.sklearn.hd.py

echo "##### 08.tf.hd.py ################"
python ./08.tf.hd.py

echo "##### 10.o16n.py #################"
python ./10.o16n.py

echo "############ END #################"
