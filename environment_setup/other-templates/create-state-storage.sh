#TF needs a storage account to save the .tfstate file. This is created here.
az group create -n rgName -l location
az storage account create -n $STATE_STORAGE_ACCOUNT_NAME -g rgName
