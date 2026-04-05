# GraphormerとDiG共通運用ガイド

## 1. 目的

orbital-sci-mcpでGraphormer系workflowを運用する際の共通前提、toolの使い分け、integration testの実行条件を1つにまとめる。

この文書は次の個別ガイドの入口としても使う。

- dev/graphormer-fairseq-evaluate-guide.md
- dev/dig-protein-ligand-guide.md

## 2. 対象tool

- graphormer_predict_property
- dig_sample_conformations
- dig_predict_equilibrium

## 3. 現在の対応workflow一覧

### 3.1 Graphormer

- tool名: graphormer_predict_property
- workflow: fairseq_evaluate
- upstream実体: graphormer/evaluate/evaluate.py
- 主用途: 既存データセット上での分子特性評価

### 3.2 DiG sampling系

- tool名: dig_sample_conformations
- workflow: protein_ligand_single_datapoint
- upstream実体: distributional_graphormer/protein-ligand/evaluation/single_datapoint_sampling.sh
- 主用途: protein-ligand系の複数コンフォメーション生成

- tool名: dig_sample_conformations
- workflow: protein_system_sampling
- upstream実体: distributional_graphormer/protein/run_inference.py
- 主用途: protein系のサンプリング

- tool名: dig_sample_conformations
- workflow: property_guided_sampling
- upstream実体: distributional_graphormer/property-guided/scripts/sample.sh
- 主用途: 原子数と目標バンドギャップを条件にした構造生成

### 3.3 DiG equilibrium系

- tool名: dig_predict_equilibrium
- workflow: catalyst_adsorption_density
- upstream実体: distributional_graphormer/catalyst-adsorption/scripts/density.sh
- 主用途: catalyst-adsorption系のdensity map計算

## 4. 使い分けの指針

- Graphormerを使う場面:
  - 既存データセット上でproperty predictionや評価ジョブを起動したいとき
  - fairseqベースのevaluate workflowをそのまま再利用したいとき
- DiG sampling系を使う場面:
  - 複数構造のサンプリングや条件付き生成を行いたいとき
  - upstreamのtask別workflowに沿って生成系ジョブを起動したいとき
- DiG equilibrium系を使う場面:
  - density mapや平衡分布寄りの計算を行いたいとき
  - catalyst-adsorption workflowを高さごとに反復実行したいとき

## 5. 共通前提条件

- Graphormerのローカルcheckoutがあること
- 対象workflowのscriptまたはPython entrypointがcheckout内に存在すること
- 各workflowに必要なdatasetとcheckpointがupstream READMEどおりに配置済みであること
- integration testを回す場合は、実際の実行環境と同じPython環境からpytestを起動すること

## 6. 必須inference_options早見表

### 6.1 graphormer_predict_property

- graphormer_repo_path
- dataset_name
- dataset_source
- pretrained_model_name

### 6.2 dig_sample_conformations

- 共通
  - graphormer_repo_path
  - dig_workflow
- protein_ligand_single_datapoint
  - pdbid
- protein_system_sampling
  - pdbid
- property_guided_sampling
  - num_gpus
  - batch_size_per_gpu
  - num_atoms
  - target_bandgap

### 6.3 dig_predict_equilibrium

- graphormer_repo_path
- dig_workflow=catalyst_adsorption_density
- num_gpus
- batch_size_per_gpu

## 7. integration test一覧

### 7.1 Graphormer

- testファイル: tests/test_graphormer_integration.py
- 有効化条件:
  - GRAPHORMER_RUN_INTEGRATION=1
  - GRAPHORMER_REPO_PATH
  - GRAPHORMER_DATASET_NAME
  - GRAPHORMER_DATASET_SOURCE
  - GRAPHORMER_PRETRAINED_MODEL_NAME
  - fairseqが入ったPython環境

### 7.2 DiG protein-ligand

- testファイル: tests/test_dig_integration.py
- 有効化条件:
  - DIG_RUN_INTEGRATION=1
  - DIG_REPO_PATH
  - DIG_WORKFLOW=protein_ligand_single_datapoint
  - DIG_PDBID

### 7.3 DiG protein

- testファイル: tests/test_dig_integration.py
- 有効化条件:
  - DIG_PROTEIN_RUN_INTEGRATION=1
  - DIG_PROTEIN_REPO_PATH
  - DIG_PROTEIN_PDBID

### 7.4 DiG property-guided

- testファイル: tests/test_dig_integration.py
- 有効化条件:
  - DIG_PROPERTY_RUN_INTEGRATION=1
  - DIG_PROPERTY_REPO_PATH
  - DIG_PROPERTY_NUM_GPUS
  - DIG_PROPERTY_BATCH_SIZE_PER_GPU
  - DIG_PROPERTY_NUM_ATOMS
  - DIG_PROPERTY_TARGET_BANDGAP

### 7.5 DiG equilibrium

- testファイル: tests/test_dig_integration.py
- 有効化条件:
  - DIG_EQUILIBRIUM_RUN_INTEGRATION=1
  - DIG_EQUILIBRIUM_REPO_PATH
  - DIG_EQUILIBRIUM_NUM_GPUS
  - DIG_EQUILIBRIUM_BATCH_SIZE_PER_GPU
- 検証内容:
  - runs件数とsummary件数の整合性
  - last_completed_height_indexの整合性

## 8. 実行コマンド

最初に環境変数ファイルを用意する。

```bash
cp .env.example .env
```

Graphormerだけを実行する例:

```bash
set -a
source .env
set +a
PYTHONPATH=src pytest -q tests/test_graphormer_integration.py -m integration
```

DiG系をまとめて実行する例:

```bash
set -a
source .env
set +a
PYTHONPATH=src pytest -q tests/test_dig_integration.py -m integration
```

通常のunit testだけを流す例:

```bash
pytest -q
```

## 9. 既知の制約

- Graphormerは単一SMILES即時推論APIではなく、evaluate workflow起動として実装している
- DiGはtask別workflow起動として実装しており、汎用の単一APIには寄せていない
- workflowごとに必要なdataset、checkpoint、GPU要件が異なる
- orbital-sci-mcp側ではupstream環境構築やモデル取得そのものは自動化していない

DiG equilibrium workflowでは、height_indicesが空配列ならINPUT_VALIDATION_FAILEDとなる。個別の高さインデックス実行が失敗した場合はEXECUTION_FAILEDとなり、error detailsにheight_indexが入る。

## 10. 参照順序

- 最初にこの共通ガイドを読む
- Graphormerの詳細を確認する場合はdev/graphormer-fairseq-evaluate-guide.mdを見る
- DiGの詳細を確認する場合はdev/dig-protein-ligand-guide.mdを見る