# Microsoft AI for Science ツール — MCP連携 優先順位リスト

> **作成日**: 2026-04-01  
> **ソース**: `references/ms-ai4science-tools.md`, `ms-ai4science-tools-2.md`, `references/MCP_AI4Science.md`  
> **目的**: orbital-sci-mcp プロジェクトにおいて、MCP (Model Context Protocol) サーバーとして連携すべき Microsoft AI for Science ツールを優先度順にリスト化する

---

## 評価基準

各ツールを以下の5軸で評価し、総合スコアで優先順位を決定した。

| 基準 | 重み | 説明 |
|------|------|------|
| **API適性** | ★★★ | Python API / CLI が明確で、MCP tool としてラップしやすいか |
| **科学的インパクト** | ★★★ | 利用者数・引用数・分野での重要性 |
| **MCP空白領域** | ★★★ | 既存 MCP エコシステムで未カバーの機能を提供するか |
| **パイプライン統合性** | ★★ | 他ツールとの連携でワークフローを構成できるか |
| **実装難易度（逆）** | ★ | 低い方が高スコア（すぐ実装できる） |

---

## 優先順位リスト

### ═══════════════════════════════════════
### Tier 1: 最優先（即時実装推奨）
### ═══════════════════════════════════════

---

#### 1️⃣ MatterSim — 材料シミュレーション基盤モデル

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/mattersim |
| **⭐** | 524 |
| **分野** | 材料科学・計算化学 |
| **MCP連携理由** | **材料科学MCP空白を埋める最重要ツール**。既存MCP（Materials Project MCP, OPTIMADE MCP）はデータベース検索のみ。MatterSim MCPはシミュレーション実行（エネルギー・力・応力・フォノン予測、構造緩和、MD実行）を提供し、検索→シミュレーションのワークフローを完成させる |
| **API適性** | ASE Calculator インターフェース。`MatterSimCalculator` をPythonから直接呼び出し可能。入出力がAtoms→{energy, forces, stress} と明確 |
| **MCP tool候補** | `mattersim_predict_energy`, `mattersim_relax_structure`, `mattersim_run_md`, `mattersim_predict_phonons`, `mattersim_bulk_properties` |
| **総合スコア** | **95/100** |

---

#### 2️⃣ MatterGen — 材料生成AIモデル

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/mattergen |
| **⭐** | 1,657 |
| **分野** | 材料科学（生成AI） |
| **MCP連携理由** | 既存MCP空白。制約条件付き材料生成はどのMCPサーバーにも存在しない。MatterSim MCPと組み合わせて「生成→評価」パイプラインを構築可能 |
| **API適性** | Python API。化学組成・体積弾性率・磁気密度等の制約を入力→CIF構造を出力。明確なI/O |
| **MCP tool候補** | `mattergen_generate_material`, `mattergen_generate_with_constraints`, `mattergen_sample_candidates`, `mattergen_evaluate_stability` |
| **総合スコア** | **93/100** |

---

#### 3️⃣ MACE / MACE-MP-0 — 汎用機械学習原子間ポテンシャル

| 項目 | 内容 |
|------|------|
| **GitHub（本体）** | https://github.com/ACEsuit/mace |
| **GitHub（基盤モデル）** | https://github.com/ACEsuit/mace-foundations |
| **分野** | 原子間ポテンシャル・分子シミュレーション |
| **MCP連携理由** | MatterSimと相補的だが、89元素対応の汎用基盤モデル（MACE-MP-0）は即座にゼロショット予測可能。研究者が最もカスタマイズする力場ツールであり、MCP化の需要が高い。`pip install mace-torch` で導入、ASE統合済み |
| **API適性** | `mace_mp()` で事前学習モデルを即時ロード。ASE Calculator として標準的に利用可能。MatterSimと同じインターフェース構造 |
| **MCP tool候補** | `mace_predict_energy`, `mace_optimize_geometry`, `mace_run_md`, `mace_calculate_forces`, `mace_finetune` |
| **総合スコア** | **91/100** |

---

#### 4️⃣ Graphormer / DiG — 分子モデリング & 平衡分布予測

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/Graphormer |
| **⭐** | 2,435 |
| **分野** | 分子モデリング・計算化学 |
| **MCP連携理由** | MS AI4Science最多スターのフラッグシップ。分子特性予測（Graphormer）と平衡分布予測（DiG）の2機能を持つ。既存MCP空白：分子のコンフォメーションアンサンブル生成はどのMCPにも存在しない |
| **API適性** | Python API。SMILES / 座標入力→予測値出力。DiGは配列→コンフォメーション分布 |
| **MCP tool候補** | `graphormer_predict_property`, `dig_sample_conformations`, `dig_predict_equilibrium`, `graphormer_embed_molecule` |
| **総合スコア** | **90/100** |

---

#### 5️⃣ BioEmu — タンパク質構造アンサンブル予測

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/bioemu |
| **⭐** | 782 |
| **ベンチマーク** | https://github.com/microsoft/bioemu-benchmarks |
| **分野** | 構造生物学・タンパク質科学 |
| **MCP連携理由** | 既存MCP（AlphaFold MCP, PDB MCP）は「1つの予測構造」の取得のみ。BioEmu MCPは「平衡アンサンブル全体」を生成し、タンパク質ダイナミクスの新パラダイムを提供。Science掲載のインパクト。創薬ワークフロー（クリプティックポケット発見、ドメイン運動解析）に直結 |
| **API適性** | アミノ酸配列入力→PDB構造アンサンブル出力。明確なI/O。GPU必要だが推論API化可能 |
| **MCP tool候補** | `bioemu_sample_ensemble`, `bioemu_predict_dynamics`, `bioemu_find_cryptic_pockets`, `bioemu_domain_motion` |
| **総合スコア** | **89/100** |

---

### ═══════════════════════════════════════
### Tier 2: 高優先（次フェーズ実装）
### ═══════════════════════════════════════

---

#### 6️⃣ RetroChimera — 逆合成予測

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/retrochimera |
| **⭐** | 23 |
| **分野** | 合成化学・創薬 |
| **MCP連携理由** | 分子設計→合成ルート計画のパイプラインで不可欠。既存MCP（RDKit MCP, ChEMBL MCP）は化合物検索・記述子計算にとどまり、合成計画機能は存在しない。TamGen/MoLeRで生成した分子の「作り方」を回答できる |
| **API適性** | SMILES入力→反応経路出力（reactants SMILES + 反応条件）。Azure AI Foundry にもモデルカタログ掲載済み |
| **MCP tool候補** | `retro_predict_single_step`, `retro_plan_multistep`, `retro_evaluate_route`, `retro_suggest_alternatives` |
| **総合スコア** | **86/100** |

---

#### 7️⃣ TamGen — ターゲット認識型分子生成

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/TamGen |
| **⭐** | 41 |
| **分野** | 創薬・分子生成 |
| **MCP連携理由** | タンパク質3D構造を入力→結合分子を生成という明確なユースケース。PDB MCP/AlphaFold MCPで構造取得→TamGenで分子設計→RetroChimeraで合成ルート計画、という創薬フルパイプラインが構築可能 |
| **API適性** | PDB構造 + 結合ポケット情報入力→SMILES分子出力。Nature Communications掲載の実績 |
| **MCP tool候補** | `tamgen_generate_molecules`, `tamgen_refine_compound`, `tamgen_dock_evaluate`, `tamgen_batch_generate` |
| **総合スコア** | **85/100** |

---

#### 8️⃣ EvoDiff — タンパク質配列設計

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/evodiff |
| **⭐** | 665 |
| **分野** | タンパク質工学・合成生物学 |
| **MCP連携理由** | 構造ベースでは到達困難な天然変性タンパク質や新規スキャフォールドの配列設計。既存MCP（UniProt, PDB）は検索のみで生成機能なし。BioEmuと組み合わせて「配列設計→動態予測」ワークフロー構築可能 |
| **API適性** | 無条件 / モチーフ条件付き生成。配列文字列→配列文字列のI/O |
| **MCP tool候補** | `evodiff_generate_sequence`, `evodiff_scaffold_motif`, `evodiff_generate_idr`, `evodiff_conditional_generate` |
| **総合スコア** | **84/100** |

---

#### 9️⃣ Skala — ニューラルネットワーク交換相関汎関数

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/skala |
| **⭐** | 195 |
| **分野** | 量子化学・DFT |
| **MCP連携理由** | 既存 GPAW MCP / Accelerated DFT は汎用DFT実行。Skalaは「化学精度のDFTをメタGGAコストで」という独自価値。MatterSimで粗いスクリーニング→Skalaで高精度検証のワークフロー |
| **API適性** | `pip install microsoft-skala`、PySCF統合。`xc="skala"` の1行で既存DFTワークフローに組み込める |
| **MCP tool候補** | `skala_single_point_energy`, `skala_optimize_geometry`, `skala_reaction_energy`, `skala_benchmark_functional` |
| **総合スコア** | **82/100** |

---

#### 🔟 MoLeR — スキャフォールド制約付き分子生成

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/molecule-generation |
| **⭐** | 323 |
| **分野** | 創薬・分子設計 |
| **MCP連携理由** | 既知スキャフォールドを保持した分子最適化はRDKit MCPでは不可能。ChEMBL MCPでヒット化合物を見つけ→MoLeRで誘導体設計、というメディシナルケミストリーワークフロー |
| **API適性** | SMILES（スキャフォールド）入力→SMILES（新規分子群）出力 |
| **MCP tool候補** | `moler_generate_from_scaffold`, `moler_optimize_molecule`, `moler_sample_diverse`, `moler_score_candidates` |
| **総合スコア** | **80/100** |

---

### ═══════════════════════════════════════
### Tier 3: 中優先（機能拡充フェーズ）
### ═══════════════════════════════════════

---

#### 1️⃣1️⃣ Aurora — 地球システム予測基盤モデル

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/aurora |
| **⭐** | 861 |
| **分野** | 気象・気候・大気科学 |
| **MCP連携理由** | 既存ClimaXとの差別化は高解像度気象予報・大気汚染・海洋波。ただしGPU/メモリ要件が高く、MCP toolとしてはリモート推論API経由が現実的 |
| **MCP tool候補** | `aurora_forecast_weather`, `aurora_predict_pollution`, `aurora_ocean_waves` |
| **総合スコア** | **75/100** |

---

#### 1️⃣2️⃣ ClimaX — 気象・気候基盤モデル

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/ClimaX |
| **⭐** | 687 |
| **分野** | 気象・気候 |
| **MCP連携理由** | 異種データセット吸収能力が強み。ファインチューニング済みモデルで下流タスク対応。Auroraより軽量で実装しやすい |
| **MCP tool候補** | `climax_forecast`, `climax_downscale`, `climax_climate_projection` |
| **総合スコア** | **73/100** |

---

#### 1️⃣3️⃣ AI2BMD — AI駆動ab initio生体分子動力学

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/AI2BMD |
| **分野** | 生体分子動力学 |
| **MCP連携理由** | ViSNet + Geoformer によるab initio精度の生体分子MDシミュレーション。BioEmuが「平衡分布」ならAI2BMDは「動力学軌跡」を提供 |
| **MCP tool候補** | `ai2bmd_run_simulation`, `ai2bmd_analyze_trajectory` |
| **総合スコア** | **72/100** |

---

#### 1️⃣4️⃣ NatureLM / SFM — マルチドメイン科学基盤モデル

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/SFM |
| **分野** | 小分子・タンパク質・DNA・RNA・材料（横断） |
| **MCP連携理由** | テキスト指示で分子生成・最適化。1B〜46.7Bの3サイズ。万能型だが個別ツールの精度には劣る可能性。MCP経由で「自然言語→科学エンティティ生成」を実現する統合tool候補 |
| **MCP tool候補** | `naturelm_generate_entity`, `naturelm_optimize`, `naturelm_predict_property` |
| **総合スコア** | **70/100** |

---

#### 1️⃣5️⃣ Dayhoff — 大規模タンパク質言語モデル

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/dayhoff |
| **分野** | タンパク質科学 |
| **MCP連携理由** | 33.4億配列で訓練。ゼロショット変異効果予測はEvoDiffと相補。既存タンパク質MCP（UniProt, PDB）はDB検索だがDayhoffは予測機能を追加 |
| **MCP tool候補** | `dayhoff_predict_mutation_effect`, `dayhoff_generate_protein`, `dayhoff_embed_sequence` |
| **総合スコア** | **68/100** |

---

#### 1️⃣6️⃣ FarmVibes.AI — 農業・地理空間ML

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/farmvibes-ai |
| **⭐** | 845 |
| **分野** | 農業・サステナビリティ |
| **MCP連携理由** | TorchGeo / Planetary Computer MCPとは差別化される農業特化機能（SpaceEye雲除去、DeepMC微気候予測、土壌炭素推定）。ただしKubernetesベースの重いワークフローのためMCP化の難易度は高い |
| **MCP tool候補** | `farmvibes_crop_segmentation`, `farmvibes_soil_carbon`, `farmvibes_microclimate` |
| **総合スコア** | **65/100** |

---

### ═══════════════════════════════════════
### Tier 4: 低優先（条件付き実装）
### ═══════════════════════════════════════

---

#### 1️⃣7️⃣ FoldingDiff / FrameFlow — タンパク質バックボーン生成

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/foldingdiff / https://github.com/microsoft/protein-frame-flow |
| **分野** | タンパク質構造設計 |
| **MCP連携理由** | EvoDiff（配列空間）の構造空間版。SE(3)フローマッチング。ただしEvoDiff + BioEmuで多くのユースケースをカバー済み |
| **総合スコア** | **58/100** |

---

#### 1️⃣8️⃣ Accelerated DFT — GPU加速DFT

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/accelerated-dft |
| **分野** | 量子化学 |
| **MCP連携理由** | PySCF比20倍高速。ただし既存 GPAW MCP と機能重複。Skala MCPがあれば多くのケースで代替可能 |
| **総合スコア** | **55/100** |

---

#### 1️⃣9️⃣ DVMP — 二重ビュー分子事前学習

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/DVMP |
| **分野** | 分子特性予測 |
| **MCP連携理由** | Graphormerと機能重複。特性予測はGraphormer MCPで十分カバー可能 |
| **総合スコア** | **45/100** |

---

#### 2️⃣0️⃣ BioGPT — バイオメディカルテキスト生成

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/microsoft/BioGPT |
| **分野** | バイオメディカルNLP |
| **MCP連携理由** | 文献検索MCPは既に20+存在（paper-search-mcp, BioMCP等）。BioGPTの生成・QA機能は汎用LLMで代替可能な場合が多い |
| **総合スコア** | **40/100** |

---

#### ベンチマーク・データセット系（MCP連携不要）

以下はベンチマーク・評価ツールのため、MCP tool化の対象外:

| ツール | GitHub | 理由 |
|--------|--------|------|
| bioemu-benchmarks | https://github.com/microsoft/bioemu-benchmarks | BioEmu評価用 |
| WeatherReal-Benchmark | https://github.com/microsoft/WeatherReal-Benchmark | 気象モデル評価用 |
| protein-uq | https://github.com/microsoft/protein-uq | UQベンチマーク |
| Chemistry-QA | https://github.com/microsoft/chemistry-qa | 化学QAベンチマーク |
| LLM4ScientificDiscovery | https://github.com/microsoft/LLM4ScientificDiscovery | 評価研究 |

---

## MCP連携ワークフロー設計

### 材料発見パイプライン

```
[Materials Project MCP]  ──検索──▶  候補結晶構造
         │
         ▼
[MatterGen MCP]  ──生成──▶  新規材料候補
         │
         ▼
[MatterSim MCP / MACE MCP]  ──シミュレーション──▶  エネルギー・安定性評価
         │
         ▼
[Skala MCP]  ──高精度DFT──▶  電子構造検証
         │
         ▼
[RetroChimera MCP]  ──合成計画──▶  合成経路提案
```

### 創薬パイプライン

```
[UniProt MCP / PDB MCP]  ──ターゲット取得──▶  タンパク質構造
         │
         ├──▶ [BioEmu MCP]  ──動態予測──▶  構造アンサンブル（クリプティックポケット発見）
         │
         ▼
[TamGen MCP]  ──分子生成──▶  候補化合物群
         │
         ├──▶ [MoLeR MCP]  ──最適化──▶  スキャフォールド保持の誘導体
         │
         ▼
[ChEMBL MCP / RDKit MCP]  ──評価──▶  ADMET・薬物様性スコア
         │
         ▼
[RetroChimera MCP]  ──合成計画──▶  合成経路提案
```

### タンパク質設計パイプライン

```
[EvoDiff MCP]  ──配列生成──▶  新規タンパク質配列
         │
         ▼
[Dayhoff MCP]  ──変異予測──▶  変異効果スコア
         │
         ▼
[BioEmu MCP]  ──アンサンブル──▶  構造分布予測
         │
         ▼
[AI2BMD MCP]  ──MD──▶  動力学軌跡
```

---

## 実装ロードマップ提案

### Phase 1（即時）: 材料科学コア + タンパク質コア

| # | ツール | 推定工数 | 備考 |
|---|--------|---------|------|
| 1 | MatterSim MCP | 中 | ASE Calculator ラッパー |
| 2 | MatterGen MCP | 中 | 生成API ラッパー |
| 3 | MACE MCP | 中 | ASE Calculator ラッパー（MatterSimと共通設計） |
| 4 | BioEmu MCP | 中〜高 | GPU推論必要 |
| 5 | Graphormer/DiG MCP | 中 | 分子特性予測 + アンサンブル |

### Phase 2（次期）: 創薬パイプライン

| # | ツール | 推定工数 | 備考 |
|---|--------|---------|------|
| 6 | RetroChimera MCP | 低〜中 | SMILES→反応経路 |
| 7 | TamGen MCP | 中 | 構造→分子生成 |
| 8 | EvoDiff MCP | 中 | 配列生成 |
| 9 | Skala MCP | 低 | PySCF統合、1行追加 |
| 10 | MoLeR MCP | 中 | スキャフォールド制約生成 |

### Phase 3（拡充）: 地球科学 + 横断

| # | ツール | 推定工数 | 備考 |
|---|--------|---------|------|
| 11 | Aurora MCP | 高 | GPU/メモリ要件大、リモート推論推奨 |
| 12 | ClimaX MCP | 中 | Auroraより軽量 |
| 13 | AI2BMD MCP | 中〜高 | ab initio MD |
| 14 | NatureLM MCP | 高 | 大規模モデル |
| 15 | Dayhoff MCP | 中 | タンパク質LM |
| 16 | FarmVibes.AI MCP | 高 | Kubernetesワークフロー |

---

## 全ツール優先順位サマリー

| 順位 | ツール名 | GitHub | スコア | Tier | 分野 |
|------|----------|--------|--------|------|------|
| 1 | **MatterSim** | [microsoft/mattersim](https://github.com/microsoft/mattersim) | 95 | Tier 1 | 材料科学 |
| 2 | **MatterGen** | [microsoft/mattergen](https://github.com/microsoft/mattergen) | 93 | Tier 1 | 材料科学 |
| 3 | **MACE** | [ACEsuit/mace](https://github.com/ACEsuit/mace) | 91 | Tier 1 | 原子間ポテンシャル |
| 4 | **Graphormer/DiG** | [microsoft/Graphormer](https://github.com/microsoft/Graphormer) | 90 | Tier 1 | 分子モデリング |
| 5 | **BioEmu** | [microsoft/bioemu](https://github.com/microsoft/bioemu) | 89 | Tier 1 | タンパク質科学 |
| 6 | **RetroChimera** | [microsoft/retrochimera](https://github.com/microsoft/retrochimera) | 86 | Tier 2 | 合成化学 |
| 7 | **TamGen** | [microsoft/TamGen](https://github.com/microsoft/TamGen) | 85 | Tier 2 | 創薬 |
| 8 | **EvoDiff** | [microsoft/evodiff](https://github.com/microsoft/evodiff) | 84 | Tier 2 | タンパク質設計 |
| 9 | **Skala** | [microsoft/skala](https://github.com/microsoft/skala) | 82 | Tier 2 | 量子化学 |
| 10 | **MoLeR** | [microsoft/molecule-generation](https://github.com/microsoft/molecule-generation) | 80 | Tier 2 | 分子設計 |
| 11 | **Aurora** | [microsoft/aurora](https://github.com/microsoft/aurora) | 75 | Tier 3 | 気象・気候 |
| 12 | **ClimaX** | [microsoft/ClimaX](https://github.com/microsoft/ClimaX) | 73 | Tier 3 | 気象・気候 |
| 13 | **AI2BMD** | [microsoft/AI2BMD](https://github.com/microsoft/AI2BMD) | 72 | Tier 3 | 生体分子MD |
| 14 | **NatureLM/SFM** | [microsoft/SFM](https://github.com/microsoft/SFM) | 70 | Tier 3 | 横断科学 |
| 15 | **Dayhoff** | [microsoft/dayhoff](https://github.com/microsoft/dayhoff) | 68 | Tier 3 | タンパク質LM |
| 16 | **FarmVibes.AI** | [microsoft/farmvibes-ai](https://github.com/microsoft/farmvibes-ai) | 65 | Tier 3 | 農業 |
| 17 | **FoldingDiff/FrameFlow** | [microsoft/foldingdiff](https://github.com/microsoft/foldingdiff) | 58 | Tier 4 | タンパク質構造 |
| 18 | **Accelerated DFT** | [microsoft/accelerated-dft](https://github.com/microsoft/accelerated-dft) | 55 | Tier 4 | DFT |
| 19 | **DVMP** | [microsoft/DVMP](https://github.com/microsoft/DVMP) | 45 | Tier 4 | 分子予測 |
| 20 | **BioGPT** | [microsoft/BioGPT](https://github.com/microsoft/BioGPT) | 40 | Tier 4 | バイオNLP |

---

## 既存MCPエコシステムとの接続マップ

| 既存MCP | → 新規MS AI4Sci MCP | 接続パターン |
|---------|---------------------|-------------|
| Materials Project MCP | → MatterSim / MACE MCP | DB検索結果→シミュレーション入力 |
| OPTIMADE MCP | → MatterSim / MatterGen MCP | 結晶構造→評価/生成 |
| PDB MCP / AlphaFold MCP | → BioEmu / TamGen MCP | 構造取得→アンサンブル/分子生成 |
| UniProt MCP | → EvoDiff / Dayhoff MCP | 配列取得→配列設計/変異予測 |
| ChEMBL MCP / PubChem MCP | → MoLeR / RetroChimera MCP | ヒット化合物→最適化/合成ルート |
| RDKit MCP | → TamGen / MoLeR MCP | 記述子計算→分子生成入力 |
| GPAW MCP | → Skala MCP | 汎用DFT→高精度DFT |
| Jupyter MCP | → 全ツール | 結果解析・可視化 |
