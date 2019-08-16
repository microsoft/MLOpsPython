#!/bin/bash

if [ $1 == 'run_train_pipeline.py' ]
then
  az login --service-principal -u $(SP_APP_ID) -p $(SP_APP_SECRET) --tenant $(TENANT_ID)
  python3 $1
else 
  python3 $1
fi