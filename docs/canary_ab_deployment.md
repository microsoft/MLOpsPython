## Model deployment to AKS cluster with Canary deployment

[![Build Status](https://aidemos.visualstudio.com/MLOps/_apis/build/status/microsoft.MLOpsPython-Canary?branchName=master)](https://aidemos.visualstudio.com/MLOps/_build/latest?definitionId=133&branchName=master)

If your target deployment environment is a K8s cluster and you want to implement [Canary and/or A/B testing deployemnt strategies](http://adfpractice-fedor.blogspot.com/2019/04/deployment-strategies-with-kubernetes.html) you can follow this sample guidance.

**Note:** It is assumed that you have an AKS instance and configured ***kubectl*** to communicate with the cluster.

#### 1. Install Istio on a K8s cluster. 

This guidance uses [Istio](https://istio.io) service mesh implememtation to control traffic routing between model versions. The instruction on installing Istio is available [here](https://docs.microsoft.com/en-us/azure/aks/servicemesh-istio-install?pivots=client-operating-system-linux).

Having the Istio installed, figure out the Istio gateway endpoint on your K8s cluster:

```bash
GATEWAY_IP=$(kubectl get svc istio-ingressgateway -n istio-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
```

You don't need to create any Istio resources (e.g. Gateway or VirtualService) at this point. It will be handled by the AzDo pipeline that builds and deploys a scoring image.

#### 2. Set up variables

There are some extra variables that you need to setup in ***devopsforai-aml-vg*** variable group (see [getting started](./getting_started.md)):

| Variable Name               | Suggested Value                                      |
| --------------------------- | -----------------------------------------------------|
| K8S_AB_SERVICE_CONNECTION   | AzDo service connection to a K8s cluster             |
| K8S_AB_NAMESPACE            | Namespace in a K8s cluster to deploy the model       |
| IMAGE_REPO_NAME             | Image reposiory name (e.g. mlopspyciamlcr.azurecr.io)|


#### 3. Configure a pipeline to build and deploy a scoring Image

Import and run the [azdo-abtest-pipeline.yml](./.pipelines/azdo-abtest-pipeline.yml) multistage deployment pipeline.

The result of the pipeline will be a registered Docker image in the ACR repository attached to the AML Service:

![scoring image](./images/scoring_image.png)

The pipeline creates Istio Gateway and VirtualService and deploys the scoring image to the Kubernetes cluster. 

```bash
kubectl get deployments --namespace abtesting
NAME          READY   UP-TO-DATE   AVAILABLE   AGE
model-green   1/1     1            1           19h
```

#### 4. Build a new Scoring Image.

Change value of the ***SCORE_SCRIPT*** variable in the [azdo-abtest-pipeline.yml](./.pipelines/azdo-abtest-pipeline.yml) to point to ***scoreA.py*** and merge it to the master branch.

**Note:** ***scoreA.py*** and ***scoreB.py*** files used in this tutorial are just mockups returning either "New Model A" or "New Model B" respectively. They are used to demonstrate the concept of testing two scoring images with different models or scoring code. In real life you would implement a scoring file similar to [score.py](./../code/scoring/score.py) (see [getting started](./getting_started.md)).

It will automatically trigger the pipeline and deploy a new scoring image with the following stages implementing ***Canary*** deployment strategy:

| Stage               | Green Weight| Blue Weight| Description                                                     |
| ------------------- |-------------|------------|-----------------------------------------------------------------|
| Blue_0              |100          |0           |New image (blue) is deployed.<br>But all traffic (100%) is still routed to the old (green) image.|
| Blue_50             |50           |50          |Traffic is split between old (green) and new (blue) images 50/50.|
| Blue_100            |0            |100         |All traffic (100%) is routed to the blue image.|
| Blue_Green          |0            |100         |Old green image is removed. The new blue image is copied as green.<br>Blue and Green images are equal.<br>All traffic (100%) is routed to the blue image.|
| Green_100           |100          |0           |All traffic (100%) is routed to the green image.<br>The blue image is removed


**Note:** The pipeline performs the rollout without any pausing. You may want to configure [Approvals and Checks](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops&tabs=check-pass) for the stages on your environment for better experience of the model testing. The environment ***abtestenv*** will be added automatically to your AzDo project after the first pipeline run.

At each stage you can verify how the traffic is routed sending requests to $GATEWAY_IP/score with ***Postman*** or with ***curl***:

```bash
curl $GATEWAY_IP/score
```

You can also emulate a simple load test on the gateway with the ***load_test.sh***:

```bash
./charts/load_test.sh 10 $GATEWAY_IP/score
```

The command above sends 10 requests to the gateway. So if the pipeline has completted stage Blue_50, the result will look like this:

```bash
"New Model A"
"New Model A"
"New Model A"
"New Model B"
"New Model A"
"New Model B"
"New Model B"
"New Model A"
"New Model A"
"New Model A"
```

Despite what blue/green weights are configured now on the cluster, you can perform ***A/B testing*** and send requests directly to either blue or green images:

```bash
curl --header "x-api-version: blue" $GATEWAY_IP/score
curl --header "x-api-version: green" $GATEWAY_IP/score
```

or with the load_test.sh:

```bash
./charts/load_test.sh 10 $GATEWAY_IP/score blue
./charts/load_test.sh 10 $GATEWAY_IP/score green
```

In this case the Istio Virtual Service analyzes the request header and routes the traffic directly to the specified model version.
