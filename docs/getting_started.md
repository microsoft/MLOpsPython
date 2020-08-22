# MLOpsPythonの開始 <!-- omit in toc -->

このガイドでは、MLプロジェクト **_diabetes_regression_** のサンプルでMLOpsPythonを動作させる方法を示します。この開始ガイド内のステップが完了したとき、このプロジェクトは糖尿病を予測する線形回帰モデルを作成し、CI/CD DevOpsのプラクティスでモデルのトレーニングと提供を可能にします。

このテンプレート構造を独自のモデルコードに利用したい場合は、[カスタムモデル](custom_model.md)ガイドに従ってください。独自のモデルコードを使用するためのテンプレート変換を実行する前に、最初にこの入門ガイドを完了し、ACIデプロイを介してデプロイされた糖尿病モデルがあなたの環境で動作していることを確認することをお勧めします。

- [Azure DevOpsのセットアップ](#azure-devopsのセットアップ)
  - [Azure Machine Learning 拡張機能のインストール](#azure-machine-learning-拡張機能のインストール)
- [コードの入手](#コードの入手)
- [パイプライン用の変数グループの作成](#パイプライン用の変数グループの作成)
  - [変数の内容](#変数の内容)
- [Azure Pipelinesを使用したリソースの構成](#azure-pipelinesを使用したリソースの構成)
  - [Azure Resource Manager用のAzure DevOpsサービス接続を作成する](#azure-resource-manager用のazure-devopsサービス接続を作成する)
  - [IaC パイプラインの作成](#iac-パイプラインの作成)
- [Azure ML ワークスペース用の Azure DevOps サービス接続の作成](#azure-ml-ワークスペース用の-azure-devops-サービス接続の作成)
- [ビルド、リリーストリガー、リリースのマルチステージパイプラインの設定](#ビルドリリーストリガーリリースのマルチステージパイプラインの設定)
  - [モデルCI、トレーニング、評価、登録パイプラインの設定](#モデルciトレーニング評価登録パイプラインの設定)
    - [モデル CI](#モデル-ci)
    - [モデルトレーニング](#モデルトレーニング)
    - [パイプラインアーティファクトの作成](#パイプラインアーティファクトの作成)
  - [リリース デプロイメントとバッチ スコアリング パイプライン(両方、もしくは片方)を設定する](#リリース-デプロイメントとバッチ-スコアリング-パイプライン両方もしくは片方を設定する)
  - [リリースデプロイメントパイプラインの設定](#リリースデプロイメントパイプラインの設定)
    - [ACIへのデプロイ](#aciへのデプロイ)
  - [バッチスコアリングパイプラインの設定](#バッチスコアリングパイプラインの設定)
    - [バッチスコアリング CI](#バッチスコアリング-ci)
    - [バッチスコアリングモデル](#バッチスコアリングモデル)
- [追加シナリオ](#追加シナリオ)
  - [モデルをAzure Kubernetes Serviceにデプロイする](#モデルをazure-kubernetes-serviceにデプロイする)
    - [Azure Kubernetes SeriviceでのWebサービス認証](#azure-kubernetes-seriviceでのwebサービス認証)
  - [モデルをAzure App Service（Azure Web App for containers）にデプロイする](#モデルをazure-app-serviceazure-web-app-for-containersにデプロイする)
  - [Rを使用したパイプラインの例](#rを使用したパイプラインの例)
  - [観測とモニタリング](#観測とモニタリング)
  - [リソースをクリーンアップする](#リソースをクリーンアップする)
- [次のステップ: 自身のプロジェクトとの統合](#次のステップ-自身のプロジェクトとの統合)
  - [追加の変数と設定](#追加の変数と設定)
    - [より多くの変数オプション](#より多くの変数オプション)
    - [ローカルでの構成](#ローカルでの構成)

## Azure DevOpsのセットアップ

Azure DevOps を使用して、ビルド、モデルトレーニング、スコアリングサービスのリリースステージを持つ多段階パイプラインを実行します。まだAzure DevOps組織を持っていない場合は、以下の手順に従って組織を作成してください。  
[Quickstart: Create an organization or project collection](https://docs.microsoft.com/ja-jp/azure/devops/organizations/accounts/create-organization?view=azure-devops).

すでにAzure DevOps組織を持っている場合は、以下の手順に従って新しいプロジェクトを作成してください。  
 [Create a project in Azure DevOps and TFS](https://docs.microsoft.com/ja-jp/azure/devops/organizations/projects/create-project?view=azure-devops).

### Azure Machine Learning 拡張機能のインストール

 [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.vss-services-azureml)から、Azure DevOps組織に**Azure Machine Learning**拡張機能をインストールします。

This extension contains the Azure ML pipeline tasks and adds the ability to create Azure ML Workspace service connections.

この拡張機能には、Azure ML のパイプラインタスクが含まれていることに加え、Azure ML Workspaceとのサービス接続を作成する機能が追加されています。

## コードの入手
 [リポジトリテンプレート](https://github.com/microsoft/MLOpsPython/generate)を使用して、自分の GitHub リポジトリにフォークしながら履歴を消去することをお勧めします。できあがったリポジトリは、このガイドや自分の実験に使うことができます。

## パイプライン用の変数グループの作成

MLOpsPythonはパイプラインを実行する前にいくつかの変数を設定する必要があります。
複数のパイプラインやパイプラインステージで再利用する値を保存するために、Azure DevOpsで_変数グループを作成する必要があります。
値を [Azure DevOpsに直接格納する](https://docs.microsoft.com/ja-jp/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=designer#create-a-variable-group)か、サブスクリプションでAzure Key Vaultに接続します。変数グループを作成してパイプラインにリンクする方法の詳細については、[変数グループの追加と使用](https://docs.microsoft.com/ja-jp/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=yaml#use-a-variable-group) のドキュメントをチェックしてください。

以下に示すように、**Pipelines**セクションの**Library**に移動します。

![Library Variable Groups](./images/library_variable_groups.png)

**`devopsforai-aml-vg`**という名前の変数グループを作成します。このリポジトリのYAMLパイプライン定義は、この名前により変数グループを参照します。

変数グループには、以下の必須変数が含まれている必要があります。**まだ存在しないAzureリソースは、後述の[Provisioning resources using Azure Pipelines](#provisioning-resources-using-azure-pipelines)の手順で作成されます。**

| 変数名            | 推奨の値           | 概要                                                                                                           |
| ------------------------ | ------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| BASE_NAME                | [任意のプロジェクト名称]       | 作成されるリソースの一意の接頭辞 - 最大10文字、文字、数字のみ                                         |
| LOCATION                 | centralus                 | [Azure location](https://azure.microsoft.com/ja-jp/global-infrastructure/locations/), スペースなし
| RESOURCE_GROUP           | mlops-RG                  | Azure リソースグループの名前                                                                                                   |
| WORKSPACE_NAME           | mlops-AML-WS              | Azure ML Workspace の名前                                                                                                     |
| AZURE_RM_SVC_CONNECTION  | azure-resource-connection | [Azure Resource Manager サービス接続](#create-an-azure-devops-service-connection-for-the-azure-resource-manager) の名前 |
| WORKSPACE_SVC_CONNECTION | aml-workspace-connection  | [Azure ML Workspace サービス接続ー](#create-an-azure-devops-azure-ml-workspace-service-connection) の名前                 |
| ACI_DEPLOYMENT_NAME      | mlops-aci                 | [Azure Container Instances](https://azure.microsoft.com/ja-jp/services/container-instances/) の名前                           |
| SCORING_DATASTORE_STORAGE_NAME      | [任意のプロジェクト名称]scoredata                 | [Azure Blob Storage Account](https://docs.microsoft.com/ja-jp/azure/storage/blobs/) の名前 (オプション)                          |
| SCORING_DATASTORE_ACCESS_KEY      |                  | [Azure Storage Account のアクセスキー](https://docs.microsoft.com/ja-jp/rest/api/storageservices/authorize-requests-to-azure-storage) (オプション)                          |

変数グループの設定で **Allow access to all pipelines** のチェックボックスを選択していることを確認してください。

より多くの変数を使用して微調整することができますが、今回の例では上記の変数で十分です。詳細は、[追加の変数と設定](#追加の変数と設定)セクションを参照してください。

### 変数の内容

**BASE_NAME** は、Azure リソースの命名の接頭辞として使用され、一意である必要があります。Azureサブスクリプションを共有する場合、接頭辞を使用することで、Azure Blob StorageやレジストリDNSなど、一意の名前を必要とするリソース名のコンフリクトを回避することができます。作成されたリソースが一意の名前を持つように、BASE_NAMEを一意の名前に設定するようにしてください。BASE_NAMEの値の長さは10文字を超えてはならず、文字と数字のみでなければなりません。

**LOCATION** はデプロイされるリソースの[Azure location](https://azure.microsoft.com/ja-jp/global-infrastructure/locations/)の名前です。名前にはスペースを入れてはいけません。例えば、central, westus, westus2などです。

**RESOURCE_GROUP** は、ソリューションのためのAzureリソースを保持するリソースグループの名前として使用されます。既存の Azure ML ワークスペースを提供する場合は、この値を対応するリソース グループ名に設定します。

**WORKSPACE_NAME** は、Azure Machine Learning ワークスペースを作成するために使用します。既存のAzure MLワークスペースがあれば、ここで入力することができます。

**AZURE_RM_SVC_CONNECTION** は、Azureリソースマネージャを介してAzure MLワークスペースと関連リソースを作成するAzure DevOpsの[Azure Pipeline](./environment_setup/iac-create-environment-pipeline.yml)で使用されます。[後述の手順](#azure-resource-manager用のazure-devopsサービス接続を作成する)で接続を作成します。

**WORKSPACE_SVC_CONNECTION** は、[Azure ML ワークスペースのサービス接続](#azure-ml-ワークスペース用の-azure-devops-サービス接続の作成)を参照するために使用します。[ワークスペースのプロビジョニング](#azure-pipelinesを使用したリソースの構成)の後に、後述の[Azure ML ワークスペース用の Azure DevOps サービス接続の作成](#azure-ml-ワークスペース用の-azure-devops-サービス接続の作成)のセクションを行って接続を作成します。

**ACI_DEPLOYMENT_NAME** は、[Azure Container Instances](https://azure.microsoft.com/ja-jp/services/container-instances/)へのデプロイ時のスコアリング用サービスの命名に使用されます。

**SCORING_DATASTORE_STORAGE_NAME** は、バッチ スコアリングの入力として使用されるデータと、バッチ スコアリングの出力データの両方を格納する Azure Blob Storage アカウントの名前です。この変数はオプションで、バッチ スコアリング機能を使用する場合にのみ必要です。このリソースはオプションなので、下記のリソース プロビジョニング パイプラインではこのリソースは自動的に作成されず、使用する前に手動で作成する必要があることに注意してください。

**SCORING_DATASTORE_ACCESS_KEY** は、上記のスコアリングデータを格納するAzureストレージアカウントのアクセスキーです。アクセスキーをプレーンテキストで保存しないように、この変数をAzure KeyVaultにリンクすることを検討するとよいでしょう。この変数はオプションであり、バッチスコアリング機能を使用する予定がある場合にのみ必要です。

## Azure Pipelinesを使用したリソースの構成

必要なすべてのAzureリソース（リソースグループ、Azure ML Workspace, Container Registryなど）を作成する最も簡単な方法は、[ARM templatesを利用した **Infrastructure as Code (IaC)** パイプライン](./environment_setup/iac-create-environment-pipelin-arm.yml) または[Terraform templatesを利用したパイプライン](./environment_setup/iac-create-environment-pipelin-tf.yml)を使用することです。パイプラインは、[ARM templates](./environment_setup/arm-templates/cloud-environment.json)、または [Terraform templates](./environment_setup/tf-templates) に基づいて、必要なリソースの設定を行います。

**注:** バッチスコアリングに必要なAzure Blobのストレージアカウントはオプションのため、上記のリソース構成用のパイプラインでは自動的に作成されず、使用前に手動で作成する必要があります。

### Azure Resource Manager用のAzure DevOpsサービス接続を作成する

 [IaC 構成パイプライン](../environment_setup/iac-create-environment-pipeline.yml) には **Azure Resource Manager** [サービス接続](https://docs.microsoft.com/ja-jp/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml#create-a-service-connection)が必要です。:

![Create service connection](./images/create-rm-service-connection.png)

**`Resource Group`** 欄は空白のままにしてください。

**注:**Azure Resource Manager サービス接続スコープを作成するには、サブスクリプションに「所有者」または「ユーザーアクセス管理者」の権限が必要です。
また、Azure ADテナントにアプリケーションを登録するのに十分な権限が必要になります。そのプリンシパルは、サブスクリプションに対して「共同作成者」の権限を持っている必要があります。

###  IaC パイプラインの作成

Azure DevOpsプロジェクト上で、フォークしたリポジトリからビルドパイプラインを作成します。:

![Build connect step](./images/build-connect.png)

**既存のAzure Pipelines YAMLファイル** オプションを選択し、ARMテンプレートやTerraformを使用してインフラストラクチャをデプロイするかどうかに応じて、[/environment_setup/iac-create-environment-pipeline-arm.yml](../environment_setup/iac-create-environment-pipeline-arm.yml)または、[/environment_setup/iac-create-environment-pipeline-tf.yml](../environment_setup/iac-create-environment-pipeline-tf.yml)にパスを設定します。:

![Configure step](./images/select-iac-pipeline.png)

If you decide to use Terraform, make sure the ['Terraform Build & Release Tasks' from Charles Zipp](https://marketplace.visualstudio.com/items?itemName=charleszipp.azure-pipelines-tasks-terraform) is installed.

Having done that, run the pipeline:

![IaC run](./images/run-iac-pipeline.png)

Check that the newly created resources appear in the [Azure Portal](https://portal.azure.com):

![Created resources](./images/created-resources.png)

## Azure ML ワークスペース用の Azure DevOps サービス接続の作成

この時点で、Azure ML ワークスペースが作成されているはずです。Azure Resource Manager のサービス接続と同様に、Azure ML ワークスペース用に追加で作成する必要があります。

Azure MLトレーニングパイプラインの実行を有効にするために、[Machine Learning Extension](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.vss-services-azureml)のガイドを使用して、Azure MLワークスペースに新しいサービス接続を作成します。接続名は、上記の変数グループで設定した `WORKSPACE_SVC_CONNECTION` と一致する必要があります (例: 'aml-workspace-connection' )。

![Created resources](./images/ml-ws-svc-connection.png)

**注:** 先ほど作成したAzure Resource Managerのサービス接続と同様に、Azure Machine Learningのワークスペーススコープでサービス接続を作成するには、ワークスペースに「所有者」または「ユーザーアクセス管理者」の権限が必要です。
Azure ADのテナントにアプリケーションを登録するには十分な権限が必要ですが、Azure ADの管理者からサービスプリンシパルのIDとシークレットを取得することもできます。そのプリンシパルは、Azure ML ワークスペース上で「共同作成者」権限を持っている必要があります。

## ビルド、リリーストリガー、リリースのマルチステージパイプラインの設定

必要なAzureリソースとサービス接続をすべてプロビジョニングしたら、機械学習モデルを本番環境にトレーニング(CI)とデプロイ(CD)するためのパイプラインを設定できます。さらに、バッチスコアリングのためのパイプラインをセットアップすることができます。

1. **モデル CI, トレーニング, 評価, 登録** - GitHub上のマスターブランチへのコード変更時にトリガーされます。リンティング、ユニットテスト、コードカバレッジを実行し、トレーニングパイプラインを公開して実行します。評価後に新しいモデルが登録された場合、モデルのJSONメタデータを含むビルドアーティファクトを作成します。定義:[diabetes_regression-ci.yml](./.pipelines/diabetes_regression-ci.yml)
2. **リリースデプロイメント** - 前段のパイプラインのアーティファクトを消費し、モデルを [Azure Container Instances (ACI)](https://azure.microsoft.com/ja-jp/services/container-instances/)、[Azure Kubernetes Service (AKS)](https://azure.microsoft.com/ja-jp/services/kubernetes-service)、または [Azure App Service](https://docs.microsoft.com/ja-jp/azure/machine-learning/service/how-to-deploy-app-service) 環境のいずれかにデプロイします。その他のデプロイメントタイプについては、[追加シナリオ](#追加シナリオ)を参照してください。
定義: [diabetes_regression-cd.yml](./.pipelines/diabetes_regression-cd.yml)
   - **注意:** パイプライン定義を編集して、使用されていないステージを削除します。例えば、Azure Container Instances と Azure Kubernetes Service のみにデプロイする場合は、未使用の `Deploy_Webapp` ステージを削除します。
3. **バッチスコアリングコードの継続的インテグレーション** - は、モデル学習パイプラインのアーティファクトを消費します。リンティング、ユニットテスト、コードカバレッジを実行し、バッチスコアリングパイプラインを公開し、公開されたバッチスコアリングパイプラインを呼び出してモデルをスコアリングします。

これらのパイプラインは、パイプラインのステップを達成するためにAzure Pipelinesエージェント上のDockerコンテナを使用します。コンテナイメージ ***mcr.microsoft.com/mlops/python:latest*** は [ このDockerfile](../environment_setup/Dockerfile) でビルドされ、MLOpsPython と ***diabetes_regression*** に必要なすべての依存関係がインストールされています。このイメージは、カスタムDockerイメージに事前作成された環境を追加した例です。この環境は、どのビルドエージェント、VM、ローカルマシンでも同じ環境であることが保証されています。プロジェクトでは、ユースケースに必要な依存関係とツールだけを含む独自のDockerイメージを構築したい場合があり、イメージはより小さく、より速く、チームがメンテナンス可能です。

### モデルCI、トレーニング、評価、登録パイプラインの設定

Azure DevOpsプロジェクトで、[diabetes_regression-ci.yml](./.pipelines/diabetes_regression-ci.yml)をベースにした新しいビルドパイプラインを作成して実行します。
フォークしたリポジトリでパイプラインの定義を確認してください。

(次のセクションの) リリースデプロイメントパイプラインを使用する場合、このパイプラインの名前を `Model-Train-Register-CI` に変更する必要があります。

パイプラインが終了したら、実行結果を確認します。:

![Build](./images/model-train-register.png)

パイプラインのアーティファクトについても同様です。:

![Build](./images/model-train-register-artifacts.png)

また、[Azure Machine Learning Studio](https://ml.azure.com/)の**mlops-AML-WS**ワークスペースで公開されているトレーニングパイプラインを確認してください。:

![トレーニングパイプライン](./images/training-pipeline.png)

これで、マスターブランチに変更があるたびに自動的にトリガーされるトレーニング用のビルドパイプラインがセットアップされました。

パイプラインが完了すると、**MLワークスペース**に新しいモデルが表示されます。:

![学習済みモデル](./images/trained-model.png)

トレーニングパイプラインの自動トリガーを無効にするには、`.pipelines\diabetes_regression-ci.yml` パイプライン内の `auto-trigger-training` 変数を `false` に変更してください。 また、パイプラインの実行時に変数をオーバーライドすることもできます。

パイプラインのステージは以下のようにまとめられています。:

#### モデル CI

- リンティング（コード品質分析)
- ユニットテストとコードカバレッジ分析
- _ML Workspace_ に _ML Training Pipeline_ を構築して公開します。

#### モデルトレーニング

- 前ステージで公開した_ML Training Pipeline_のIDを決定します。
- _ML Training Pipeline_ をトリガーにして、完了を待機します。
  - これは **エージェントレス** のジョブです。CIパイプラインは、エージェントリソースを使用せずに何時間、あるいは何日もMLパイプラインの完了を待つことができます。
- _MLトレーニングパイプライン_ によって新しいモデルが登録されたかどうかを判断します。
  - モデルの評価で、新しいモデルが以前のモデルよりも良いパフォーマンスを発揮しないと判断された場合、新しいモデルは登録されず、_MLトレーニングパイプライン_ は**キャンセル**されます。この場合、'Determine if evaluation succeeded and new model is registered' stepの下の'Train Model' jobで'**Model was not registered for this run.**'というメッセージが表示されます。
  - 評価ロジックは [evaluate_model.py](./diabetes_regression/evaluate/evaluate_model.py#L118) を参照してください。
  - この動作やその他の動作を設定するには、[追加の変数と設定](#追加の変数と設定)を参照してください。

#### パイプラインアーティファクトの作成

- 登録されているモデルの情報を取得する
- モデル情報を含む `model.json` ファイルを含む `model` という名前のパイプラインアーティファクトを作成する。

### リリース デプロイメントとバッチ スコアリング パイプライン(両方、もしくは片方)を設定する

---
**前提条件**

これらのパイプラインを使用するには

1. モデルCI、トレーニング、評価、および登録パイプラインをセットアップするための手順に従います。
1. モデルCI/トレーニング/評価/登録パイプラインの名前を `Model-Train-Register-CI` に変更する必要があります。

これらのパイプラインはモデルCIパイプラインに依存しており、名前を参照しています。

モデルCIパイプラインの名前を変更したい場合は、CDとバッチスコアリングパイプライン用のymlのこのセクションを編集しなければなりません。ここでは、`source: Model-Train-Register-CI`と書かれているので、この設定を変更後の名前を使うように編集する必要があります。
```
trigger: none
resources:
  containers:
  - container: mlops
    image: mcr.microsoft.com/mlops/python:latest
  pipelines:
  - pipeline: model-train-ci
    source: Model-Train-Register-CI # トリガーとなるパイプラインの名前
    trigger:
      branches:
        include:
        - master
```

---

リリースデプロイメントとバッチスコアリングのパイプラインには、次のような動作があります。

- パイプラインは、マスターブランチの Model-Train-Register-CI パイプラインが完了すると、**自動的に**トリガーされます。
- パイプラインは、Model-Train-Register-CI パイプラインの最新の成功したビルドを使用するようにデフォルト設定されます。そのビルドで生成されたモデルをデプロイします。
- パイプラインを手動で実行する際に `Model-Train-Register-CI` ビルド ID を指定することができます。これはビルドのURLで見つけることができ、そのビルドから登録されたモデルもビルドIDでタグ付けされます。これはモデルのトレーニングや登録をスキップし、`Model-Train-Register-CI` ビルドで正常に登録されたモデルをデプロイ/スコアするのに便利です。

### リリースデプロイメントパイプラインの設定

Azure DevOpsプロジェクトで、[diabetes_regression-cd.yml](./.pipelines/diabetes_regression-cd.yml)をベースにした新しいビルドパイプラインを作成して実行します。
パイプライン定義をフォークしてください。

最初の実行では、`Model-Train-Register-CI` パイプラインによって作成された最新のモデルを使用します。

パイプラインが終了したら、実行結果を確認してください。:

![Build](./images/model-deploy-result.png)

特定のビルドのモデルを指定するには、`Model Train CI Build Id`パラメータに使用したいビルドIDを設定します。:

![Build](./images/model-deploy-configure.png)

パイプラインの実行が始まると、`Model-Train-Register-CI` パイプラインからダウンロードしたモデル名とバージョンが表示されます。:

![Build](./images/model-deploy-get-artifact-logs.png)

パイプラインには以下のようなステージがあります。:

#### ACIへのデプロイ

- [Azure Container Instances](https://azure.microsoft.com/ja-jp/services/container-instances/)のQA環境にモデルをデプロイします。
- スモークテスト
  - このテストでは、サンプルのクエリをスコアリングウェブサービスに送信し、それが期待されるレスポンスを返すかどうかを検証します。例としては、[スモークテストコード](./ml_service/util/smoke_test_scoring_service.py)を参照してください。

### バッチスコアリングパイプラインの設定

Azure DevOpsプロジェクトで、[diabetes_regression-batchscoring-ci.yml](./.pipelines/diabetes_regression-batchscoring-ci.yml)に基づいた新しいビルドパイプラインを作成して実行します。
パイプラインの定義をフォークしたリポジトリで確認してください。

パイプラインが終了したら、実行結果を確認します。:

![Build](./images/batchscoring-ci-result.png)

また、[Azure Portal](https://portal.azure.com/)の**mlops-AML-WS**ワークスペースで公開されているバッチスコアリングパイプラインを確認してください。:

![バッチ スコアリング パイプライン](./images/batchscoring-pipeline.png)

これでバッチスコアリング用のビルドパイプラインが設定され、マスターブランチに変更があるたびに自動的にトリガーされるようになりました。

パイプラインのステージは以下のようにまとめられています。:

#### バッチスコアリング CI

- リンティング（コード品質分析
- ユニットテストとコードカバレッジ分析
- *ML Workspace* に *ML Batch Scoring Pipeline*を構築して公開します。

#### バッチスコアリングモデル

- モデル名（必須）、モデルバージョン、モデルタグ名、モデルタグ値のバインドされたパイプラインパラメータに基づいて、使用するモデルを決定します。
  - Azure DevOps パイプライン経由で実行する場合、バッチスコアリングパイプラインは入力として使用される `Model-Train-Register-CI` ビルドからモデル名とバージョンを取得します。
  - モデルのバージョンなしでローカルで実行された場合、バッチスコアリングパイプラインはモデルの最新バージョンを使用します。
- *ML バッチスコアリングパイプライン* をトリガーし、完了を待機します。
  - これは**エージェントレス**ジョブです。CIパイプラインは、エージェントリソースを使用せずに、MLパイプラインの完了を何時間も、あるいは何日も待つことができます。
- *SCORING_DATASTORE_INPUT_* 設定変数で指定されるスコアリング入力データを使用します。
- スコアリングが完了すると、*SCORING_DATASTORE_OUTPUT_* 設定変数で指定した場所の同じブロブストレージでスコアが利用可能になります。

**注:** スコアリングデータストアがまだ設定されていない場合でも、データフォルダ内のスコアリング入力データファイルを指定することで、バッチスコアリングを試すことができます。SCORING_DATASTORE_INPUT_FILENAME変数にファイル名を設定してください。この方法では、スコア出力はMLワークスペースのデフォルトのデータストアに書き込まれます。

## 追加シナリオ

これで、MLOpsPythonを使い始めるためのパイプラインが完成しました。以下に、あなたのシナリオに適した機能をいくつか紹介します。

### モデルをAzure Kubernetes Serviceにデプロイする

MLOpsPythonは[Azure Kubernetes Service](https://azure.microsoft.com/ja-jp/services/kubernetes-service)にもデプロイできます。

Azure Kubernetes Service上にクラスタを作成することはこのチュートリアルの範囲外ですが、セットアップ情報は[Quickstart: Deploy an Azure Kubernetes Service (AKS) cluster using the Azure portal](https://docs.microsoft.com/ja-jp/azure/aks/kubernetes-walkthrough-portal#create-an-aks-cluster) ページに掲載されています。

> **_注_**
>
> 対象のデプロイ環境がKubernetesクラスタで、カナリアリリースやA/Bテストのデプロイ戦略を実装したい場合は、この[チュートリアル]をチェックしてください(./canary_ab_deployment.md)。

Azure Kubernetes Service にデプロイする前に変更を検証するために可能な簡単な方法なので、Azure Container Instances のデプロイをアクティブにしておきます。

変数タブで、変数グループ (`devopsforai-aml-vg`) を編集します。変数グループの定義で、これらの変数を追加します。

| 変数名       | 推奨値  |
| ------------------- | --------------- |
| AKS_COMPUTE_NAME    | aks             |
| AKS_DEPLOYMENT_NAME | mlops-aks       |

Azure ML ワークスペースの Azure Kubernetes Service クラスタを参照する推論クラスタの  _Compute name_  に **AKS_COMPUTE_NAME** を設定します。

Azure Container Instancesへのデプロイに成功したら、次はモデルをKubernetesにデプロイしてスモークテストを実行します。

![build](./images/multi-stage-aci-aks.png)

デプロイ前に[手動の承認](https://docs.microsoft.com/ja-jp/azure/devops/pipelines/process/approvals)を有効にすることを検討してください。

#### Azure Kubernetes SeriviceでのWebサービス認証

Azure Kubernetes Service にデプロイする場合、デフォルトではキーベース認証が有効になっています。また、トークンベースの認証を有効にすることもできます。トークンベース認証では、クライアントが Azure Active Directory アカウントを使用して認証トークンを要求する必要があり、トークンはデプロイされたサービスへのリクエストに使用されます。AKSサービス上に配置されたMLのWebサービスで認証を行う方法の詳細については、[Smoke Test](./ml_service/util/smoke_test_scoring_service.py)またはAzureのドキュメントの[Webサービス認証](https://docs.microsoft.com/ja-jp/azure/machine-learning/how-to-deploy-azure-kubernetes-service#web-service-authentication)を参照してください。

### モデルをAzure App Service（Azure Web App for containers）にデプロイする

スコアリングサービスをAzure Container InstancesとAzure Kubernetes Serviceの代わりに[Azure App Service](https://docs.microsoft.com/ja-jp/azure/machine-learning/service/how-to-deploy-app-service)としてデプロイする場合は、以下の追加手順に従ってください。

変数タブで、変数グループ(`devopsforai-aml-vg`)を編集し、変数を追加します。

| 変数名                    | 推奨値                    |
|------------------------|------------------------|
| WEBAPP_DEPLOYMENT_NAME | _name of your web app_ |

**WEBAPP_DEPLOYMENT_NAME** をAzure Web Appの名前に設定します。このアプリにモデルをデプロイする前に、このアプリが存在している必要があります。

変数 **ACI_DEPLOYMENT_NAME**  を削除します。

パイプラインでは、[Azure ML CLI](./.pipelines/diabetes_regression-package-model-template.yml)を使用してスコアリングイメージを作成します。イメージは、Azure Machine Learning Serviceに属するAzure Container Registryインスタンスの下に登録されます。スコアリングファイルが依存する依存関係は、イメージのコンフィグ設定でコンテナと一緒にパッケージ化することもできます。Azure ML SDKを使用したコンテナの作成方法については、[Image class](https://docs.microsoft.com/ja-jp/python/api/azureml-core/azureml.core.image.image.image?view=azure-ml-py#create-workspace--name--models--image-config-)を参照してください。API ドキュメントを参照してください。

Web アプリが Infrastructure as Code パイプラインによって作成された Azure Container Registry からイメージを引き出すための資格情報を持っていることを確認してください。手順は、[Configure registry credentials in web app](https://docs.microsoft.com/ja-jp/azure/devops/pipelines/targets/webapp-on-container-linux?view=azure-devops&tabs=dotnet-core%2Cyaml#configure-registry-credentials-in-web-app) ページに記載されています。レジストリにイメージが存在するように、パイプラインを一度実行する必要があります (Deploy to Webapp ステージから `Create scoring image` ステップまでを含む)。その後、AzureポータルのAzure Container RegistryにWebアプリを接続することができます。

![build](./images/multi-stage-webapp.png)

### Rを使用したパイプラインの例

ビルドパイプラインは、モデルを訓練するためにRを使ってAzure MLパイプラインをビルドして公開することもサポートしています。これを有効にするには、`build-train-script`パイプライン変数を以下のいずれかの値に変更します。

- Diabetes_regression_build_train_pipeline_with_r.py` を変更することで、Azure ML Compute上でRを使ってモデルを学習することができます。また、環境定義YAML `diabetes_regression/conda_dependencies.yml` の中の `r-essentials` Conda パッケージをアンコメント（コードに含める）必要があります。
- `diabetes_regression_build_train_pipeline_with_r_on_dbricks.py` を使うと、Rを使ってDatabricks上でモデルを学習させることができます。手動でDatabricksクラスタを作成し、計算リソースとしてAzure ML Workspaceにアタッチする必要があります。変数グループにDB_CLUSTER_IDとDATABRICKS_COMPUTE_NAMEを設定します。

Rを使用したMLパイプラインの例では、モデルを訓練するための単一のステップがあります。モデルを評価して登録する方法は示されていません．評価と登録の方法はPythonの実装でのみ示されています．

### 観測とモニタリング

以下のようにソリューションのモデルの観測の側面を探ることができます。

- **ログ**。Azure MLポータルにリンクされたApplication Insightsインスタンスに移動し、Logs (Analytics) ペインに移動します。次のサンプルクエリは、HTTPリクエストを `score.py` で生成されたカスタムログと相関させます。これは、例えば、クエリの持続時間とスコアリングのバッチサイズを分析するために使用することができます。

  ```sql
  let Traceinfo=traces
  | extend d=parse_json(tostring(customDimensions.Content))
  | project workspace=customDimensions.["Workspace Name"],
      service=customDimensions.["Service Name"],
      NumberOfPredictions=tostring(d.NumberOfPredictions),
      id=tostring(d.RequestId),
      TraceParent=tostring(d.TraceParent);
  requests
  | project timestamp, id, success, resultCode, duration
  | join kind=fullouter Traceinfo on id
  | project-away id1
  ```

- **分散トレース**: スモークテストクライアントのコードはHTTP `traceparent` ヘッダを設定し（[W3C Trace Context proposed specification](https://www.w3.org/TR/trace-context-1)）、`score.py` コードはそのヘッダをログに記録します。上のクエリは、この値をどのようにして表面化するかを示しています。これをトレースフレームワークに適応させることができます。
- **モニタリング** :Azure ML のスコアリングコンテナのパフォーマンスを監視するために、[Azure Monitor for containers](https://docs.microsoft.com/ja-jp/azure/azure-monitor/insights/container-insights-overview)を利用することができます。

### リソースをクリーンアップする

このプロジェクトに作成されたリソースを削除するには、[/environment_setup/iac-remove-environment-pipeline.yml](./environment_setup/iac-remove-environment-pipeline.yml)の定義を使用するか、[Azure Portal](https://portal.azure.com)でリソースグループを削除するだけです。

## 次のステップ: 自身のプロジェクトとの統合

- [カスタムモデル](custom_model.md)ガイドには、このリポジトリテンプレートに自分のコードを適用するための情報がが含まれています。
- Azure MLパイプラインの実行を高速化するために、[Azure Pipelines selfhosted agents](https://docs.microsoft.com/ja-jp/azure/devops/pipelines/agents/agents?view=azure-devops&tabs=browser#install)の使用を検討してみてください。Azure MLパイプライン用のDockerコンテナイメージはサイズが大きく、実行の間にエージェント上にキャッシュされているので、実行から数分を短縮することができます。

### 追加の変数と設定

#### より多くの変数オプション

プロジェクトで使用される変数はさらにあります。1つはローカルで実行するためのもので、もう1つはAzure DevOps Pipelinesを使用するためのものです。

Azure Pipelinesを使用する場合、他のすべての変数はファイル `.pipelines/diabetes_regression-variables-template.yml` に保存されます。デフォルト値を出発点として使用し、必要に応じて変数を調整してください。

このフォルダには、トレーニング、評価、スコアリングスクリプトのパラメータを提供するために使用することを推奨する `parameters.json` ファイルもあります。diabetes_regression`が使用しているサンプルパラメータは、リッジ回帰[_α_ハイパーパラメータ](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html)です。この設定ファイルにはシリアライザは提供していません。

#### ローカルでの構成

ローカル開発環境の設定方法については、[開発環境設定手順]（development_setup.md）を参照してください。
