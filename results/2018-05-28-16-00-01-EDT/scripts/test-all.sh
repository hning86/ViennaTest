#set -x 

echo "###################################"
echo "START AT: $(date +%F-%T)"
echo "###################################"

source activate daily

#python ./00.config.py

echo ""
echo ""
echo "##### 01.interactive.e2e.py ######"
echo "$(date  +%F-%T)"
python ./01.interactive.e2e.py

echo ""
echo ""
echo "##### 02.lcoal.py ################"
echo "$(date  +%F-%T)"
python ./02.local.py

echo ""
echo ""
echo "##### 03.aci.py ##################"
echo "$(date  +%F-%T)"
python ./03.aci.py

echo ""
echo ""
echo "##### 04.dsvm ####################"
echo "$(date  +%F-%T)"
python ./04.dsvm.py

echo ""
echo ""
echo "##### 05.spark ###################"
echo "$(date  +%F-%T)"
python ./05.spark.py

echo ""
echo ""
echo "##### 07.sklearn.hd.py ###########"
echo "$(date  +%F-%T)"
python ./07.sklearn.hd.py

echo ""
echo ""
echo "##### 08.tf.hd.py ################"
echo "$(date  +%F-%T)"
python ./08.tf.hd.py

echo ""
echo ""
echo "##### 10.o16n.py #################"
echo "$(date  +%F-%T)"
python ./10.o16n.py

echo ""
echo ""
echo "########### END AT $(date +%F-%T)"
