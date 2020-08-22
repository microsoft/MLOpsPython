## 開発環境の設定

### セットアップ

ローカル環境でもAzureサブスクリプションへのアクセスが必要なので、Azure MLワークスペース上で共同作成者としてアクセスする必要があることに注意してください。

プロジェクトをローカルで設定するためには、ルートディレクトリに `.env.example` のコピーを作成し、それに `.env` という名前を付けます。不足している値をすべて記入し、必要に応じて既存の値を調整してください。

### インストール

Azure CLIをインストールする](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)。Azure CLIを使用して対話的にログインします。

[venv](https://docs.python.org/3/library/venv.html)、[conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)、または[pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)を使用して仮想環境を作成します。

ここでは、Python 3で`venv`環境を設定して起動する例を示します。

```
python3 -mvenv .venv
source .venv/bin/activate
```

仮想環境に必要なPythonモジュールをインストールします。

```
pip install -r environment_setup/requirements.txt 
```

### ローカルコードの実行

ローカルのMLのパイプラインコードをAzure ML上で実行するには、以下のようなコマンドを実行してください（bashで、すべて一行で実行します）。

```
export BUILD_BUILDID=$(uuidgen); python ml_service/pipelines/build_train_pipeline.py && python ml_service/pipelines/run_train_pipeline.py
```

BUILD_BUILDIDは、MLパイプラインを一意に識別するための変数です。
`build_train_pipeline.py` と `run_train_pipeline.py` スクリプトを使用します。Azure DevOpsでは
を現在のビルド番号に設定されます。ローカル環境では、次のようなコマンドを使用することができます。
`uuidgen` なので、それぞれの実行で異なるランダムな識別子を設定し、不整合がないようにします。
