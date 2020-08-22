# カナリアリリースによるAKSクラスタへのモデルデプロイメント <!-- omit in toc -->

[![Build Status](https://aidemos.visualstudio.com/MLOps/_apis/build/status/microsoft.MLOpsPython-Canary?branchName=master)](https://aidemos.visualstudio.com/MLOps/_build/latest?definitionId=133&branchName=master)

対象のデプロイ環境がKubernetesクラスタで、[カナリアリリースおよび/またはA/Bテストのデプロイ戦略](http://adfpractice-fedor.blogspot.com/2019/04/deployment-strategies-with-kubernetes.html)を実装したい場合は、このサンプルガイドに従ってください。

- [前提条件](#前提条件)
- [K8s クラスタへの Istio のインストール](#k8s-クラスタへの-istio-のインストール)
- [変数の設定](#変数の設定)
- [スコアリングイメージをビルドして展開するためのパイプラインを設定します。](#スコアリングイメージをビルドして展開するためのパイプラインを設定します)
- [新しいスコアリングイメージのビルド](#新しいスコアリングイメージのビルド)

## 前提条件

このガイドを続ける前に、以下が必要です。

* Azure Kubernetes Service (AKS)](https://azure.microsoft.com/en-us/services/kubernetes-service) クラスタ
  * [Getting Started: Deploy the model to Azure Kubernetes Service](/docs/getting_started.md#deploy-the-model-to-azure-kubernetes-service)の例と同じクラスタである必要はありません。
  * クラスタは、Azure Machine Learningに接続している必要はありません。
  * 新しいクラスタをデプロイする場合は、[Quickstart: Deploy an Azure Kubernetes Service cluster using the Azure CLI](https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough)を参照してください。
* Azure Kubernetes サービス クラスタで認証されている Azure Container Registry インスタンス。
  * デプロイするチャートは、サービスプリンシパルを使用して認証されていることを前提としています。
  * 認証ガイドについては、[Azure Kubernetes ServiceからAzure Container Registryで認証する](https://docs.microsoft.com/en-us/azure/aks/cluster-container-registry-integration#configure-acr-integration-for-existing-aks-clusters)を参照してください。
* Azure DevOpsでは、Kubernetesクラスタへのサービス接続を指します。
  * 名前空間がない場合は、'abtesting'という名前の名前を作成してください。

## K8s クラスタへの Istio のインストール

[Istio](https://istio.io)のサービスメッシュ実装を使用して、モデルバージョン間のトラフィックルーティングを制御することになります。[Azure Kubernetes Service (AKS) に Istio をインストールして使用する](https://docs.microsoft.com/azure/aks/servicemesh-istio-install?pivots=client-operating-system-linux) の手順に従ってください。

Istioをインストールしたら、K8sクラスタ上のIstioゲートウェイエンドポイントを把握します。

```bash
GATEWAY_IP=$(kubectl get svc istio-ingressgateway -n istio-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
```

この時点では、Istioリソース（GatewayやVirtualServiceなど）を作成する必要はありません。スコアリングイメージをビルドしてデプロイする AzDo パイプラインによって処理されます。

## 変数の設定

***devopsforai-aml-vg*** 変数グループで設定する必要がある追加の変数があります ( [MLOpsPythonの開始](./getting_started.md) を参照してください)。:

| 変数名             | 推奨値       | 概要                                         |
|---------------------------|-----------------------|-----------------------------------------------------------|
| K8S_AB_SERVICE_CONNECTION | mlops-aks             | Kubernetes クラスタへのサービス接続の名前 |
| K8S_AB_NAMESPACE          | abtesting             | モデルデプロイのためのKubernetes名前空間                 |
| IMAGE_REPO_NAME           | [ACRのDNS 名称] | イメージレポジトリ名 (例: mlopspyciamlcr.azurecr.io)     |

## スコアリングイメージをビルドして展開するためのパイプラインを設定します。

[abtest.yml](./.pipelines/abtest.yml)のマルチステージデプロイメントパイプラインをインポートして実行します。

パイプラインが正常に完了すると、Azure ML サービスに接続された ACR リポジトリに登録された Docker イメージが表示されます。:

![scoring image](./images/scoring_image.png)

パイプラインでは、Istio GatewayとVirtualServiceを作成し、スコアリングイメージをKubernetesクラスタにデプロイします。

```bash
kubectl get deployments --namespace abtesting
NAME          READY   UP-TO-DATE   AVAILABLE   AGE
model-green   1/1     1            1           19h
```

## 新しいスコアリングイメージのビルド

[abtest.yml](./.pipelines/abtest.yml)の***SCORE_SCRIPT*** 変数の値を***scoring/scoreA.py*** を指すように変更し、マスターブランチにマージしてください。

**注意:** このチュートリアルで使用されている ***scoreA.py*** と ***scoreB.py*** ファイルは、それぞれ "New Model A" または "New Model B" を返すモックアップです。これらのファイルは、異なるモデルやスコアリングコードで2つのスコアリングイメージをテストするというコンセプトを示すために使用されます。実際には、[score.py](./.../code/scoring/score.py)のようなスコアリングファイルを実装します（[MLOpsPythonの開始](./getting_started.md)ガイドを参照してください）。

ここでは自動的にパイプラインをトリガーし、***カナリアリリース***のデプロイ戦略を実装する次の段階で新しいスコアリングイメージをデプロイします。:

| Stage      | Green Weight | Blue Weight | 概要                                                                                                                                               |
|------------|--------------|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Blue_0     | 100          | 0           | 新しいイメージ(Blue)が展開されています。<br>すべてのトラフィック(100%)はまだ古いイメージ(Green)にルーティングされています。    |
| Blue_50    | 50           | 50          | トラフィックは旧（Green）と新（Blue）イメージを50/50で分けています。                                                                                        |
| Blue_100   | 0            | 100         | すべてのトラフィック(100%)は新しいイメージ(Blue)にルーティングされます。                                                                                                           |
| Blue_Green | 0            | 100         | 古いイメージ(Green)が削除されます。<br>新しいイメージ(Blue)を古いイメージ(Green)としてコピーします。<br>新しいイメージ(Blue)と古いイメージ(Green)は同じとなります。<br>すべてのトラフィック(100%)は新しいイメージ(Blue)にルーティングされます。 |
| Green_100  | 100          | 0           | すべてのトラフィック(100%)は古いイメージ(Green)にルーティングされます。<br>新しいイメージ(Blue)は削除されます。                                                                           |

**注：** パイプラインは一時停止なしでロールアウトを行います。モデルテストをより良く体験するために、[Approvalvals and Checks](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops&tabs=check-pass)を設定することをおすすめします。環境 ***abtestenv*** は、最初のパイプライン実行後、自動的にAzDoプロジェクトに追加されます。

各ステージでは、トラフィックがどのようにルーティングされているか、***Postman*** や***curl*** で$GATEWAY_IP/scoreにリクエストを送信するかを確認することができます。

```bash
curl $GATEWAY_IP/score
```

また、***load_test.sh***でゲートウェイ上の単純な負荷テストをエミュレートすることもできます。:

```bash
./charts/load_test.sh 10 $GATEWAY_IP/score
```

上のコマンドはゲートウェイに10個のリクエストを送信します。そのため、パイプラインがステージBlue_50を完了した場合、結果は以下のようになります。:

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

クラスタに設定されている青/緑のウェイト値に関係なく、** *A/Bテスト***を実行し、BlueまたはGreenのどちらかのイメージに直接リクエストを送信することができます。:

```bash
curl --header "x-api-version: blue" $GATEWAY_IP/score
curl --header "x-api-version: green" $GATEWAY_IP/score
```

または load_test.sh スクリプトを使用します。:

```bash
./charts/load_test.sh 10 $GATEWAY_IP/score blue
./charts/load_test.sh 10 $GATEWAY_IP/score green
```

この場合、Istio 仮想サービスは要求ヘッダーを分析し、トラフィックを指定されたモデルバージョンに直接ルーティングします。
