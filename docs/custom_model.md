# MLOpsPythonのリポジトリテンプレートを使って自分のコードを持ちこむ

このドキュメントでは、このリポジトリをテンプレートとして使用して、独自のスクリプトやデータを使用してAzure MLでリアルタイム推論を用いてモデルを訓練し、デプロイする際の手順を説明しています。

1. MLOpsPython [開始](get_started.md)ガイドに従ってください。
1. プロジェクトのブートストラップ
1. トレーニングデータの設定
1. (必要に応じて）MLの実験コードを本番環境で使用可能なコードに変換します。
1. トレーニングコードの置き換えます。
1. (オプション)評価用コードを更新します。
1. ビルドエージェント環境のカスタマイズします。
1. (該当する場合)スコアコードを差し替えてください。

## スタートアップガイドを実施する

MLOpsPythonを実行するためのインフラとパイプラインを設定するには、[スタートアップ](getting_started.md)ガイドに従ってください。

このリポジトリの構造については、[レポジトリの詳細](code_description.md)を参照してください。

## プロジェクトのブートストラップ

ブートストラップは、プロジェクト名に使用されるディレクトリ構造を準備します。

* ベースのプロジェクト名 `diabetes_regression` から指定のプロジェクト名にファイルとフォルダの名前を変更する。
* プロジェクト名に基づいたインポートと絶対パスの修正
* いくつかのディレクトリの削除とクリーンアップ

**注:**ブートストラップスクリプトは `diabetes_regression` フォルダの名前を任意のプロジェクト名に変更するので、パスが関係している場合は `[project name]` と呼びます。

既存のMLOpsPythonリポジトリからブートストラップを実行するには、以下のようにします。

1. Python 3がローカルにインストールされていることを確認します。
1. コードのローカルコピーから、`bootstrap` フォルダ内の `bootstrap.py` スクリプトを実行します。
`python bootstrap.py -d [dirpath] -n [project name]`。
    * `[dirpath]` は、MLOpsPythonがクローンされるディレクトリのルートへの絶対パスです。
    * `[project name]` はあなたのMLプロジェクトの名前です。

## トレーニングデータの設定

トレーニングMLパイプラインでは、トレーニングデータとして[sample diabetes dataset](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_diabetes.html)を使用しています。

**重要** 以下の手順でモデルトレーニングに独自のAzure ML Datasetを使用するためにテンプレートを変換します。

1. Azure ML Workspaceで[データセットを作成](https://docs.microsoft.com/azure/machine-learning/how-to-create-register-datasets)します。
1. .pipelines/[project name]-variables-template.yml` の変数 `DATASET_NAME` と `DATASTORE_NAME` を更新します。

## MLの実験的なコードを本番を想定したコードに変換する

MLOpsPythonテンプレートは、[Azure MLパイプラインステップ](https://docs.microsoft.com/python/api/azureml-pipeline-steps/azureml.pipeline.steps)のセットを呼び出すAzure Machine Learning(ML)パイプラインを作成します (`ml_service/pipelines/[project name]_build_train_pipeline.py`を参照してください)。もしあなたの実験が現在Jupyterノートブックの中にあるならば、それを独立して実行できるスクリプトにリファクタリングして、既存のAzure MLパイプラインステップが利用するテンプレートにドロップする必要があります。

1. 実験コードをスクリプトにリファクタリングする
1. 【推奨】ユニットテストの準備

これらのスクリプトの例はすべてこのリポジトリにあります．
ステップ・バイ・ステップのガイドや詳細は [Convert ML experimental code to production code tutorial](https://docs.microsoft.com/azure/machine-learning/tutorial-convert-ml-experiment-to-production) を参照してください。

## トレーニングコードの置き換え

テンプレートには、`[project name]/training`フォルダにある3つのスクリプトが含まれています。これらのスクリプトを実験コードに合わせて更新してください。

* `train.py`は基本的なデータの準備とモデルの学習に必要なプラットフォームに依存しないロジックが含まれています。このスクリプトは、ローカル開発のために静的なデータファイルに対して起動することができます。
* `train_aml.py` は，MLのパイプラインステップのエントリースクリプトです．train.pyの関数をAzure MLのコンテキストで呼び出し、ログを追加します。`train_aml.py` は `[project name]/parameters.json` から学習用のパラメータを読み込み、`train.py` の学習関数に渡します。実験コードを `train.py` の関数のシグネチャに合わせてリファクタリングできるのであれば、このファイルはそれほど変更する必要はないでしょう。
* `test_train.py` には、`train.py` の関数の回帰を防ぐためのテストが含まれています。自分のコードのテストがない場合は、このファイルを削除してください。

トレーニングで必要な依存関係を `[プロジェクト名]/conda_dependencies.yml]` に追加します。このファイルは、パイプラインのステップが実行される環境を生成するために使用されます。

## 評価用のコードを更新する

MLOpsPythonのテンプレートでは、evaluate_modelスクリプトを使用して、新しく学習したモデルと現在の本番モデルの性能をMean Squared Errorに基づいて比較します。新しく訓練されたモデルの性能が現在の本番モデルよりも良い場合、パイプラインは続行され、そうでなければ，パイプラインはキャンセルされます。

評価ステップを維持するには、`[project name]/evaluate/evaluate_model.py` の `mse` のインスタンスをすべて必要なメトリックに置き換えてください。

評価ステップを無効にするには、以下のいずれかを実行します。

* DevOpsパイプライン変数 `RUN_EVALUATION` を `false` に設定します。
* `.pipelines/[project name]-variables-template.yml` の `RUN_EVALUATION` のコメントを外し、値を `false` に設定する。

## ビルドエージェント環境のカスタマイズ

MLOpsPythonテンプレートのDevOpsパイプライン定義は、スターツアップガイドの作業に必要な依存関係が含まれたDockerコンテナ内でいくつかのステップを実行します。
ユニットテストの実行やAzure MLパイプラインの生成に追加の依存関係が必要な場合、いくつかのオプションがあります。:

* ユニットテストで必要な依存関係を `.pipelines/code-quality-template.yml` にインストールするパイプラインステップを追加します。テストの依存関係の数が少ない場合にお勧めします。
* 依存関係を含む新しいDockerイメージを作成します。docs/custom_container.md](custom_container.md)を参照してください。依存関係の数が多い場合や、実行ごとに追加の依存関係をインストールするオーバーヘッドが大きすぎる場合にお勧めします。
* パイプライン定義ファイルからコンテナ参照を削除し、依存関係がプリインストールされているセルフホストエージェント上でパイプラインを実行します。

## スコアコードの置き換え

モデルがリアルタイムスコアリング機能を提供するためには、スコアコードを置き換える必要があります。MLOpsPythonテンプレートはスコアコードを使用してモデルをデプロイし、ACI、AKS、またはWebアプリ上でリアルタイムスコアリングを行います。

スコアリングを継続したい場合:

1. プロジェクト名]/scoring/score.py`を更新または置換してください。
1. スコアリングで必要な依存関係を `[プロジェクト名]/conda_dependencies.yml` に追加します。
1. ml_service/util/smoke_test_scoring_service.py` スクリプトのテストケースを、データ内の学習特徴量のスキーマと一致するように変更します。
