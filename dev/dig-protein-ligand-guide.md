# DiG sampling運用ガイド

## 1. 目的

orbital-sci-mcpにおけるDiG対応として、Graphormerリポジトリ内のdistributional_graphormer配下workflowをMCP経由で起動できるようにする。

対象ツール:

- src/orbital_sci_mcp/adapters/dig.py
- MCP tool名: dig_sample_conformations
- MCP tool名: dig_predict_equilibrium

## 2. 現在サポートするworkflow

対応するworkflowは、upstream READMEに具体的な実行手順がある次の4つである。

- protein_ligand_single_datapoint
- protein_system_sampling
- property_guided_sampling
- catalyst_adsorption_density

このworkflowは、distributional_graphormer/protein-ligand/evaluation/single_datapoint_sampling.shを起動して、特定のpdbidに対する複数コンフォメーション生成を行う。

protein_system_samplingは、distributional_graphormer/protein/run_inference.pyを起動して、pdbidに対応する特徴量ファイルとFASTAファイルからサンプリングを行う。

property_guided_samplingは、distributional_graphormer/property-guided/scripts/sample.shを起動して、原子数と目標バンドギャップを条件に構造生成を行う。

catalyst_adsorption_densityは、distributional_graphormer/catalyst-adsorption/scripts/density.shを指定した高さインデックス群に対して順次起動し、density map計算を実行する。

## 3. 前提条件

- Graphormerのローカルcheckoutが存在すること
- checkout内に対象workflowのscriptが存在すること
- protein-ligandまたはprotein用のdatasetとcheckpointがupstream READMEどおりに配置済みであること
- 現在のPython実行環境でworkflowが要求する依存が解決されていること

## 4. 必須inference_options

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
- catalyst_adsorption_density
  - num_gpus
  - batch_size_per_gpu

dig_workflowには現在protein_ligand_single_datapoint、protein_system_sampling、property_guided_sampling、catalyst_adsorption_densityを指定する。

## 5. 任意パラメーター

- conformer_count
- inference_options.sample_count
- inference_options.checkpoint_path
- inference_options.feature_path
- inference_options.fasta_path
- inference_options.output_prefix
- inference_options.use_gpu
- inference_options.use_tqdm
- inference_options.num_gpus
- inference_options.batch_size_per_gpu
- inference_options.save_dir
- inference_options.height_indices
- inference_options.num_atoms
- inference_options.target_bandgap

sample_countが指定されない場合は、conformer_countを利用する。どちらも未指定なら1件生成する。

## 6. MCP引数テンプレート

```json
{
  "tool_name": "dig_sample_conformations",
  "arguments": {
    "conformer_count": 50,
    "inference_options": {
      "graphormer_repo_path": "/absolute/path/to/Graphormer",
      "dig_workflow": "protein_ligand_single_datapoint",
      "pdbid": "1a2k"
    }
  }
}
```

注記:

- このworkflowはSMILESを直接使わない
- 入力対象はupstream datasetに含まれるpdbidである
- 利用可能なpdbidはdistributional_graphormer/protein-ligand/src/dataset/all_md.listを参照する

protein_system_samplingの例:

```json
{
  "tool_name": "dig_sample_conformations",
  "arguments": {
    "conformer_count": 3,
    "inference_options": {
      "graphormer_repo_path": "/absolute/path/to/Graphormer",
      "dig_workflow": "protein_system_sampling",
      "pdbid": "6lu7"
    }
  }
}
```

property_guided_samplingの例:

```json
{
  "tool_name": "dig_sample_conformations",
  "arguments": {
    "inference_options": {
      "graphormer_repo_path": "/absolute/path/to/Graphormer",
      "dig_workflow": "property_guided_sampling",
      "num_gpus": 1,
      "batch_size_per_gpu": 2,
      "save_dir": "/tmp/dig-property-guided",
      "num_atoms": 16,
      "target_bandgap": 1.5
    }
  }
}
```

catalyst_adsorption_densityの例:

```json
{
  "tool_name": "dig_predict_equilibrium",
  "arguments": {
    "inference_options": {
      "graphormer_repo_path": "/absolute/path/to/Graphormer",
      "dig_workflow": "catalyst_adsorption_density",
      "num_gpus": 1,
      "batch_size_per_gpu": 2,
      "save_dir": "/tmp/dig-density",
      "height_indices": [0, 1, 2]
    }
  }
}
```

## 7. 実際に生成されるコマンド

```bash
bash /path/to/Graphormer/distributional_graphormer/protein-ligand/evaluation/single_datapoint_sampling.sh \
  --pdbid 1a2k \
  --number 50
```

実行ディレクトリは次になる。

```bash
/path/to/Graphormer/distributional_graphormer/protein-ligand
```

protein_system_samplingでは概ね次のコマンドを生成する。

```bash
python /path/to/Graphormer/distributional_graphormer/protein/run_inference.py \
  -c /path/to/Graphormer/distributional_graphormer/protein/checkpoints/checkpoint-520k.pth \
  -i /path/to/Graphormer/distributional_graphormer/protein/dataset/6lu7.pkl \
  -s /path/to/Graphormer/distributional_graphormer/protein/dataset/6lu7.fasta \
  -o 6lu7 \
  --output-prefix /path/to/Graphormer/distributional_graphormer/protein/output \
  -n 3 \
  --use-gpu \
  --use-tqdm
```

property_guided_samplingでは概ね次のコマンドを生成する。

```bash
bash /path/to/Graphormer/distributional_graphormer/property-guided/scripts/sample.sh 1 2 /tmp/dig-property-guided 16 1.5
```

catalyst_adsorption_densityでは、README記載のdensity.sh実行を高さごとに繰り返す。たとえばheight_indicesが［0,1,2］の場合、概ね次の3コマンドを順に実行する。

```bash
bash /path/to/Graphormer/distributional_graphormer/catalyst-adsorption/scripts/density.sh 1 2 /tmp/dig-density 0
bash /path/to/Graphormer/distributional_graphormer/catalyst-adsorption/scripts/density.sh 1 2 /tmp/dig-density 1
bash /path/to/Graphormer/distributional_graphormer/catalyst-adsorption/scripts/density.sh 1 2 /tmp/dig-density 2
```

## 8. 出力

成功時は次の情報を返す。

- mode
- summary
- runsまたはcommand群
- workflow固有のパラメーター

output_dirはprotein-ligand workflowでは通常distributional_graphormer/protein-ligand/src/outputになる。protein_system_samplingでは通常distributional_graphormer/protein/outputになる。property_guided_samplingではsave_dir配下に結果を書き出す。catalyst_adsorption_densityでもsave_dir配下に結果を書き出す。

catalyst_adsorption_densityではsummaryに次が含まれる。

- requested_height_count
- completed_height_count
- successful_height_count
- failed_height_count
- last_completed_height_index

height_indicesを明示指定した場合、requested_height_countとcompleted_height_countはその配列長と一致する。全実行成功時はfailed_height_countが0になり、last_completed_height_indexには最後に完了した高さインデックスが入る。

## 9. 現在の制約

- genericなSMILES入力から直接コンフォメーションを出すAPIとしては未対応
- upstream側のdatasetやcheckpoint配置まではorbital-sci-mcpでは自動化しない

## 10. エラー時の見方

主なerror code:

- INPUT_VALIDATION_FAILED
  - graphormer_repo_pathやpdbidが不足している
- UNSUPPORTED_OPERATION
  - 指定workflowが未実装、またはsampling scriptが見つからない
- EXECUTION_FAILED
  - scriptは起動したが環境、checkpoint、dataset、pdbidなどの問題で失敗した

EXECUTION_FAILEDのdetailsには以下が含まれる。

- returncode
- stdout
- stderr
- command

catalyst_adsorption_densityで特定の高さインデックスの実行に失敗した場合は、上記に加えてheight_indexが含まれる。これにより、どの反復実行で停止したかを追跡できる。

height_indicesが空配列の場合はINPUT_VALIDATION_FAILEDとなり、detailsにheight_indicesがそのまま含まれる。

## 11. Integration testの実行方法

opt-inのintegration testは以下のファイルにある。

- tests/test_dig_integration.py

このテストは次の条件を満たした場合だけ実行される。

- DIG_RUN_INTEGRATION=1
- DIG_REPO_PATHが設定済み
- DIG_WORKFLOWが設定済み
- DIG_PDBIDが設定済み
- Graphormer checkout内にdistributional_graphormer/protein-ligand/evaluation/single_datapoint_sampling.shが存在する

protein system用のopt-in integration testも同じファイルに含まれている。こちらは次の条件を満たした場合だけ実行される。

- DIG_PROTEIN_RUN_INTEGRATION=1
- DIG_PROTEIN_REPO_PATHが設定済み
- DIG_PROTEIN_PDBIDが設定済み
- Graphormer checkout内にdistributional_graphormer/protein/run_inference.pyが存在する

equilibrium用のopt-in integration testも同じファイルに含まれている。こちらは次の条件を満たした場合だけ実行される。

- DIG_EQUILIBRIUM_RUN_INTEGRATION=1
- DIG_EQUILIBRIUM_REPO_PATHが設定済み
- DIG_EQUILIBRIUM_NUM_GPUSが必要に応じて設定済み
- DIG_EQUILIBRIUM_BATCH_SIZE_PER_GPUが必要に応じて設定済み
- Graphormer checkout内にdistributional_graphormer/catalyst-adsorption/scripts/density.shが存在する

このintegration testでは、runsの件数に加えてsummaryの件数整合性も検証する。

property-guided用のopt-in integration testも同じファイルに含まれている。こちらは次の条件を満たした場合だけ実行される。

- DIG_PROPERTY_RUN_INTEGRATION=1
- DIG_PROPERTY_REPO_PATHが設定済み
- DIG_PROPERTY_NUM_GPUSが設定済み
- DIG_PROPERTY_BATCH_SIZE_PER_GPUが設定済み
- DIG_PROPERTY_NUM_ATOMSが設定済み
- DIG_PROPERTY_TARGET_BANDGAPが設定済み
- Graphormer checkout内にdistributional_graphormer/property-guided/scripts/sample.shが存在する

最初の雛形として、ルートにあるサンプル環境設定ファイルをコピーして必要値を埋める。

```bash
cp .env.example .env
```

envを反映してintegration testだけを実行する例:

```bash
set -a
source .env
set +a
PYTHONPATH=src pytest -q tests/test_dig_integration.py -m integration
```

注記:

- DIG_WORKFLOWは現在protein_ligand_single_datapoint、protein_system_sampling、property_guided_sampling、catalyst_adsorption_densityに対応している
- DIG_PDBIDはupstream datasetに含まれる値である必要がある
- DIG_PROTEIN_PDBIDはprotein workflow用datasetに含まれる値である必要がある
- DIG_EQUILIBRIUM_HEIGHT_INDICESはカンマ区切りで指定できる
- DIG_PROPERTY_SAVE_DIRは必要に応じて上書きできる
- datasetとcheckpointの配置不足はEXECUTION_FAILEDとして返る