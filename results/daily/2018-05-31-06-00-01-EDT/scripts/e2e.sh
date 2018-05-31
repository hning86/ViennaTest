set -x
SUB_NAME="Boston PM"
RG_NAME=aml-e2e-rg
WS_NAME=e2ews
PROJ_PATH=/tmp
PROJ_NAME=mnist_test
SAMPLE_URL=https://github.com/Azure/MachineLearningSamples-mnist
CUR_PATH=$(pwd)

az account set -s "$SUB_NAME"
az account show -o json
az group show -n $RG_NAME -o json

az ml project delete -n $PROJ_NAME -w $WS_NAME -g $RG_NAME -y
#az ml workspace delete -n $WS_NAME -g $RG_NAME
rm -rf $PROJ_PATH/$PROJ_NAME

az ml workspace create -n $WS_NAME -g $RG_NAME
az ml project create -n $PROJ_NAME --path $PROJ_PATH -w $WS_NAME -g $RG_NAME --template-url $SAMPLE_URL

cd $PROJ_PATH/$PROJ_NAME

az ml experiment submit -c local ./mnist_sklearn.py

# hack to workaround the docker.runconfig bug
sed -i '' 's/userManagedDependencies: true/userManagedDependencies: false/g' aml_config/docker.runconfig
#python -c "from azureml.core.runconfig import RunConfiguration; runconfig_object = RunConfiguration.load('docker'); run_config_object.environment.python.user_managed_dependencies = False; runconfig_object.save();"

az ml experiment prepare -c docker
az ml experiment submit -c docker ./mnist_sklearn.py

cd $CUR_PATH


