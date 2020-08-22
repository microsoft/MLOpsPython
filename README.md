---
page_type: sample
languages:
- python
products:
- azure
- azure-machine-learning-service
- azure-devops
description: "Code which demonstrates how to set up and operationalize an MLOps flow leveraging Azure Machine Learning and Azure DevOps."
---

# MLOps with Azure ML

CI: [![Build Status](https://aidemos.visualstudio.com/MLOps/_apis/build/status/Model-Train-Register-CI?branchName=master)](https://aidemos.visualstudio.com/MLOps/_build/latest?definitionId=160&branchName=master)

CD: [![Build Status](https://aidemos.visualstudio.com/MLOps/_apis/build/status/microsoft.MLOpsPython-CD?branchName=master)](https://aidemos.visualstudio.com/MLOps/_build/latest?definitionId=161&branchName=master)

MLOpsでは、ML/AIプロジェクトのContinuous IntegrationとContinuous Deliveryパイプラインの構築方法を理解します。モデル再トレーニングパイプライン、モデル管理、運用化のためのAzure MLサービスとともに、ビルドおよびリリース/デプロイメントパイプラインにAzure DevOps Projectを使用します。

![ML lifecycle](/docs/images/ml-lifecycle.png)

このテンプレートには、エンドツーエンドのML/AIワークフローを自動化する方法を示す機械学習プロジェクトのコードとパイプライン定義が含まれています。

2020年8月

## Architecture and Features

アーキテクチャの参照: [Azure Machine Learning を使用した Python モデル用の機械学習運用化 (MLOps)](https://docs.microsoft.com/ja-jp/azure/architecture/reference-architectures/ai/mlops-python) 
 
このリファレンスアーキテクチャでは、Azure DevOpsと[Azure Machine Learning](https://docs.microsoft.com/ja-jp/azure/machine-learning/overview-what-is-azure-ml)を使用してAIアプリケーションに継続的インテグレーション(CI)、継続的デリバリー(CD)、再トレーニングパイプラインを実装する方法を紹介しています。このソリューションは scikit-learn 糖尿病データセット上に構築されていますが、あらゆるAIシナリオやJenkinsやTravisのような他の一般的なビルドシステムに簡単に適応させることができます。

ビルドパイプラインには、データのサニティテスト、ユニットテスト、異なるコンピューティングターゲット上でのモデルトレーニング、モデルバージョン管理、モデル評価/モデル選択、リアルタイムWebサービスとしてのモデル展開、QA/prodへの段階的展開、統合テストのためのDevOpsタスクが含まれています。

## 要件

- 有効なAzure サブスクリプション
- サブスクリプションに対する共同作成者を含む権限

## はじめに

このソリューションをサブスクリプションにデプロイするには、[getting started](docs/getting_started.md) ドキュメントのマニュアルの指示に従ってください。次に、このリポジトリ テンプレートを使用して [独自のコードを統合する] (docs/custom_model.md) のガイドに従ってください。

### リポジトリの詳細

コードやスクリプトの詳細はリポジトリ[こちら](/docs/code_description.md)にあります。

### 参考リンク

- [Azure ML とは](https://docs.microsoft.com/ja-jp/azure/machine-learning/overview-what-is-azure-ml)
- [Azure ML CLI](https://docs.microsoft.com/ja-jp/azure/machine-learning/service/reference-azure-machine-learning-cli)
- [Azure ML Samples](https://docs.microsoft.com/ja-jp/azure/machine-learning/service/samples-notebooks)
- [Azure ML Python SDK クイックスタート](https://docs.microsoft.com/ja-jp/azure/machine-learning/service/quickstart-create-workspace-with-python)
- [Azure DevOps](https://docs.microsoft.com/ja-jp/azure/devops/?view=vsts)

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit <https://cla.microsoft.com.>

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## 補足

### 日本語版について

このリポジトリは、2020年8月時点の[MLOps with Azure ML](https://github.com/microsoft/MLOpsPython)の日本語訳です。

### お困りですか?

- おかしいな? と思ったら、英語版オリジナルをご確認いただき、オリジナルでも発生するのか日本語訳だけの問題かを切り分けてください。
- 英語オリジナルについては、下記手順で英語リポジトリに対して改善要求をお送りください。
  - まず、ラボに記載されているすべての指示 (「ハンズオン ラボの前に」のドキュメントを含む) に従っていることを確認します。
  - 次に、問題を、その詳細な説明とともに送信します。
  - pull 要求を送信しないでください。コンテンツ作成者がすべての変更を行い、pull 要求を送信して承認を求めます。

ワークショップ開催を計画している場合、早めに資料をレビューおよびテストしてください。 少なくとも 2 週間前には実施することをお勧めします。