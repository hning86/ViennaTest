#set -x 

ENV_NAME="$1"
export PATH=/home/ninghai/miniconda3/envs/$ENV_NAME/bin:$PATH

if [ "$ENV_NAME" = "daily" ] ; then
    echo "daily"
    # use eastus2euap workspace for daily
    cp aml_config/config.haieastus2euapws.json aml_config/config.json
    # use daily branch test code
    git stash
    echo "git checkout daily"
    git checkout daily
    git pull
elif [ "$ENV_NAME" = "candidate" ] ; then
    echo "candidate"
    # use eastus2 workspace
    cp aml_config/config.haieastus2ws3.json aml_config/config.json
    # use candidate branch for test code
    git stash
    echo "git checkout candidate"
    git checkout candidate
    git pull
else # preview
    echo "preview"
    # use eastus2 workspace for preview
    cp aml_config/config.haieastus2ws3.json aml_config/config.json
    # user master branch for test code
    git stash
    echo "git checkout master"
    git checkout master
    git pull
fi

echo "git status"
git branch
git status

echo "###################################"
echo "START AT: $(date +%F-%T)"
echo "###################################"

#python ./00.config.py

echo ""
echo ""
echo "##### 01.interactive.e2e.py ($(date +%F-%T)) ######"
python ./01.interactive.e2e.py

echo ""
echo ""
echo "##### 02.local.py ($(date +%F-%T)) ################"
python ./02.local.py

echo ""
echo ""
echo "##### 03.aci.py ($(date +%F-%T)) ##################"
python ./03.aci.py

echo ""
echo ""
echo "##### 04.dsvm ($(date +%F-%T)) ####################"
python ./04.dsvm.py

echo ""
echo ""
echo "##### 05.spark ($(date +%F-%T)) ###################"
python ./05.spark.py

echo ""
echo ""
echo "##### 07.sklearn.hd.py ($(date +%F-%T)) ###########"
python ./07.sklearn.hd.py

echo ""
echo ""
echo "##### 08.tf.hd.py ($(date +%F-%T)) ################"
python ./08.tf.hd.py

echo ""
echo ""
echo "##### 10.o16n.py ($(date + %F-%T)) #################"
python ./10.o16n.py


git checkout master
git pull
echo ""
echo ""
echo "###################################"
echo "########### END AT $(date +%F-%T)"
echo "###################################"
