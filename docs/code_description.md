## リポジトリの詳細

### ディレクトリ構造

このリポジトリのディレクトリ構造:

```bash
├── .pipelines            <- CI、PR、モデルのトレーニングとデプロイのためのAzure DevOps YAMLパイプライン
├── bootstrap             <- Pythonスクリプトにより、このリポジトリをカスタムプロジェクト名で初期化します
├── charts                <- Azure Kubernetes Service(AKS)上にリソースをデプロイするためのHelmチャートです
├── data                  <- モデルを学習・評価するためのデータの初期セット。データの保存には使用しません
├── diabetes_regression   <- MLプロジェクトのトップレベルのフォルダです。
│   ├── evaluate          <- 学習したMLモデルを評価するPythonスクリプト
│   ├── register          <- 学習したMLモデルをAzure Machine Learning Serviceに登録するPythonスクリプト
│   ├── scoring           <- 学習したMLモデルを展開するためのPython score.py
│   ├── training          <- MLモデルを学習するPythonスクリプト
│       ├── R             <- RベースのMLモデルを学習するためのRスクリプト
│   ├── util              <- このMLプロジェクトに特化した様々なユーティリティ操作のためのPythonスクリプト
├── docs                  <- プロジェクト全体のための豊富なマークダウン・ドキュメント
├── environment_setup     <- インフラストラクチャに関連するすべてのものが格納されているトップレベルのフォルダ
│   ├── arm-templates     <- プロジェクトに必要なインフラを構築するためのAzure Resource Manager(ARM)テンプレート
│   ├── tf-templates      <- このプロジェクトに必要なインフラストラクチャを構築するためのTerraformテンプレート
├── experimentation       <- MLの実験コードが入ったJupyterノートブック
├── ml_service            <- すべてのAzure Machine Learningリソースのトップレベルフォルダ
│   ├── pipelines         <- Azure Machine Learningパイプラインを構築するPythonスクリプト
│   ├── util              <- Azure Machine Learningに特化した様々なユーティリティ操作のためのPythonスクリプト
├── .env.example          <- ローカルでの開発経験のための環境の例.envファイル  
├── .gitignore            <- gitignore ファイルは、意図的にトラックされていないファイルを Git が無視するように指定します  
├── LICENSE               <- このプロジェクトのライセンス文書
├── README.md             <- このプロジェクトを使う開発者のためのトップレベルのREADME  
```

リポジトリは，複数のMLプロジェクトを管理するのに適したフォルダ構造のテンプレートを提供します．***.pipelines*** , ***environment_setup***, ***ml_service***などの共通のフォルダと，各MLプロジェクトのコードベースを格納したフォルダがあります．このリポジトリには，***diabetes_regression***フォルダにあるMLプロジェクトのサンプルが含まれています．このフォルダは，[bootstrap procedure](./bootstrap/README.md)を実行すると，自動的にプロジェクト名に変更されます．

### 環境設定

- `environment_setup/install_requirements.sh` : 環境定義で指定されたパッケージとAzure ML SDKをインストールするためのローカル環境を準備します。

- `環境設定/iac-*-arm.yml, arm-templates` : Infrastructure as Code は、ARM を使用して必要なリソースを作成するためのプログラムと、それに対応する arm-templates を提供します。Infrastructure as Codeは、このテンプレートまたはTerraformテンプレートを使用してデプロイすることができます。

- `environment_setup/iac-*-tf.yml, tf-templates` : Terraform を使用して必要なリソースを作成するための Infrastructure as Code パイプラインで、対応する tf-templates と一緒に作成します。Infrastructure as Code は、このテンプレートまたは ARM テンプレートを使ってデプロイすることができます。

- `environment_setup/iac-remove-environment.yml` : 作成した必須リソースを削除するための Infrastructure as Code パイプラインです。

- `environment_setup/Dockerfile` : Python 3.6と必要なパッケージを含むビルドエージェントのDockerfileです。

- `environment_setup/docker-image-pipeline.yml` : [microsoft/mlopspython](https://hub.docker.com/_/microsoft-mlops-python) のイメージをビルドしてプッシュするための AzDo パイプラインです。

### パイプライン

- `.pipelines/abtest.yml` : [カナリアリリースのデプロイ戦略]を示すパイプライン(./docs/canary_ab_deployment.md)。
- `.pipelines/code-quality-template.yml` : CIパイプラインとPRパイプラインで使用されるパイプラインテンプレートです。リンティング、データ、ユニットテストを行うステップが含まれています。
- `.pipelines/diabetes_regression-ci-image.yml` : 糖尿病回帰予測モデルのスコアリングイメージを構築するパイプライン。
- `.pipelines/diabetes_regression-ci.yml` : コードが**master**にマージされたときにトリガーされるパイプラインです。リンティング、データ整合性テスト、ユニットテスト、MLパイプラインの構築と公開を行います。
- `.pipelines/diabetes_regression-cd.yml` : コードが**master**にマージされ、`.pipelines/diabetes_regression-ci.yml`が完了したときにトリガされるパイプラインです。リンティング、データの完全性テスト、ユニットテスト、MLパイプラインの構築と公開を行います。
- `.pipelines/diabetes_regression-package-model-template.yml` : コードが**master**にマージされたときにトリガーされるパイプラインです。登録されたモデルをターゲットにデプロイします。
- `.pipelines/diabetes_regression-get-model-id-artifact-template.yml` : `.pipelines/diabetes_regression-cd.yml` パイプラインで使用されるパイプラインテンプレートです。前のパイプラインで公開されたモデルメタデータを取得し、モデルIDを取得します。
- `.pipelines/diabetes_regression-publish-model-artifact-template.yml` : `.pipelines/diabetes_regression-ci.yml` パイプラインで利用されるパイプラインテンプレート。新しいモデルが登録されたかどうかを調べ、モデルのメタデータを含むパイプラインの成果物を公開します。
- `.pipelines/helm-*.yml` : `.pipelines/abtest.yml` パイプラインで利用されるパイプラインテンプレート。
- `.pipelines/pr.yml` : **master** ブランチへの **プル リクエスト** が作成されたときにトリガーされるパイプライン。リンティング、データの完全性テスト、ユニットテストのみを行います。

### MLサービス

- `ml_service/pipelines/diabetes_regression_build_train_pipeline.py` : MLトレーニングパイプラインをビルドして公開します．ML Compute上でPythonを使用します。
- `ml_service/pipelines/diabetes_regression_build_train_pipeline_with_r.py` : MLのトレーニングパイプラインをビルドして公開します．ML Compute上でRを使用します。
- `ml_service/pipelines/diabetes_regression_build_train_pipeline_with_r_on_dbricks.py` : ML学習パイプラインを構築して公開します．R on Databricks Computeを利用しています．
- `ml_service/pipelines/run_train_pipeline.py` : 公開されているMLトレーニングパイプライン(Python on ML Compute)をREST API経由で呼び出します。
- `ml_service/util` : MLトレーニングパイプラインを構築し公開するための共通のユーティリティ関数が含まれています．

### 環境定義

- `diabetes_regression/conda_dependencies.yml` : トレーニングとスコアリングに使用する環境のConda環境定義 (train.pyとscore.pyが実行されているDockerイメージ)。
- `diabetes_regression/ci_dependencies.yml` : CI環境のためのConda環境定義。

### トレーニングステップ

- `diabetes_regression/training/train_aml.py` : MLトレーニングパイプラインのトレーニングステップです。
- `diabetes_regression/training/train.py` : train_aml.pyによって呼び出されるMLの機能です．
- `diabetes_regression/training/R/r_train.r` : サンプルデータ(weight_data.csv)をもとにRを用いてモデルを学習します．
- `diabetes_regression/training/R/train_with_r.py` : ML Compute上でのR学習スクリプトを呼び出す python ラッパー (ML Pipeline Step) です．
- `Diabetes_regression/training/R/train_with_r_on_databricks.py` : Databricks Compute上のR学習スクリプトを起動する python ラッパー (ML Pipeline Step) です。
- `diabetes_regression/training/R/weight_data.csv` : モデルを学習するためのRスクリプト(r_train.r)が使用するサンプルデータセット
- `diabetes_regression/training/R/test_train.py` : 訓練スクリプトのユニットテスト

### 評価ステップ

- `diabetes_regression/evaluate/evaluate_model.py` : ML学習パイプラインの評価ステップで，評価の結果，新しいモデルの方が前のモデルよりも性能が高いことが示された場合に，新しいモデルを登録します．

### 登録ステップ

- `diabetes_regression/evaluate/register_model.py` : 新しいモデルが前のモデルよりも性能が高いことが評価で示された場合に、新しい学習済みモデルを登録します。

### スコアリング

- `diabetes_regression/scoring/score.py` : QA/Prod環境にデプロイされている間に、モデルと一緒にDockerイメージパッケージ化されるスコアリングスクリプトです。
- `diabetes_regression/scoring/inference_config.yml`, `deployment_config_aci.yml`, `deployment_config_aks.yml` : ACI と AKS のデプロイ対象の [AML Model Deploy](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.private-vss-services-azureml&ssr=false#overview) パイプラインタスクのための設定ファイルです。
- `diabetes_regression/scoring/scoreA.py`, `diabetes_regression/scoring/scoreB.py` : [カナリアリリースサンプル] (./docs/canary_ab_deployment.md) 用の単純なスコアリングファイルです。