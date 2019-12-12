#!/bin/bash

for ((i=1;i<=$1;i++))
do
	curl --header "x-api-version: $3" $2
	echo
    sleep .2
done