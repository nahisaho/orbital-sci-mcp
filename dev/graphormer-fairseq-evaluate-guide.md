# Graphormer fairseq evaluateモード利用ガイド

## 1. 目的

orbital-sci-mcpにおけるGraphormer対応は、任意のSMILESを直接Python APIへ流し込む方式ではなく、upstreamが公開しているfairseqベースのevaluateワークフローをMCP経由で起動する方式を採用している。

この文書は、graphormer_predict_propertyをfairseq evaluateモードで実行するための引数テンプレートと運用前提をまとめる。

対象実装:

- src/orbital_sci_mcp/adapters/graphormer.py

## 2. 背景

Graphormerの公開ドキュメントでは、主な利用経路は以下の2つだった。

- fairseq-trainを使った学習
- graphormer/evaluate/evaluate.pyを使った事前学習済みモデルの評価

一方で、単一のSMILES文字列を与えてすぐに予測値を返す安定した公開Python APIは、2026-04-01時点で確認できなかった。そのためMCP側では、Graphormerリポジトリのローカルcheckoutを前提にevaluate.pyをsubprocessで呼び出す構成としている。

## 3. 前提条件

- Graphormerのローカルcheckoutが存在すること
- Graphormer実行環境にfairseqが入っていること
- 対象データセットの前処理と配置がupstreamの想定どおり完了していること
- 使用するpretrained model名がupstreamのevaluate.pyで受け付けられること

## 4. 必須 inference_options

graphormer_predict_propertyを使う場合、argumentsの中にinference_optionsを入れる。

必須項目:

- graphormer_repo_path
- dataset_name
- dataset_source
- pretrained_model_name

推奨項目:

- task
- arch
- num_classes
- batch_size
- split
- seed
- num_workers
- criterion
- metric
- save_dir
- load_pretrained_model_output_layer

## 5. MCP 引数テンプレート

```json
{
  "tool_name": "graphormer_predict_property",
  "arguments": {
    "smiles": "CCO",
    "target_property": "pcqm4m",
    "inference_options": {
      "graphormer_repo_path": "/absolute/path/to/Graphormer",
      "dataset_name": "pcqm4m",
      "dataset_source": "ogb",
      "pretrained_model_name": "pcqm4mv1_graphormer_base",
      "task": "graph_prediction",
      "arch": "graphormer_base",
      "num_classes": 1,
      "batch_size": 64,
      "split": "valid",
      "seed": 1,
      "num_workers": 16,
      "criterion": "l1_loss",
      "load_pretrained_model_output_layer": true
    }
  }
}
```

注記:

- 現在のadapterはsmilesを直接evaluate.pyに渡していない
- smilesは将来の単分子推論API用に保持しているが、fairseq evaluateモードではdataset側の入力を使う
- したがって、このモードは「単一分子予測」ではなく「upstreamの評価ジョブ起動」に近い

## 6. 実際に生成されるコマンド

上記テンプレートは概ね次のコマンドに変換される。

```bash
python /path/to/Graphormer/graphormer/evaluate/evaluate.py \
  --user-dir /path/to/Graphormer/graphormer \
  --dataset-name pcqm4m \
  --dataset-source ogb \
  --task graph_prediction \
  --arch graphormer_base \
  --num-classes 1 \
  --batch-size 64 \
  --pretrained-model-name pcqm4mv1_graphormer_base \
  --split valid \
  --seed 1 \
  --criterion l1_loss \
  --num-workers 16 \
  --load-pretrained-model-output-layer
```

## 7. 想定ユースケース

### 7.1 事前学習済みモデルの評価

- 既存データセット上でpretrained Graphormerの精度を確認する
- MCP経由で評価コマンドを一元化する

### 7.2 再現性のあるジョブ起動

- エージェントからinference_optionsを固定し、同じ評価条件を再利用する
- CLIコマンド組み立てミスを減らす

## 8. 現在の制約

- 単一のSMILESをその場で推論するAPIではない
- evaluate.pyの前提にしたがってdatasetが用意されている必要がある
- Graphormer環境構築はorbital-sci-mcp側では自動化していない
- stdoutとstderrはそのままMCPレスポンスへ返すため、出力量が大きい場合がある

## 9. エラー時の見方

返却される主なerror code:

- DEPENDENCY_MISSING
  - availability checkの段階でfairseqなどの依存が不足している
- INPUT_VALIDATION_FAILED
  - graphormer_repo_pathが存在しない
  - dataset_name、dataset_source、pretrained_model_nameなど必須inference_optionsが不足している
- UNSUPPORTED_OPERATION
  - inference_options自体が与えられていない
  - ローカルcheckout内にgraphormer/evaluate/evaluate.pyが存在しない
- EXECUTION_FAILED
  - evaluate.pyは起動したがコマンド実行に失敗した

INPUT_VALIDATION_FAILEDで必須項目が不足した場合、detailsにはmissing_inference_optionsが入る。

EXECUTION_FAILEDの場合はdetailsに以下が含まれる。

- returncode
- stdout
- stderr
- command

## 10. 既知の今後課題

- Graphormer upstreamで安定したPython推論APIが見つかればadapterをそちらへ切り替える
- 単一SMILESの即時推論モードを別ツールとして分離する可能性がある

## 11. 推奨運用

- Graphormerはevaluateジョブ実行用ツールとして扱う
- 対話的な単分子予測用途は当面Graphormer以外の軽量推論バックエンドを優先する
- MCP側ではinference_optionsのテンプレートを保存して再利用する

## 12. Integration testの実行方法

opt-inのintegration testは以下のファイルにある。

- tests/test_graphormer_integration.py

このテストは次の条件を満たした場合だけ実行される。

- GRAPHORMER_RUN_INTEGRATION=1
- GRAPHORMER_REPO_PATHが設定済み
- GRAPHORMER_DATASET_NAMEが設定済み
- GRAPHORMER_DATASET_SOURCEが設定済み
- GRAPHORMER_PRETRAINED_MODEL_NAMEが設定済み
- 実行中のPython環境にfairseqが入っている

最初の雛形として、ルートにあるサンプル環境設定ファイルをコピーして必要値を埋める。

```bash
cp .env.example .env
```

envを反映してintegration testだけを実行する例:

```bash
set -a
source .env
set +a
PYTHONPATH=src pytest -q tests/test_graphormer_integration.py -m integration
```

通常の単体テストだけを流したい場合は、これまでどおり次でよい。

```bash
pytest -q
```

注記:

- .env.exampleのGRAPHORMER_RUN_INTEGRATIONは既定で0にしている
- save_dirを指定しない場合、Graphormer側の既定動作に委ねる
- integration testはevaluate.pyの成功終了まで確認するため、データセット準備不足やmodel名不一致はEXECUTION_FAILEDとして返る
- integration testの前段では、必須環境変数が未設定ならskipされる

## 13. 追加で確認すべき点

- Graphormer checkout側でgraphormer/evaluate/evaluate.pyが利用可能であること
- pretrained model名が使用中のupstream revisionと一致していること
- dataset_sourceとdataset_nameの組み合わせがupstream実装の前提に一致していること