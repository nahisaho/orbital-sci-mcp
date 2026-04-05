# AI4Science MCPサーバー要件定義書

## 1. 文書情報

| 項目 | 値 |
|------|-----|
| 作成日 | 2026-04-01 |
| 更新日 | 2026-04-05 |
| バージョン | 2.0 |
| 対象リポジトリ | orbital-sci-mcp |
| パッケージ名 | `orbital-sci-mcp` v0.1.0 |
| Python要件 | >=3.11 |
| ランタイム依存 | fastmcp >=2.12.3,<4.0.0 / pydantic >=2.11,<3.0 |

### 参照資料

- references/ms-ai4science-tools-final.md
- references/ToolUniverse/ （参照実装）
- dev/ai4science-mcp-design.md
- dev/graphormer-fairseq-evaluate-guide.md
- dev/dig-protein-ligand-guide.md
- dev/graphormer-dig-operations-guide.md

## 1.1 実装到達点サマリ（2026-04-05時点）

Phase 1（共通基盤 + 材料科学）およびPhase 2（分子モデリング + タンパク質科学）が完了し、
9個の科学計算ツールを3ドメインにわたり公開済みである。

| カテゴリ | 実装状況 |
|----------|---------|
| **共通基盤** | stdio / streamable-http 起動、compact mode、CLI (argparse)、環境変数設定、ロギング |
| **MCP公開ツール** | list_tools / get_tool_info / search_tools / execute_tool（4 discovery tools） |
| **Registry + Adapter** | ToolRegistry + BaseAdapter + ExecutionService + StructuredToolError |
| **材料科学 (materials)** | mattersim_predict_energy, mattersim_relax_structure, mattergen_generate_material, mace_predict_energy, mace_calculate_forces |
| **分子モデリング (molecules)** | graphormer_predict_property, dig_sample_conformations (3 workflows), dig_predict_equilibrium (1 workflow) |
| **タンパク質科学 (proteins)** | bioemu_sample_ensemble |
| **テスト** | 14テストファイル、opt-in integration test（Graphormer, DiG 5 workflows） |
| **ソースコード規模** | 約1,700行（src/orbital_sci_mcp/以下） |

---

## 2. 背景

本リポジトリでは、Microsoft AI for Science系ツールをMCPサーバーとして公開し、AIエージェントから統一的に操作可能にする。対象ツール群は references/ms-ai4science-tools-final.md に整理されており、材料科学、創薬、タンパク質設計、気象・地球科学まで広い領域を含む。

各ツールは実行要件が大きく異なる。CPUで即時に扱えるものとGPU前提のもの、外部モデル重みが必要なもの、Python APIが安定しているものとsubprocess起動が必要なものが混在している。そのため、ToolUniverseのMCPサーバー実装を参照しつつ、段階導入可能な共通基盤を設計している。

## 3. 目的

- Microsoft AI for Scienceツール群をMCP互換の統一インターフェイスで公開する
- ツールごとの差分を吸収するアダプター層を設け、個別ツールを段階的に追加できる構成にする
- stdioとHTTPの両トランスポートに対応し、ローカル開発とエージェント統合の両方を成立させる
- ToolUniverseのcompact modeの考え方を取り込み、ツール数が増えてもコンテキスト過多にならない運用を可能にする

## 4. スコープ

### 4.1 開発対象

src/orbital_sci_mcp/ 配下にPython実装のMCPサーバーを構築する。

- MCPサーバーの起動基盤（FastMCPベース）
- ツール定義と登録の共通フレームワーク（ToolRegistry + ToolSpec）
- ツール探索・情報取得・実行の基本API（4 discovery tools）
- Tier1科学計算ツールのアダプター群（6アダプター、9ツール）
- 環境変数およびCLI引数による有効ツール制御
- 依存関係未導入時のgraceful degradation

### 4.2 実装スコープ

| 区分 | 内容 | 状態 |
|------|------|------|
| 共通基盤 | サーバー起動CLI、stdio/http transport、ツールレジストリ、compact mode、discovery tools | **実装済** |
| 材料科学 | MatterSim (2), MatterGen (1), MACE (2) | **実装済** |
| 分子モデリング | Graphormer (1), DiG (2: 4 workflows) | **実装済** |
| タンパク質科学 | BioEmu (1) | **実装済** |

### 4.3 スコープ外

- Tier2以降ツールの全面実装（RetroChimera, TamGen, EvoDiff, Skala, MoLeR等）
- ジョブキュー、非同期ワーカー、分散実行基盤
- GPUクラスター運用、Kubernetes配備、オートスケール
- すべての外部ツールの自動インストール
- 研究用UIやWebフロントエンド
- ToolUniverse互換の1,000+ tools大規模自動公開

## 5. 想定ユーザー

- Claude DesktopやVS Code等から科学ツールを呼び出したい研究者
- 材料科学や創薬の実験パイプラインをエージェントに接続したい開発者
- 複数のAI4Scienceモデルを単一のMCP endpoint配下で扱いたい基盤開発者

## 6. ユースケース

### 6.1 材料科学

- UC-MAT-001: CIFテキストまたは原子番号+座標を入力し、MatterSimでenergy/forces/stressを計算する
- UC-MAT-002: MatterSimでBFGS構造緩和を実行し、緩和後のenergyと構造を取得する
- UC-MAT-003: MatterGenで制約条件付き材料候補を生成し、結果をJSON構造体で受け取る
- UC-MAT-004: MACEでenergy予測またはforces計算を行う
- UC-MAT-005: MatterGenで生成した候補をMatterSimまたはMACEで評価する連携ワークフロー

### 6.2 分子モデリング

- UC-MOL-001: Graphormerのfairseq evaluate workflowを起動して物性評価ジョブを実行する
- UC-MOL-002: DiGのprotein-ligand single datapoint samplingでコンフォメーションを生成する
- UC-MOL-003: DiGのprotein system samplingでタンパク質構造サンプリングを行う
- UC-MOL-004: DiGのproperty-guided samplingでbandgap条件付き材料サンプリングを行う
- UC-MOL-005: DiGのcatalyst-adsorption density workflowで触媒吸着平衡密度を計算する

### 6.3 タンパク質科学

- UC-PRO-001: アミノ酸配列を入力してBioEmuで構造アンサンブルを生成する
- UC-PRO-002: FASTA形式テキストからBioEmuでサンプリングし、PDB/XTCアーティファクトを取得する
- UC-PRO-003: 生成結果を後続の創薬ワークフローに渡す

### 6.4 エージェント利用

- UC-AGT-001: エージェントがcompact modeで最小ツール群だけを見て探索する
- UC-AGT-002: list_toolsでドメイン別フィルタ・availability filterを組み合わせてツールを発見する
- UC-AGT-003: get_tool_infoで入力スキーマと依存関係を取得し、execute_tool経由で実行する
- UC-AGT-004: search_toolsでキーワード検索してツール候補を絞り込む

---

## 7. 機能要件

### 7.1 サーバー起動 (FR-0xx)

| ID | 要件 | 実装状態 |
|----|------|---------|
| FR-001 | Python 3.11以上で動作すること | ✅ `requires-python = ">=3.11"` |
| FR-002 | CLIからstdio transportで起動できること | ✅ `cli.py` → `run_server(transport="stdio")` |
| FR-003 | CLIからstreamable-http transportで起動できること | ✅ `run_server(transport="streamable-http")` |
| FR-004 | host, port, transport, log level, compact modeをCLI引数で切り替えられること | ✅ `parse_args()` で10個の引数を受付 |
| FR-005 | 環境変数 (`ORBITAL_SCI_MCP_*`) からも設定を読み込めること | ✅ `AppConfig.from_env()` |
| FR-006 | CLI引数が環境変数設定を上書きすること | ✅ `build_config()` でmodel_copy(update=) |
| FR-007 | 有効化するドメイン・ツール・無効化ツールをCLI引数で指定できること | ✅ `--enable-domain`, `--enable-tool`, `--disable-tool` |
| FR-008 | デフォルトタイムアウト秒数をCLI引数で指定できること | ✅ `--default-timeout` (default: 300) |

### 7.2 ツール管理 (FR-1xx)

| ID | 要件 | 実装状態 |
|----|------|---------|
| FR-101 | ツール定義をToolSpecとして共通レジストリへ登録できること | ✅ `ToolRegistry.register(spec)` |
| FR-102 | 各ToolSpecはname, description, domain, tags, maturity, input_model, adapter_key, dependency_requirementsを保持すること | ✅ `ToolSpec` Pydanticモデル |
| FR-103 | 有効化するツールを `enabled_tools` で絞り込めること | ✅ `ToolRegistry.configure(enabled_tools=)` |
| FR-104 | ドメイン単位で `enabled_domains` フィルターできること | ✅ `ToolRegistry.configure(enabled_domains=)` |
| FR-105 | 特定ツールを `disabled_tools` で無効化できること | ✅ `ToolRegistry.configure(disabled_tools=)` |
| FR-106 | アダプターファクトリをキー名で登録できること | ✅ `ToolRegistry.register_adapter(key, factory)` |
| FR-107 | ツール名からアダプターインスタンスを生成できること | ✅ `ToolRegistry.create_adapter(name)` |

### 7.3 MCP公開機能 (FR-2xx)

| ID | 要件 | 実装状態 |
|----|------|---------|
| FR-201 | `list_tools` で公開ツール一覧を返せること。domain/available_onlyでフィルタ可能 | ✅ |
| FR-202 | `get_tool_info` でツール詳細（スキーマ・依存関係・availability）を返せること | ✅ |
| FR-203 | `execute_tool` で任意の公開ツールをtool_name + arguments指定で実行できること | ✅ |
| FR-204 | `search_tools` でquery/domain/limit指定のキーワード検索を返せること | ✅ |
| FR-205 | compact modeではdiscovery系（list_tools, get_tool_info, search_tools, execute_tool）のみをFastMCPに直接登録すること | ✅ |
| FR-206 | compact mode無効時は各ToolSpecを個別のFastMCPツールとしても登録すること | ✅ `build_individual_tool()` |
| FR-207 | compact modeでも内部的には有効ツール定義を保持し、execute_tool経由で呼び出せること | ✅ |

### 7.4 アダプター層 (FR-3xx)

| ID | 要件 | 実装状態 |
|----|------|---------|
| FR-301 | 各ツールを共通BaseAdapter抽象クラスを介して実行すること | ✅ `BaseAdapter` ABC |
| FR-302 | Adapterは `validate_input`, `check_availability`, `execute`, `normalize_output` を提供すること | ✅ |
| FR-303 | 依存ライブラリ未導入時はImportErrorを生で出さず、`StructuredToolError` (code=DEPENDENCY_MISSING) を返すこと | ✅ `build_unavailable_response()` |
| FR-304 | GPU必須ツールはGPU利用不可時に `StructuredToolError` (code=GPU_UNAVAILABLE) を返すこと | ✅ `_is_gpu_available()` + BioEmuAdapter |
| FR-305 | 必須入力フィールド不足時に `StructuredToolError` (code=INPUT_VALIDATION_FAILED) を返すこと | ✅ `_ensure_required_fields()` |
| FR-306 | 未サポート操作時に `StructuredToolError` (code=UNSUPPORTED_OPERATION) を返すこと | ✅ `raise_unsupported()` |

### 7.5 科学計算ツール (FR-4xx)

#### 7.5.1 材料科学 (materials ドメイン)

| ID | ツール名 | 説明 | アダプター | 実装状態 |
|----|---------|------|-----------|---------|
| FR-401 | `mattersim_predict_energy` | MatterSimでenergy/forces/stress予測 | MatterSimAdapter | ✅ |
| FR-402 | `mattersim_relax_structure` | MatterSimでBFGS構造緩和 | MatterSimAdapter | ✅ |
| FR-403 | `mattergen_generate_material` | MatterGenで材料候補生成 | MatterGenAdapter | ✅ |
| FR-404 | `mace_predict_energy` | MACEでenergy予測 | MaceAdapter | ✅ |
| FR-405 | `mace_calculate_forces` | MACEでforces計算 | MaceAdapter | ✅ |

**MatterSimAdapter 詳細要件:**
- FR-401a: CIFテキスト (`structure_text`) またはatomic_numbers + positions指定で入力できること
- FR-401b: lattice指定で周期境界条件をサポートすること
- FR-401c: calculator_optionsでfmax, steps等の緩和パラメータを制御できること
- FR-401d: 依存パッケージは `mattersim`, `ase` であること

**MatterGenAdapter 詳細要件:**
- FR-403a: prompt, constraints, sample_count指定で材料生成できること
- FR-403b: constraintsでpretrained_name, model_path, properties_to_condition_on, target_compositions, diffusion_guidance_factorを指定できること
- FR-403c: バッチ実行（batch_size最大16, 自動分割）をサポートすること
- FR-403d: 出力はformula, num_sites, lattice, species, frac_coordsを含むJSON構造体であること

**MaceAdapter 詳細要件:**
- FR-404a: 入力形式はMatterSimAdapterと同一のMaterialStructureInputであること
- FR-404b: mace_mpプリトレインモデルを使用すること
- FR-404c: 依存パッケージは `mace`, `ase` であること

#### 7.5.2 分子モデリング (molecules ドメイン)

| ID | ツール名 | 説明 | アダプター | 実装状態 |
|----|---------|------|-----------|---------|
| FR-411 | `graphormer_predict_property` | Graphormer fairseq evaluateで物性予測 | GraphormerAdapter | ✅ |
| FR-412 | `dig_sample_conformations` | DiGで分子コンフォメーション生成 (3 workflows) | DigAdapter | ✅ |
| FR-413 | `dig_predict_equilibrium` | DiGで平衡密度計算 (1 workflow) | DigAdapter | ✅ |

**GraphormerAdapter 詳細要件:**
- FR-411a: inference_optionsに `graphormer_repo_path`, `dataset_name`, `dataset_source`, `pretrained_model_name` が必須であること
- FR-411b: evaluate.pyをsubprocess.run()で起動すること
- FR-411c: task, arch, num_classes, batch_size, split, seed, criterion, num_workers, metric, save_dir等のオプションを制御できること
- FR-411d: graphormer_repo_pathの存在検証およびevaluate.pyの存在検証を行うこと
- FR-411e: 依存パッケージは `fairseq` であること
- FR-411f: inference_options未指定時は対応モード(fairseq_evaluate)と必須オプションを案内するエラーを返すこと

**DigAdapter 詳細要件:**

dig_sample_conformationsは以下の3 workflowをサポートすること:

| ID | workflow | 必須inference_options | スクリプト |
|----|----------|----------------------|-----------|
| FR-412a | protein_ligand_single_datapoint | graphormer_repo_path, pdbid | single_datapoint_sampling.sh |
| FR-412b | protein_system_sampling | graphormer_repo_path, pdbid | run_inference.py |
| FR-412c | property_guided_sampling | graphormer_repo_path, num_gpus, batch_size_per_gpu, num_atoms, target_bandgap | scripts/sample.sh |

dig_predict_equilibriumは以下の1 workflowをサポートすること:

| ID | workflow | 必須inference_options | スクリプト |
|----|----------|----------------------|-----------|
| FR-413a | catalyst_adsorption_density | graphormer_repo_path | scripts/density.sh |

- FR-412d: DigAdapterはsubprocessベースで各シェルスクリプト/Pythonスクリプトを起動すること
- FR-412e: graphormer_repo_pathの存在検証と、該当スクリプトの存在検証を行うこと
- FR-412f: catalyst_adsorption_density workflowは複数height_indicesのバッチ処理をサポートし、成功/失敗のサマリを返すこと
- FR-412g: protein_system_sampling workflowはcheckpoint_path, feature_path, fasta_path, output_prefixの指定を許容すること
- FR-412h: inference_options未指定時はサポートworkflow一覧と必須オプションを案内するエラーを返すこと

#### 7.5.3 タンパク質科学 (proteins ドメイン)

| ID | ツール名 | 説明 | アダプター | 実装状態 |
|----|---------|------|-----------|---------|
| FR-421 | `bioemu_sample_ensemble` | BioEmuで構造アンサンブル生成 | BioEmuAdapter | ✅ |

**BioEmuAdapter 詳細要件:**
- FR-421a: sequenceまたはfasta_textで入力できること
- FR-421b: sample_count, random_seed指定でサンプリング制御できること
- FR-421c: inference_optionsで model_name, denoiser_type, denoiser_config, batch_size_100, cache_embeds_dir, cache_so3_dir, msa_host_url, filter_samples, steering_config, output_dir を制御できること
- FR-421d: output_dir指定時は永続パスに出力し、未指定時はTemporaryDirectoryに出力すること
- FR-421e: 出力アーティファクト（topology.pdb, samples.xtc, sequence.fasta）の存在を検証して報告すること
- FR-421f: GPU必須であること（`gpu_required = True`）
- FR-421g: 依存パッケージは `bioemu` であること

### 7.6 スキーマ定義 (FR-5xx)

| ID | 要件 | 実装状態 |
|----|------|---------|
| FR-501 | 全入力スキーマはPydantic BaseModelで定義すること | ✅ |
| FR-502 | 共通基底 `CommonToolInput` にinput_format, payload_version, timeout_seconds, metadataを保持すること | ✅ |
| FR-503 | 材料科学入力は `MaterialStructureInput` (structure_text, atomic_numbers, positions, lattice, calculator_options) と `MaterialGenerationInput` (prompt, constraints, sample_count) で定義すること | ✅ |
| FR-504 | 分子モデリング入力は `MoleculeInput` (smiles, molecule_block, conformer_count, target_property, generation_options, inference_options) で定義すること | ✅ |
| FR-505 | タンパク質科学入力は `ProteinSequenceInput` (sequence, fasta_text, sample_count, random_seed, inference_options) で定義すること | ✅ |

### 7.7 実行サービス (FR-6xx)

| ID | 要件 | 実装状態 |
|----|------|---------|
| FR-601 | `ExecutionService` がtool_name + payloadを受けて、アダプター解決→入力検証→availability確認→実行→出力正規化の一連パイプラインを処理すること | ✅ |
| FR-602 | 各実行に一意の `request_id` (UUID) を付与すること | ✅ |
| FR-603 | 実行時間 (`runtime_seconds`) をmetadataに記録すること | ✅ |
| FR-604 | 未知ツール名に対して UNSUPPORTED_OPERATION エラーとremediation（list_tools/search_toolsの案内）を返すこと | ✅ |
| FR-605 | アダプター例外を `ToolExecutionException` → `StructuredToolError` に変換すること | ✅ |
| FR-606 | 予期しない例外を `internal_error` → `StructuredToolError` (code=INTERNAL_ERROR) に変換すること | ✅ |

### 7.8 診断と観測性 (FR-7xx)

| ID | 要件 | 実装状態 |
|----|------|---------|
| FR-701 | stdioモードではログを標準エラー (stderr) へ出力し、JSON-RPCストリームを汚染しないこと | ✅ `configure_logging()` |
| FR-702 | httpモードではログを標準出力 (stdout) へ出力すること | ✅ |
| FR-703 | ツール実行レスポンスのmetadataに request_id, tool_name, backend, availability_status, runtime_seconds を含められること | ✅ |
| FR-704 | ログレベルをCLI引数 (`--log-level`) で切り替えられること | ✅ |

---

## 8. 非機能要件

### 8.1 保守性

| ID | 要件 | 実装状態 |
|----|------|---------|
| NFR-001 | 個別ツール追加時に既存サーバー本体を変更しなくてよい構成であること（registry.pyへのspec/adapter追加のみ） | ✅ |
| NFR-002 | ドメイン別にschemas/, adapters/配下でモジュール分割されていること | ✅ |
| NFR-003 | 全アダプターがBaseAdapterを継承する統一構造であること | ✅ |

### 8.2 信頼性

| ID | 要件 | 実装状態 |
|----|------|---------|
| NFR-101 | 利用不能な1ツールが原因でサーバー全体が起動失敗しないこと | ✅ lazy import + availability check |
| NFR-102 | ツール単位でavailability checkを行い、未利用環境でもdiscovery機能は維持すること | ✅ |
| NFR-103 | 全てのアダプター例外が `StructuredToolError` に変換され、サーバープロセスがクラッシュしないこと | ✅ |

### 8.3 性能

| ID | 要件 | 実装状態 |
|----|------|---------|
| NFR-201 | 軽量なdiscovery系操作はローカル環境で1秒程度を目標とすること | ✅ |
| NFR-202 | 実計算系ツールは同期実行を基本とし、timeout_seconds制御を持つこと | ✅ (default: 300秒) |
| NFR-203 | 将来の非同期化を阻害しないinterface設計であること | ✅ ExecutionContext分離 |

### 8.4 可搬性

| ID | 要件 | 実装状態 |
|----|------|---------|
| NFR-301 | Linux環境を第一対象とすること | ✅ |
| NFR-302 | ローカルCPU環境でも起動でき、discovery機能が動作すること | ✅ |
| NFR-303 | GPUの有無によって利用可能ツールが変わる設計を許容すること | ✅ `gpu_required` flag |

---

## 9. アーキテクチャ要件

### 9.1 基盤方針

- FastMCP (>=2.12.3) をベースとする
- 起動エントリポイント（cli.py）とツール定義（registry.py）を分離する
- stdioモードではログをstderrに逃がす
- compact modeを持つ（discovery 4ツールのみFastMCPに登録）
- 単純なFastMCPデコレータ乱立ではなく、registry + adapter + execution serviceで管理する

### 9.2 モジュール構成（実装済み）

```
src/orbital_sci_mcp/
├── __init__.py          # パッケージ公開API (AppConfig, ToolRegistry, create_server等)
├── cli.py               # CLIエントリポイント (argparse, build_config, main)
├── config.py            # AppConfig (Pydantic, 環境変数/CLI引数)
├── errors.py            # StructuredToolError, ToolExecutionException
├── execution.py         # ExecutionService (ツール実行パイプライン)
├── logging_config.py    # configure_logging (transport別ハンドラ設定)
├── models.py            # ToolSpec, DependencyRequirement, ExecutionContext, ToolExecutionResponse等
├── registry.py          # ToolRegistry, create_default_registry
├── server.py            # create_server, run_server (FastMCPインスタンス構築)
├── adapters/
│   ├── base.py          # BaseAdapter (ABC: validate_input, check_availability, execute等)
│   ├── bioemu.py        # BioEmuAdapter (GPU必須, bioemu.sample.main起動)
│   ├── dig.py           # DigAdapter (subprocess: 4 workflows)
│   ├── graphormer.py    # GraphormerAdapter (subprocess: fairseq evaluate)
│   ├── mace.py          # MaceAdapter (mace.calculators.mace_mp)
│   ├── mattergen.py     # MatterGenAdapter (mattergen.scripts.generate)
│   ├── mattersim.py     # MatterSimAdapter (mattersim.forcefield.MatterSimCalculator)
│   └── utils.py         # material_input_to_atoms, atoms_to_dict, to_serializable
├── schemas/
│   ├── common.py        # CommonToolInput (payload_version, timeout_seconds, metadata)
│   ├── materials.py     # MaterialStructureInput, MaterialGenerationInput
│   ├── molecules.py     # MoleculeInput
│   └── proteins.py      # ProteinSequenceInput
└── tools/
    ├── discovery.py     # build_list_tools, build_get_tool_info, build_search_tools
    └── execution_tools.py  # build_execute_tool, build_individual_tool
```

### 9.3 compact mode要件

compact modeでは以下のみをFastMCPに直接登録する:
- `list_tools`
- `get_tool_info`
- `search_tools`
- `execute_tool`

compact mode無効時は上記に加えて、registryに登録された全ToolSpecが個別のFastMCPツールとしても登録される。

### 9.4 依存関係管理

| 区分 | パッケージ | 役割 |
|------|-----------|------|
| **必須** | fastmcp >=2.12.3,<4.0.0 | MCPプロトコル基盤 |
| **必須** | pydantic >=2.11,<3.0 | スキーマ定義・検証 |
| **optional: materials** | ase, mattersim, mattergen, mace-torch | 材料科学ツール群 |
| **optional: molecules** | rdkit, graphormer (fairseq) | 分子モデリングツール群 |
| **optional: proteins** | bioemu, torch | タンパク質科学ツール群 |
| **optional: dev** | pytest, ruff | 開発・テスト |

---

## 10. インターフェイス要件

### 10.1 ツール名

- ツール名はreferences/ms-ai4science-tools-final.mdの候補名を原則踏襲する
- 命名はsnake_caseとする
- 同一バックエンドで接頭辞を揃える（`mattersim_*`, `mace_*`, `dig_*`, `bioemu_*`等）

### 10.2 入力形式

- JSON schemaベースでPydantic BaseModelとして定義する
- 材料構造データはCIFテキスト (`structure_text`) またはatomic_numbers + positionsで入力できる
- 分子データはSMILES (`smiles`) またはmolecule_block、もしくはinference_options辞書で制御する
- タンパク質データはsequenceまたはfasta_textで入力できる
- 入力検証エラーは人間が修正可能なメッセージとremediationを含む

### 10.3 出力形式

- すべてのツール実行結果は `ToolExecutionResponse` (success, data, error, metadata) で返す
- metadataにはrequest_id, tool_name, backend, availability_status, runtime_secondsを含む
- エラーは `StructuredToolError` (code, message, details, remediation, retryable) で構造化する
- 数値計算系の結果は後続ツールが扱いやすいJSON（リスト・辞書）で返す

### 10.4 エラーコード体系（実装済み）

| code | 用途 | 例 |
|------|------|-----|
| `DEPENDENCY_MISSING` | optional dependency未導入 | mattersimパッケージ不足 |
| `GPU_UNAVAILABLE` | CUDA必須だがGPU不可 | BioEmu実行時 |
| `INPUT_VALIDATION_FAILED` | 必須入力フィールド不足 | inference_optionsの必須キー不足 |
| `UNSUPPORTED_OPERATION` | 未対応操作・未知ツール | 未実装workflowの指定 |
| `EXECUTION_FAILED` | subprocess実行失敗 | Graphormer/DiGコマンドのreturncode != 0 |
| `INTERNAL_ERROR` | 予期しないサーバー内部エラー | キャッチされない例外 |

---

## 11. セキュリティ要件

| ID | 要件 | 実装状態 |
|----|------|---------|
| SEC-001 | 任意Pythonコード実行を受け付けないこと | ✅ 入力はPydanticスキーマで検証 |
| SEC-002 | 外部コマンド実行（subprocess）はアダプター内の限定スクリプトのみ許可すること | ✅ Graphormer/DiGのみ |
| SEC-003 | graphormer_repo_path等のパス入力は存在検証を行うこと | ✅ `Path.exists()` チェック |
| SEC-004 | 機密情報は環境変数から受け取り、ログへ出力しないこと | ✅ |

---

## 12. テスト要件

### 12.1 テスト構成（実装済み）

| テストファイル | 対象 | 種別 |
|---------------|------|------|
| test_registry.py | ToolRegistry登録・フィルタ・検索 | 単体 |
| test_server.py | create_server、compact mode公開制御 | 単体 |
| test_cli.py | CLI引数パース、AppConfig構築 | 単体 |
| test_execution.py | ExecutionService実行パイプライン | 単体 |
| test_smoke.py | CLIエントリポイント、fastmcp存在時のcreate_server | スモーク |
| test_mattersim_adapter.py | MatterSimAdapter | 単体 |
| test_mattergen_adapter.py | MatterGenAdapter | 単体 |
| test_mace_adapter.py | MaceAdapter | 単体 |
| test_graphormer_adapter.py | GraphormerAdapter | 単体 |
| test_bioemu_adapter.py | BioEmuAdapter | 単体 |
| test_dig_adapter.py | DigAdapter (全workflow) | 単体 |
| test_graphormer_integration.py | Graphormer fairseq evaluate | opt-in integration |
| test_dig_integration.py | DiG 5 workflows | opt-in integration |
| conftest.py | テスト共通フィクスチャ | - |

### 12.2 テスト方針

- 単体テスト: optional dependency未導入でもmock/patchで実行可能
- integration test: 環境変数 (`GRAPHORMER_RUN_INTEGRATION=1`, `DIG_RUN_INTEGRATION=1` 等) でopt-in制御
- pytest対象はtests/配下に固定 (`pytest.ini`)
- references/ToolUniverse/tests は通常テスト収集対象外

---

## 13. 段階導入方針

### Phase 1 — 共通基盤 + 材料科学 (完了)

- サーバー基盤（FastMCP + stdio/http + CLI + config）
- compact mode
- registry/adapter/execution service抽象
- MatterSim (2ツール), MatterGen (1ツール), MACE (2ツール)

### Phase 2 — 分子モデリング + タンパク質科学 (完了)

- Graphormer fairseq evaluate workflow
- DiG 4 workflows (protein-ligand, protein-system, property-guided, catalyst-adsorption)
- BioEmu構造アンサンブル生成
- StructuredToolErrorベースのエラーモデル標準化

### Phase 3 — 拡張ツール + 高度化 (未着手)

- Tier2ツール追加: RetroChimera, TamGen, EvoDiff, Skala, MoLeR
- search_toolsの高度化（現状はname/descriptionの部分一致検索）
- 長時間実行ジョブの非同期化
- 外部ストレージ連携
- パストラバーサル防止の強化

---

## 14. 受け入れ基準

| ID | 基準 | 状態 |
|----|------|------|
| AC-001 | src/配下にMCPサーバーの実装一式が作成されていること | ✅ |
| AC-002 | stdioとHTTPの両モードで起動できること | ✅ |
| AC-003 | compact modeでdiscovery系最小ツールのみ公開できること | ✅ |
| AC-004 | 3ドメイン（materials, molecules, proteins）に対して6アダプター、9ツールが存在すること | ✅ |
| AC-005 | optional dependency未導入時でもlist_toolsとget_tool_infoが動作すること | ✅ |
| AC-006 | ツール実行時に構造化された成功レスポンスまたは説明可能な失敗レスポンスを返すこと | ✅ |
| AC-007 | 14テストファイルが存在し、基本テストがpassすること | ✅ |
| AC-008 | Graphormer/DiGのopt-in integration testが環境変数でゲートされていること | ✅ |

---

## 15. 未確定事項

### 未解決

- 各upstreamパッケージの正式なインストール方法とライセンス条件の最終確認
- BioEmuをローカル推論前提にするか、将来リモートバックエンドを許容するか
- 長時間実行タスクに対するcancelの扱い（timeoutは実装済み）
- CIF、PDB、SMILES、FASTAなどの共通入力表現をどこまで抽象化するか
- パストラバーサル防止の体系的な対策（現状はPath.exists()検証のみ）

### 解消済み

- GraphormerとDiGは別adapterとして実装（確定）
- DiGは4 workflowを2ツール（dig_sample_conformations, dig_predict_equilibrium）に集約（確定）
- subprocess経由のワークフロー起動パターンを標準化（GraphormerAdapter, DigAdapterで実装済み）
- エラーモデルはStructuredToolErrorで統一（確定）

---

## 16. 変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-04-01 | 1.0 | 初版作成。Phase 1 MVP要件を定義 |
| 2026-04-02 | 1.5 | Phase 2実装到達を反映。Graphormer/DiG/BioEmu追加、integration test方針追記 |
| 2026-04-05 | 2.0 | ソースコード全体を参照し全面改訂。ユースケース詳細化、ツール別詳細要件追加、スキーマ/実行サービス/エラーコード体系の要件追加、実装状態を全項目に付記 |