#TF needs a storage account to save the .tfstate file. This is created here.
az group create -n rgName -l rgLoc
az storage account create -n statestor -g rgName
