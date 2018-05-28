#set -x 

echo "###################################"
echo "START AT: $(date +%F-%T)"
echo "###################################"

source activate daily

#python ./00.config.py

echo ""
echo ""
echo "##### 01.interactive.e2e.py ######"
python ./01.interactive.e2e.py

echo ""
echo ""
echo "##### 02.lcoal.py ################"
python ./02.local.py

echo ""
echo ""
echo "##### 03.aci.py ##################"
python ./03.aci.py

echo ""
echo ""
echo "##### 04.dsvm ####################"
python ./04.dsvm.py

echo ""
echo ""
echo "##### 05.spark ###################"
python ./05.spark.py

echo ""
echo ""
echo "##### 07.sklearn.hd.py ###########"
python ./07.sklearn.hd.py

echo ""
echo ""
echo "##### 08.tf.hd.py ################"
python ./08.tf.hd.py

echo ""
echo ""
echo "##### 10.o16n.py #################"
python ./10.o16n.py

echo ""
echo ""
echo "########### END AT $(date +%F-%T)"
