Model deployment to a Kubernetes cluster with Canary and A/B testing deployemnt strategies.

If you target deployment environment is a K8s cluster and you want to implement [Canary and/or A/B testing deployemnt strategies](http://adfpractice-fedor.blogspot.com/2019/04/deployment-strategies-with-kubernetes.html) you can follow this sample guidance:

**Note:** It is assumed that tou have an AKS instance and configured ***kubectl*** to communicate with the cluster.

1. Install Istio on a K8s cluster. 
This guidance uses Istio service mesh implememtation to control traffic routing between model versions. The instruction on installing Istio is available [here](https://docs.microsoft.com/en-us/azure/aks/servicemesh-istio-install?pivots=client-operating-system-linux).

Having the Istio installed, figure out the Istio gateway endpoint:

GATEWAY_IP=$(kubectl get svc istio-ingressgateway -n istio-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}')


2. Configure a pipeline to build a Scoring Image
Use [azdo-ci-image.yml](./.pipelines/azdo-ci-image.yml) to create a pipeline building a scoring image. 
{Picture}

3. Configure a Relese Pipeline.
Use [azdo-release-abtest-pipeline.yml](./.pipelines/azdo-release-abtest-pipeline.yml) to configure a multistage release pipeline:

{Picture}

Make sure that the release pipeline is configured to be triggered once the scoring image build is completed:

{Picture}

Approvals!!!!!

Manually run a pipeline builing scoring image. The result of the pipeline will be a registered Docker image in the ACR repository attached to the AML Service:

The release pipeline will be triggered automatically and it will deploy the scroring imnage to the Kubernetes cluster. 

4. Build a new Scoring Image.

Change the code in the [azdo-ci-image.yml](./.pipelines/azdo-ci-image.yml) and merge it to the master branch.
It will trigger the building pipeline and the release pipeline after that.

The release pipeline deploys a new scoring image with the following stages implementing Canary deployment strategy:

| Stage               | Green Weight| Blue Weight| Description|
| ------------------- |-------------|------------|-------------
| Blue_0              |100          |0           |New image (blue) is deployed. 
|                     |             |            |But all traffic (100%) is still routed to the old (green) image.
| ------------------- |-------------|------------|-------------
| Blue_50             |50           |50          |Traffic is split between old (green) and new (blue) images 50/50.
| ------------------- |-------------|------------|-------------
| Blue_100            |0            |100         |All traffic (100%) is routed to the blue image.
| ------------------- |-------------|------------|-------------
| Blue_Green          |0            |100         |Old green image is removed. The new blue image is copied as green.
|                     |             |            |Blue and Green images are equal. 
|                     |             |            |All traffic (100%) is routed to the blue image.
| ------------------- |-------------|------------|-------------
| Green_100           |100          |0           |All traffic (100%) is routed to the green image.
|                     |             |            |The blue image is removed

At ecah stage you can verify how the traffic is routed sending requests to $GATEWAY_IP/score with Postman or with 'curl':

curl $GATEWAY_IP/score

You can also emulate a simple load test on the gateway with the load_test.sh:

./charts/load_test.sh $GATEWAY_IP 10

The command above sends 10 requests to the gateway. So, if the pipeline has completted stage Blue_50, the result will look like this:
.
..
.
.
.

Despite what blue/green weights are configured now on the cluster you can perform A/B testing and send requests directly to either blue or green images:

./charts/load_test.sh $GATEWAY_IP 10 blue

./charts/load_test.sh $GATEWAY_IP 10 green

