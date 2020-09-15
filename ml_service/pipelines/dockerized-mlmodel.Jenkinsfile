pipeline {
    agent { label 'master' }
    environment {
        ML_IMAGE_FOLDER         = 'imagefiles'
        ML_CONTAINER_REGISTRY   = 'b8becdb6f4794d62a5a153653ba7bcdc'
        IMAGE_NAME              = 'mlmodelimage'
        RESOURCE_GROUP = 'upskill_devops_rg'
        MODEL_NAME = 'diabetes_regression_model.pkl'
        MODEL_VERSION = '1'
        SCORE_SCRIPT = 'scoring/score.py'
        WORKSPACE_NAME = 'mlops-upskill'
        SUBSCRIPTION_ID = '6c49a293-8733-477c-a12f-df2d12565703'
    }
    stages {
        stage('initialize') {
            steps {
                echo 'Remove the previous one!'
            }
            post {
                always {
                    deleteDir() /* clean up our workspace */
                }
            }
        }
        stage('generate_dockerfile') {
            steps {
                echo "Hello build ${env.BUILD_ID}"
                /*checkout scm*/
                checkout([$class: 'GitSCM', branches: [[name: '*/ml_model_uc76']],
                    userRemoteConfigs: [[url: 'https://github.com/Merlion-Crew/MLOpsPython.git/']]])
                /*sh 'az login --service-principal -u $ARM_CLIENT_ID -p $ARM_CLIENT_SECRET -t $ARM_TENANT_ID'
                sh 'az account set -s $ARM_SUBSCRIPTION_ID'*/

                azureCLI commands: [[exportVariablesString: '', script: "az account set -s ${SUBSCRIPTION_ID}"]], principalCredentialId: "${AZURE_SP}"
                
                sh '''#!/bin/bash -ex
                    source /home/azureuser/anaconda3/bin/activate mlopspython_ci
                    python3 -m ml_service.util.create_scoring_image
                '''
            }
        }
        stage('build') {
            steps {
                echo "Build docker images"

                sh '''#!/bin/bash -ex
                    az acr login --name $ML_CONTAINER_REGISTRY
                    docker build -t $NEXUS_DOCKER_REGISTRY_URL/$IMAGE_NAME:$BUILD_ID ./diabetes_regression/scoring/$ML_IMAGE_FOLDER/ 
                '''

                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'nexus-docker-repo',
                    usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                        
                    sh '''#!/bin/bash -ex
                        docker login -u $USERNAME --password $PASSWORD https://$NEXUS_DOCKER_REGISTRY_URL
                        docker push $NEXUS_DOCKER_REGISTRY_URL/$IMAGE_NAME:$BUILD_ID
                    '''
                }
            }
        }
    }
}