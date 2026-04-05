# AI4Science MCP Server設計書

## 1. 文書情報

- 作成日: 2026-04-01
- 更新日: 2026-04-05
- 対象要件: dev/ai4science-mcp-requirements.md
- 対象リポジトリ: orbital-sci-mcp
- 参照実装:
  - references/ToolUniverse/src/tooluniverse/smcp.py
  - references/ToolUniverse/src/tooluniverse/smcp_server.py
  - references/ToolUniverse/src/tooluniverse/mcp_tool_registry.py

## 1.1 現在の設計反映範囲

本設計書は初期設計書として作成したが、2026-04-02時点では以下の実装済み構成を反映する。

- registry には materials (5) / molecules (3) / proteins (1) の 9 ToolSpec を登録済み
- 6 adapter: MatterSimAdapter, MatterGenAdapter, MaceAdapter, GraphormerAdapter, DigAdapter, BioEmuAdapter
- GraphormerAdapter は fairseq evaluate workflow を subprocess で起動する
- DigAdapter は sampling系 3 workflow と equilibrium系 1 workflow を subprocess で起動する
- tests/ 配下に 14 テストファイル（unit test、smoke test、workflow別 opt-in integration test）を配置する

## 2. 設計目的

本設計書は、要件定義書で定めたAI4Science MCP Serverを実装可能な粒度へ落とし込むためのものである。実装方針は以下の3点に集約する。

- FastMCPベースでstdioとstreamable-httpを統一的に扱う
- registry + adapter構成でツール追加コストを下げる
- optional dependency前提で、未導入環境でもdiscovery機能を維持する

## 3. 設計方針

### 3.1 基本方針

- サーバー本体はMCPプロトコル対応と公開制御に専念する
- 科学ツール固有の処理はadapterに閉じ込める
- ツールのメタ情報はregistryに一元管理する
- MCPに直接公開する関数は最小限にし、内部ではregistryを通じてdispatchする
- compact modeを標準機能として設計し、ツール追加後もMCP公開数を制御できるようにする

### 3.2 段階導入方針

Phase 1では基盤と材料科学3ツールを先行実装する。Graphormer/DiGとBioEmuは同じ枠組みに追加できることを優先し、設計上は初日から拡張可能な形にしておく。

実装注記:

- 2026-04-02時点で Graphormer / DiG / BioEmu は初期拡張まで実装済み
- 現在は Phase 2 の一部を前倒しで取り込んだ状態として扱う

## 4. システム全体構成

### 4.1 論理構成

システムは以下の6層で構成する。

1. CLI層
2. Server層
3. MCPPublicTool層
4. Registry/Catalog層
5. Adapter層
6. BackendIntegration層

### 4.2 データフロー

通常モードのツール呼び出しフロー:

1. クライアントがMCP経由でツールを呼ぶ
2. FastMCPが公開関数へルーティングする
3. 公開関数がregistryから対象ツール定義を取得する
4. registryが対応adapterを初期化または取得する
5. adapterが入力検証、実行可否判定、バックエンド呼び出し、出力正規化を行う
6. 共通レスポンス形式へ変換して返す

compact modeのdiscoveryフロー:

1. クライアントはlist_tools、search_tools、get_tool_infoのみを見る
2. execute_toolで内部登録済みツールを指定して実行する
3. 個別ツールはMCPのトップレベル公開対象にしない

## 5. ディレクトリ設計

初期実装ではsrc配下を以下のように構成する。

```text
src/
  orbital_sci_mcp/
    __init__.py
    cli.py
    server.py
    config.py
    logging_config.py
    errors.py
    models.py
    registry.py
    execution.py
    tools/
      __init__.py
      discovery.py
      execution_tools.py
    adapters/
      __init__.py
      base.py
      mattersim.py
      mattergen.py
      mace.py
      graphormer.py
      dig.py
      bioemu.py
      utils.py
    schemas/
      __init__.py
      common.py
      materials.py
      molecules.py
      proteins.py
```

責務は以下の通りとする。

- cli.py: 引数解析、設定読込、起動モード分岐
- server.py: FastMCPインスタンス生成と公開ツール登録
- config.py: 環境変数とCLI引数を統合した設定モデル
- logging_config.py: stdioとHTTPでのログ出力切替
- errors.py: エラーコード、構造化例外、変換関数
- models.py: ツール定義、依存定義、実行結果などのPydanticモデル
- registry.py: ツール定義の登録、公開判定、検索、adapter解決
- execution.py: request id生成、メトリクス採取、実行ラッパー
- tools/discovery.py: list_tools、get_tool_info、search_toolsのMCP公開関数
- tools/execution_tools.py: execute_toolと通常公開モードの薄いラッパー
- adapters/*.py: 各backendとの統合
- schemas/*.py: 入力と出力のJSON schema/Pydanticモデル

## 6. 主要コンポーネント設計

### 6.1 AppConfig

目的:

- 実行時の全設定を一元管理する

主な保持項目:

- server_name
- transport
- host
- port
- log_level
- compact_mode
- enabled_domains
- enabled_tools
- disabled_tools
- optional_dependency_policy
- default_timeout

設計ポイント:

- CLI引数を最優先し、その次に環境変数、最後にデフォルト値を採用する
- compact mode時の公開ルールはconfigではなくregistry側で判定する

### 6.2 ToolSpec

目的:

- MCP公開に必要なメタ情報とadapter解決情報を保持する

保持項目:

- name
- description
- domain
- tags
- maturity
- input_model
- output_model
- adapter_key
- dependency_requirements
- availability_policy

補足:

- dependency_requirementsにはPythonパッケージ名、GPU必須有無、モデル重み要件、環境変数要件を持たせる

### 6.3 ToolRegistry

目的:

- 全ツール定義を登録し、公開候補と実行対象を引き当てる

主な責務:

- ツール登録
- ツール名による取得
- ドメイン/タグ検索
- compact modeに応じた公開ツール集合の生成
- adapterファクトリの解決

主要メソッド:

- register(spec: ToolSpec)
- get(name: str) -> ToolSpec
- list_public_tools(compact_mode: bool) -> list[ToolSpec]
- search(query: str, domain: str | None) -> list[ToolSpec]
- create_adapter(name: str) -> BaseAdapter

設計ポイント:

- registry自体はadapter instanceを長期キャッシュしない
- 将来GPUメモリやモデルロード戦略が必要になった場合に備え、adapter factoryを挟む

### 6.4 BaseAdapter

目的:

- 各AI4Science backendを同じ実行モデルで扱う

必須インターフェイス:

- tool_name() -> str
- validate_input(payload: dict) -> BaseModel
- check_availability() -> AvailabilityResult
- execute(validated_input: BaseModel, context: ExecutionContext) -> Any
- normalize_output(raw_result: Any, context: ExecutionContext) -> ToolExecutionResponse

補助メソッド:

- import_backend()
- describe_backend()
- build_unavailable_response()

設計ポイント:

- validate_inputはPydanticモデル変換を含む
- check_availabilityはimport可否、GPU可否、モデル重み可否、設定可否を統一評価する
- normalize_outputでsuccess/data/error/metadata構造へ統一する

### 6.5 ExecutionService

目的:

- ツール実行時の共通処理を一箇所へ寄せる

主な責務:

- request_id発行
- 実行時間計測
- 構造化例外の変換
- adapter実行とレスポンス正規化

主要メソッド:

- execute_tool(tool_name: str, payload: dict) -> ToolExecutionResponse

## 7. MCP公開設計

### 7.1 公開ツール一覧

通常モード:

- list_tools
- get_tool_info
- search_tools
- execute_tool
- 個別ツール関数群

compact mode:

- list_tools
- get_tool_info
- search_tools
- execute_tool

### 7.2 discovery系ツール仕様

list_tools:

- 入力: domain、tag、available_onlyなどの軽量フィルター
- 出力: name、description、domain、availability_summary、input schema summary

get_tool_info:

- 入力: tool_name
- 出力: 詳細説明、依存要件、入力schema、想定出力、利用例

search_tools:

- 入力: query、domain、limit
- 出力: relevance付き候補一覧

### 7.3 execute_tool仕様

入力:

- tool_name
- arguments

出力:

- ToolExecutionResponse

設計ポイント:

- compact modeではexecute_toolが内部dispatchの唯一の実行入口になる
- 通常モードの個別ツール関数も内部ではexecute_toolと同じ経路へ寄せる

## 8. クラス設計

### 8.1 ExecutionContext

保持項目:

- request_id
- tool_name
- start_time
- transport
- caller_metadata
- timeout_seconds

用途:

- ログ相関
- 監査と計測
- adapter内での補助情報引き渡し

### 8.2 AvailabilityResult

保持項目:

- available
- status
- missing_packages
- missing_env_vars
- gpu_required
- gpu_available
- missing_artifacts
- message

status候補:

- available
- dependency_missing
- gpu_unavailable
- model_not_ready
- unsupported_environment

### 8.3 ToolExecutionResponse

保持項目:

- success
- data
- error
- metadata

metadataの標準項目:

- request_id
- tool_name
- backend
- runtime_seconds
- availability_status

### 8.4 StructuredToolError

保持項目:

- code
- message
- details
- remediation
- retryable

error code候補:

- DEPENDENCY_MISSING
- GPU_UNAVAILABLE
- MODEL_ARTIFACT_MISSING
- INPUT_VALIDATION_FAILED
- EXECUTION_FAILED
- TIMEOUT
- UNSUPPORTED_OPERATION
- INTERNAL_ERROR

## 9. モジュール間シーケンス

### 9.1 サーバー起動シーケンス

1. cli.pyが引数を解釈する
2. config.pyがAppConfigを構築する
3. logging_config.pyがtransportに応じたloggerを初期化する
4. registry.pyが標準ToolSpec群を登録する
5. server.pyがFastMCP serverを生成する
6. discovery系とexecute系ツールを登録する
7. 通常モードの場合のみ個別ツールをFastMCPへ追加登録する
8. transportに応じてrunを開始する

### 9.2 ツール実行シーケンス

1. MCP関数がexecution serviceを呼ぶ
2. execution serviceがToolSpecを取得する
3. adapterを生成する
4. adapterが入力検証を行う
5. adapterがavailabilityを検査する
6. 利用不能なら構造化エラー応答を返す
7. 利用可能ならbackendを実行する
8. 実行結果をnormalize_outputする
9. execution serviceがruntimeとrequest idをmetadataに追加する
10. 呼び出し元へ返す

## 10. 入力モデル設計

### 10.1 共通入力モデル

共通基底フィールド:

- input_format
- payload_version
- timeout_seconds
- metadata

### 10.2 材料科学系入力

候補フィールド:

- structure_text
- structure_format
- atomic_numbers
- positions
- lattice
- calculator_options

対応フォーマット:

- cif
- poscar
- xyz
- ase_atoms_json

### 10.3 分子系入力

候補フィールド:

- smiles
- molecule_block
- conformer_count
- target_property
- generation_options

### 10.4 タンパク質系入力

候補フィールド:

- sequence
- fasta_text
- sample_count
- random_seed
- inference_options

## 11. 出力モデル設計

### 11.1 共通出力

```json
{
  "success": true,
  "data": {},
  "error": null,
  "metadata": {
    "request_id": "req-...",
    "tool_name": "mattersim_predict_energy",
    "backend": "mattersim",
    "runtime_seconds": 0.42,
    "availability_status": "available"
  }
}
```

### 11.2 材料科学系出力

候補フィールド:

- energy
- forces
- stress
- relaxed_structure
- units

### 11.3 分子系出力

候補フィールド:

- predicted_properties
- embeddings
- conformers
- scores

### 11.4 タンパク質系出力

候補フィールド:

- ensemble_structures
- confidence_scores
- dynamics_summary

## 12. ツール設計

### 12.1 実装済みツール（9 ToolSpec）

MatterSim:

- mattersim_predict_energy
- mattersim_relax_structure

MatterGen:

- mattergen_generate_material

MACE:

- mace_predict_energy
- mace_calculate_forces

Graphormer:

- graphormer_predict_property

DiG:

- dig_sample_conformations（3 workflows: protein_ligand, protein_system, property_guided）
- dig_predict_equilibrium（1 workflow: catalyst_adsorption_density）

BioEmu:

- bioemu_sample_ensemble

### 12.2 ツール登録方法

ツール定義はコードで静的登録する。初期段階では外部JSONによる定義ではなく、PythonモジュールにToolSpec一覧を持ち、起動時にregistryへ投入する。

理由:

- adapter classとの対応が明確
- optional dependency条件をコードで表現しやすい
- 仕様変更が多い初期フェーズで追従が容易

将来はYAML/JSON化を検討してよい。

### 12.3 Tier2対象ツール（Phase 3）

Phase 1の6ツール群が安定した後に追加するTier2候補を以下の優先順位で導入する。

| 優先度 | ツール | 分野 | tool候補数 | 根拠 |
|--------|--------|------|------------|------|
| T2-1 | **TamGen** | 創薬・分子生成 | 4 | BioEmu/DiGとの直接パイプライン（構造→分子設計→動態予測）。Nature Communications掲載実績 |
| T2-2 | **RetroChimera** | 合成化学 | 4 | TamGen/MoLeRで生成した分子の合成ルート計画。Azure AI Foundryカタログ掲載済み |
| T2-3 | **EvoDiff** | タンパク質工学 | 4 | BioEmuと「配列設計→動態予測」ワークフロー構築可能。GitHub⭐665で利用実績多い |
| T2-4 | **Skala** | 量子化学・DFT | 4 | MatterSimで粗スクリーニング→Skalaで高精度検証。`pip install microsoft-skala`でPySCF統合可能 |
| T2-5 | **MoLeR** | 分子設計 | 4 | スキャフォールド制約付き分子最適化。TamGenとは入力形式が異なり相補的 |

優先順位の決定基準:

1. 既存Tier1ツールとのパイプライン接続性（BioEmu→TamGen→RetroChimera）
2. API適性（入出力が明確でadapter化しやすいか）
3. コミュニティ利用実績（GitHub stars、論文引用数）
4. optional dependencyの複雑さ（pip installで完結するか）

各ツールのMCP tool候補:

- **TamGen**: `tamgen_generate_molecules`, `tamgen_refine_compound`, `tamgen_dock_evaluate`, `tamgen_batch_generate`
- **RetroChimera**: `retro_predict_single_step`, `retro_plan_multistep`, `retro_evaluate_route`, `retro_suggest_alternatives`
- **EvoDiff**: `evodiff_generate_sequence`, `evodiff_scaffold_motif`, `evodiff_generate_idr`, `evodiff_conditional_generate`
- **Skala**: `skala_single_point_energy`, `skala_optimize_geometry`, `skala_reaction_energy`, `skala_benchmark_functional`
- **MoLeR**: `moler_generate_from_scaffold`, `moler_optimize_molecule`, `moler_sample_diverse`, `moler_score_candidates`

Adapter実装方針:

- Tier1と同一のBaseAdapter / ToolSpec / ToolExecutionResponseパターンを踏襲する
- TamGen/RetroChimeraはsubprocessベース（Graphormer/DiGと同パターン）
- EvoDiff/Skala/MoLeRはPython callableベース（MatterSim/MACEと同パターン）
- 各adapterは独立した`extras`をpyproject.tomlに追加する

## 13. Adapter詳細設計

### 13.1 MatterSimAdapter

責務:

- 構造入力をASE Atoms相当へ変換
- MatterSim calculatorをロード
- energy、force、stress、relaxを実行

availability条件:

- mattersim import成功
- 必要に応じてGPU/CPU backendが使用可能

### 13.2 MatterGenAdapter

責務:

- 生成条件の検証
- MatterGen backend呼び出し
- 生成構造をJSON互換形式へ正規化

### 13.3 MaceAdapter

責務:

- ASE Atoms互換構造の受理
- MACE foundation modelまたは指定モデルのロード
- energy/force計算

### 13.4 GraphormerAdapter

責務:

- MoleculeInput入力検証（inference_options必須）
- fairseq evaluateベースのGraphormer評価ジョブをsubprocess.run()で起動
- stdout/stderrを含む実行結果の返却

補足:

- upstreamの公開経路は主にevaluate.pyによる評価ワークフローであり、単一SMILES向けの安定した公開Python推論APIは確認できていない
- 実運用用の引数テンプレートはdev/graphormer-fairseq-evaluate-guide.mdを参照する

### 13.5 DigAdapter

責務:

- 分子入力とサンプリング条件の処理
- conformer候補の返却

2026-04-02時点の補足:

- dig_sample_conformations と dig_predict_equilibrium を単一adapter内で受ける
- tool_name と dig_workflow の組み合わせで upstream workflow を切り替える
- 対応workflowは protein_ligand_single_datapoint、protein_system_sampling、property_guided_sampling、catalyst_adsorption_density
- catalyst_adsorption_density の返却値には runs 配列に加えて summary を含める
- 実運用用の引数テンプレートは dev/dig-protein-ligand-guide.md と dev/graphormer-dig-operations-guide.md を参照する

### 13.6 BioEmuAdapter

責務:

- アミノ酸配列検証
- サンプル数、seed、推論設定の処理
- 構造アンサンブル結果の整形

設計上の注意:

- BioEmuはローカル推論を前提にしつつ、将来remote backendに差し替え可能な実装境界を維持する

## 14. compact mode設計

### 14.1 判定ルール

compact_mode=trueの場合、registryは公開ツール一覧の生成時にdiscovery系の固定リストだけを返す。

固定公開ツール:

- list_tools
- get_tool_info
- search_tools
- execute_tool

### 14.2 内部保持

- registryは全ToolSpecを保持する
- execute_toolはcompact mode時でも全登録ツールへdispatchできる
- list_toolsはcompact mode時、discovery系と内部登録済みツールの概要件数を返す

### 14.3 理由

- ToolUniverseのcompact modeの長所を取り込み、MCP tool数を抑えながら実行能力を維持するため

## 15. エラー処理設計

### 15.1 方針

- Python例外をそのまま返さない
- adapter内の既知エラーはStructuredToolErrorに変換する
- 不明例外はINTERNAL_ERRORとしてラップする

### 15.2 remediations例

- DEPENDENCY_MISSING: 必要なpip installコマンド例を返す
- GPU_UNAVAILABLE: CPU fallbackの可否またはGPU必須である旨を返す
- MODEL_ARTIFACT_MISSING: モデル重み配置方法または環境変数名を返す
- INPUT_VALIDATION_FAILED: 必須フィールドと期待フォーマットを返す

## 16. ログ設計

### 16.1 標準ログ項目

- timestamp
- level
- request_id
- tool_name
- event
- duration_ms
- transport

### 16.2 transport別出力

- stdio: stderrのみ
- HTTP: stdout/stderrどちらでもよいがアプリログとアクセスログを分けられる形にする

## 17. 設定設計

### 17.1 CLIオプション

初期案:

- --transport stdio|http
- --host
- --port
- --name
- --compact-mode
- --log-level
- --enable-domain DOMAIN (複数指定時はオプションを繰り返す)
- --enable-tool TOOL_NAME
- --disable-tool TOOL_NAME
- --default-timeout

### 17.2 環境変数

初期案:

- ORBITAL_SCI_MCP_TRANSPORT
- ORBITAL_SCI_MCP_HOST
- ORBITAL_SCI_MCP_PORT
- ORBITAL_SCI_MCP_COMPACT_MODE
- ORBITAL_SCI_MCP_LOG_LEVEL

必要に応じてbackend固有の環境変数をadapter側で参照する。

## 18. テスト設計

### 18.1 単体テスト対象

- AppConfigの優先順位
- ToolRegistryの登録と検索
- compact modeの公開制御
- BaseAdapter派生クラスのavailability判定
- StructuredToolError変換

### 18.2 結合テスト対象

- stdio起動とdiscovery呼び出し
- HTTP起動とtool execution呼び出し
- optional dependency未導入時のgraceful degradation

### 18.3 テストダブル

実backendに強く依存するツールは、Phase 1ではfake adapterまたはmock backendで最低限の契約テストを持つ。

## 19. 実装順序

1. models.py、errors.py、config.pyを作る
2. registry.pyとbase adapterを作る
3. execution.pyとMCP公開ツールを作る
4. server.pyとcli.pyを実装する
5. MatterSim、MatterGen、MACE adapterを作る
6. GraphormerとBioEmu adapterを追加する
7. テストを追加する

実装注記:

- 2026-04-02時点で 1 から 7 は完了済み
- 現在は DiG workflow追加、integration test追加、運用ドキュメント整備まで進んでいる

## 20. 実装上の判断事項

現時点では以下を設計決定とする。

- Pythonパッケージ名はorbital_sci_mcpとする
- Pydanticモデルで入力/出力契約を定義する
- registryは静的登録方式を採用する
- 個別ツール公開とexecute_toolは同一実行経路を使う
- long-running job用の非同期基盤は実装せず、timeoutフィールドだけ先に設ける

## 21. 将来拡張ポイント

### 21.1 Tier2ツール追加（Phase 3）

12.3節で定義したTier2候補5ツール（TamGen → RetroChimera → EvoDiff → Skala → MoLeR）を順次追加する。各ツールは既存のBaseAdapter / registry / ToolSpec基盤をそのまま再利用し、adapterモジュールの追加のみで導入可能とする。

### 21.2 インフラ拡張

- 非同期ジョブ管理
- リモートbackend adapter
- YAML/JSONベースのツール宣言
- エンベディングやキーワードによる高機能search_tools
- ToolUniverse互換の自動ローダー

## 22. 実装開始条件

この設計書を基に実装を開始する条件は以下とする。

- src/orbital_sci_mcpのパッケージ骨格を作成する
- pyproject.tomlまたは同等のPythonプロジェクト定義を追加する
- FastMCPとPydanticを基盤依存として定義する
- Phase 1のadapter雛形とdiscoveryツールを同時に作成する