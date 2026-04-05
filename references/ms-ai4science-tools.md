# Microsoft AI for Science ツール総合カタログ

> **調査日**: 2026-04-01  
> **調査手法**: MACE (Multi-Atomic Cluster Expansion) を起点とし、Microsoft Research AI for Science が開発・共同開発したツール群を網羅的にリストアップ  
> **対象範囲**: GitHub公開リポジトリ、Azure AI Foundry モデルカタログ、Microsoft Research 公式ページ、学術論文

---

## 目次

1. [概要 — Microsoft Research AI for Science](#1-概要)
2. [MACE および関連基盤モデル（原子間ポテンシャル）](#2-mace-および関連基盤モデル)
3. [材料科学・計算化学](#3-材料科学計算化学)
4. [創薬・低分子設計](#4-創薬低分子設計)
5. [タンパク質・生体分子](#5-タンパク質生体分子)
6. [気象・気候・地球科学](#6-気象気候地球科学)
7. [農業・サステナビリティ](#7-農業サステナビリティ)
8. [統合プラットフォーム](#8-統合プラットフォーム)
9. [MACEとMicrosoft AI4Scienceの関係](#9-maceとmicrosoft-ai4scienceの関係)
10. [サマリーテーブル](#10-サマリーテーブル)

---

## 1. 概要

Microsoft Research AI for Science は、AI を活用して化学、材料科学、生物学、気象学、農業などの自然科学分野における発見を加速することを目指す研究ラボである。「第5のパラダイム」として位置づけられ、深層学習モデルを大規模に展開し、実験やシミュレーションを桁違いの速度で実行可能にする[^1]。

Azure AI Foundry、Azure Quantum Elements といったクラウドプラットフォームと連携し、オープンソースとして公開されたモデルの多くは研究者が直接利用可能である[^2]。

---

## 2. MACE および関連基盤モデル

### 2.1 MACE (Multi-Atomic Cluster Expansion)

| 項目 | 内容 |
|------|------|
| **開発元** | ACEsuit (Cambridge大学 — Ilyes Batatia, Dávid Péter Kovács, Gábor Csányi ら) + Microsoft Research 共同 |
| **GitHub** | [ACEsuit/mace](https://github.com/ACEsuit/mace) |
| **論文** | NeurIPS 2022: "MACE: Higher Order Equivariant Message Passing Neural Networks for Fast and Accurate Force Fields" (arXiv:2206.07697)[^3] |
| **概要** | E(3)-等変メッセージパッシングニューラルネットワークによる機械学習原子間ポテンシャル。高次（4体）メッセージにより1-2回のメッセージパッシングで高精度を達成 |
| **特徴** | PyTorch / JAX バックエンド、ASE統合、データ効率性が高い |

**Microsoft Research との関係**: MACEの原論文は Microsoft Research 公式ページにも掲載されており[^4]、著者の一部（Batatia, Kovács）は Microsoft Research のアフィリエーションを持つ。

### 2.2 MACE-MP-0 (Foundation Model)

| 項目 | 内容 |
|------|------|
| **GitHub** | [ACEsuit/mace-foundations](https://github.com/ACEsuit/mace-foundations) |
| **論文** | "A foundation model for atomistic materials chemistry" (arXiv:2401.00096)[^5] |
| **概要** | Materials Project の MPTrj データセット（160万構造）で訓練された汎用基盤モデル。89元素をカバー |
| **モデルサイズ** | Small / Medium / Large の3段階 |
| **使用法** | `from mace.calculators import mace_mp` でASE計算器として即座に利用可能 |

### 2.3 MACE の位置づけ

MACEは Microsoft が直接開発したツールではないが、Microsoft Research が共同研究・論文共著・公式掲載しており、MatterSim などの Microsoftツールと相補的な関係にある。MACEが汎用的・カスタマイズ可能な力場を提供し、MatterSimはスケーラブルなシミュレーション基盤を提供する。

---

## 3. 材料科学・計算化学

### 3.1 MatterSim

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research AI for Science |
| **GitHub** | [microsoft/mattersim](https://github.com/microsoft/mattersim) ⭐524 |
| **論文** | arXiv:2405.04967[^6] |
| **概要** | 深層学習に基づく原子スケールモデル。全元素・温度5000K・圧力1000GPaまで対応 |
| **機能** | エネルギー・力・応力・フォノンの予測、分子動力学シミュレーション |
| **提供形態** | オープンソース + Azure AI Foundry カタログ |
| **ファインチューニング** | カスタムデータセットでの再訓練をサポート |

### 3.2 MatterGen

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research AI for Science |
| **GitHub** | [microsoft/mattergen](https://github.com/microsoft/mattergen) ⭐1,657 |
| **概要** | 無機材料の生成AIモデル（拡散モデル）。周期表全体にわたる安定な新材料を設計 |
| **特徴** | 体積弾性率・磁気密度・化学組成など特性制約付き生成、ファインチューニング対応 |
| **応用** | バッテリー材料、触媒、サステナブル材料の発見 |

### 3.3 Skala

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research AI for Science |
| **GitHub** | [microsoft/skala](https://github.com/microsoft/skala) ⭐195 |
| **論文** | arXiv:2506.14665[^7] |
| **概要** | ニューラルネットワークベースの交換相関汎関数（DFT用）。ハイブリッド汎関数レベルの精度をメタGGAの計算コストで実現 |
| **特徴** | ~276,000パラメータ、PySCF統合、GPU加速対応、`pip install microsoft-skala` で利用可能 |
| **精度** | W4-17 MAE: 1.06 kcal/mol、GMTKN55 WTMAD-2: ~3.89 kcal/mol |

### 3.4 Graphormer

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research AI for Science |
| **GitHub** | [microsoft/Graphormer](https://github.com/microsoft/Graphormer) ⭐2,435 |
| **概要** | 分子モデリング用の汎用深層学習バックボーン。Transformer アーキテクチャを分子グラフに適用 |
| **特徴** | KDD Cup 2021 優勝、OGB-LSCベンチマーク上位 |
| **サブプロジェクト** | Distributional Graphormer (DiG) を含む |

### 3.5 Distributional Graphormer (DiG)

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research AI for Science |
| **GitHub** | [microsoft/Graphormer/distributional_graphormer](https://github.com/microsoft/Graphormer/tree/main/distributional_graphormer) |
| **論文** | Nature Machine Intelligence (2024)[^8] |
| **概要** | 分子系の平衡分布を予測する深層学習フレームワーク。単一構造ではなくコンフォメーションアンサンブルを生成 |
| **応用** | タンパク質コンフォメーションサンプリング、リガンド結合、触媒-吸着系 |
| **特徴** | 分子動力学に比べ桁違いに高速 |

---

## 4. 創薬・低分子設計

### 4.1 TamGen

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research AI for Science + GHDDI |
| **GitHub** | [microsoft/TamGen](https://github.com/microsoft/TamGen) ⭐41 |
| **論文** | Nature Communications (2024)[^9] |
| **概要** | ターゲット認識型分子生成ツール。タンパク質構造情報を取り込み、結合親和性の高い新規分子をGPT風の化学言語モデルで生成 |
| **実績** | 結核プロテアーゼに対する阻害剤候補を同定（IC₅₀ 1.9 μM） |
| **提供形態** | Azure AI Foundry Labs でも利用可能 |

### 4.2 RetroChimera

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research AI for Science |
| **GitHub** | [microsoft/retrochimera](https://github.com/microsoft/retrochimera) ⭐23 |
| **論文** | arXiv:2412.05269[^10] |
| **概要** | 逆合成予測AIモデル。テンプレートベース（GNN）とテンプレートフリー（Transformer）を学習ベースのアンサンブルで統合 |
| **特徴** | 単段・多段合成ルート計画、化学者ブラインド評価で既存データセット超え |
| **提供形態** | Azure AI Foundry カタログ + GitHub |

### 4.3 MoLeR (Molecule Generation)

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research |
| **GitHub** | [microsoft/molecule-generation](https://github.com/microsoft/molecule-generation) ⭐323 |
| **論文** | "Learning to Extend Molecular Scaffolds with Structural Motifs" (arXiv:2103.03864)[^11] |
| **概要** | スキャフォールド制約付き分子生成モデル（VAE + GNN）。既知の分子骨格を保持しつつ化学空間を探索 |
| **特徴** | HierVAE等に比べ訓練・生成が高速 |
| **応用** | 創薬、ポリマー設計 |

---

## 5. タンパク質・生体分子

### 5.1 BioEmu

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research AI for Science |
| **GitHub** | [microsoft/bioemu](https://github.com/microsoft/bioemu) ⭐782 |
| **ベンチマーク** | [microsoft/bioemu-benchmarks](https://github.com/microsoft/bioemu-benchmarks) ⭐57 |
| **概要** | タンパク質平衡アンサンブルの生成的深層学習エミュレーション。スケーラブルに生体分子コンフォメーション分布を予測 |
| **応用** | タンパク質構造・機能研究、創薬（結合柔軟性解析） |

### 5.2 EvoDiff

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research |
| **GitHub** | [microsoft/evodiff](https://github.com/microsoft/evodiff) ⭐665 |
| **概要** | タンパク質配列の進化的拡散モデル。3D構造情報なしに配列のみから新規タンパク質を生成 |
| **特徴** | UniRef50 で訓練、条件付き生成（モチーフスキャフォールディング、天然変性領域）に対応 |
| **意義** | 構造ベースではアクセスできない配列空間を探索可能にする「配列ファースト」パラダイム |
| **実験検証** | Adaptyv Bio によるウェットラボ検証で発現・折りたたみ・機能が確認[^12] |

### 5.3 protein-uq

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research |
| **GitHub** | [microsoft/protein-uq](https://github.com/microsoft/protein-uq) ⭐21 |
| **概要** | タンパク質に対する不確実性定量化手法のベンチマーク |
| **対象タスク** | フィットネス予測、機能予測、能動学習 |

---

## 6. 気象・気候・地球科学

### 6.1 Aurora

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research AI for Science |
| **GitHub** | [microsoft/aurora](https://github.com/microsoft/aurora) ⭐861 |
| **概要** | 地球システム予測のための基盤モデル。大気・気候・海洋波・大気化学に対応 |
| **特徴** | 高解像度気象予報、大気汚染予測、熱帯低気圧追跡 |
| **提供形態** | Azure AI Foundry 経由で利用可能（2025年1月～） |

### 6.2 ClimaX

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research |
| **GitHub** | [microsoft/ClimaX](https://github.com/microsoft/ClimaX) ⭐687 |
| **論文** | "ClimaX: A foundation model for weather and climate" (arXiv:2301.10343)[^13] |
| **概要** | 気象・気候のための最初の大規模基盤モデル。CMIP6 等の異種データで事前学習し、下流タスクにファインチューニング |
| **特徴** | Transformer ベース、マルチ変数・マルチ解像度対応 |

### 6.3 ADAF (AI Data Assimilation Framework)

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research |
| **GitHub** | [microsoft/ADAF](https://github.com/microsoft/ADAF) ⭐12 |
| **論文** | arXiv:2411.16807[^14] |
| **概要** | AIによるデータ同化フレームワーク。異種観測データ（地上気象、衛星）をキロメートルスケールで統合 |
| **性能** | HRRRDAS 比 16-33% 精度向上、GPUで数秒/同化サイクル |
| **応用** | 極端気象の再構築（例：熱帯低気圧風場） |

### 6.4 WeatherReal-Benchmark

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research |
| **GitHub** | [microsoft/WeatherReal-Benchmark](https://github.com/microsoft/WeatherReal-Benchmark) ⭐43 |
| **概要** | 気象予報検証のためのベンチマークデータセット・評価パイプライン |
| **特徴** | 地上気象観測データの集約・正規化 |

### 6.5 SolarSeer

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research |
| **GitHub** | [microsoft/SolarSeer](https://github.com/microsoft/SolarSeer) ⭐13 |
| **概要** | 24時間先の太陽放射照度を超高速・高精度に予測。数値気象予報を凌駕する性能 |
| **応用** | ソーラーエネルギー予測、電力グリッド管理 |

---

## 7. 農業・サステナビリティ

### 7.1 FarmVibes.AI

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft Research |
| **GitHub** | [microsoft/farmvibes-ai](https://github.com/microsoft/farmvibes-ai) ⭐845 |
| **概要** | 農業・サステナビリティ向けのマルチモーダル地理空間MLモデル群 |
| **データソース** | 衛星画像、ドローン、センサー、気象データなどのフュージョン |
| **応用** | 作物モニタリング、成長率推定、環境モデリング |

---

## 8. 統合プラットフォーム

### 8.1 Microsoft Discovery

| 項目 | 内容 |
|------|------|
| **発表** | Microsoft Build 2025 |
| **概要** | エージェント型AI駆動の科学R&Dプラットフォーム。文献レビュー、仮説生成、シミュレーション、実験設計をAIエージェントチームで自動化 |
| **コア技術** | グラフベース知識エンジン、Copilot-Discovery（科学AIアシスタント） |
| **基盤** | Azure HPC + Azure AI Foundry |
| **実績** | データセンター冷却材の新規候補を367,000化合物から200時間で発見 |
| **パートナー** | GSK、Estée Lauder、Synopsys、NVIDIA 等 |
| **URL** | [公式ブログ](https://azure.microsoft.com/en-us/blog/transforming-rd-with-agentic-ai-introducing-microsoft-discovery/)[^15] |

### 8.2 Azure Quantum Elements

| 項目 | 内容 |
|------|------|
| **概要** | 量子化学・材料シミュレーションのためのクラウドプラットフォーム |
| **主要機能** | |
| — Generative Chemistry | AI駆動の分子設計・合成経路計画・特性予測 |
| — Accelerated DFT | AI+HPC による高速電子構造計算 |
| — Copilot for Quantum | 自然言語インターフェースでの科学ワークフロー制御 |
| — MatterSim 統合 | Foundation Model による材料シミュレーション |
| — レガシーコード統合 | NWChem, NWChemEx, FLOSIC, ExaChem のクラウドネイティブ実行 |
| **URL** | [Azure Quantum Elements](https://azure.microsoft.com/en-us/products/quantum/elements/)[^16] |

### 8.3 Azure AI Foundry (AI for Science モデルカタログ)

Azure AI Foundry で利用可能な AI for Science モデル一覧:

| モデル名 | 分野 |
|----------|------|
| MatterSim | 材料シミュレーション |
| MatterGen | 材料生成 |
| Aurora | 気象・気候 |
| Skala | 量子化学 (DFT) |
| RetroChimera | 逆合成予測 |
| TamGen | 創薬・分子生成 |
| EvoDiff | タンパク質配列生成 |
| BioEmu | 生体分子アンサンブル |

---

## 9. MACEとMicrosoft AI4Scienceの関係

### 共同研究・共著関係

MACEは Cambridge大学の ACEsuit グループ（Gábor Csányi ラボ）が主導して開発しているが、Microsoft Research との協力関係は深い:

1. **論文共著**: MACE の NeurIPS 2022 論文は Microsoft Research のアフィリエーションを持つ著者を含み、Microsoft Research 公式ページにも掲載されている[^4]
2. **MACE-MP-0 基盤モデル**: Materials Project データで訓練されたユニバーサルモデルは、Microsoft AI for Science のエコシステムと相補的に機能する[^5]
3. **技術的相補性**:
   - MACE: カスタマイズ可能な汎用 ML 原子間ポテンシャル（研究者がファインチューニングに活用）
   - MatterSim: Microsoft のスケーラブルなシミュレーション基盤（クラウド統合、プロダクション利用向き）

### ワークフローにおける位置づけ

```
材料候補生成 (MatterGen)
        ↓
特性シミュレーション (MatterSim / MACE)
        ↓
量子化学検証 (Skala / Accelerated DFT)
        ↓
合成経路計画 (RetroChimera)
```

MACEは上記ワークフローの「特性シミュレーション」段階で、MatterSim と並行して利用できる柔軟なオプションを提供する。

---

## 10. サマリーテーブル

| カテゴリ | ツール名 | リポジトリ | ⭐ | 概要 |
|----------|----------|------------|-----|------|
| **原子間ポテンシャル** | MACE | [ACEsuit/mace](https://github.com/ACEsuit/mace) | — | 等変MPNN力場（MS Research共同） |
| | MACE-MP-0 | [ACEsuit/mace-foundations](https://github.com/ACEsuit/mace-foundations) | — | 89元素対応ユニバーサルモデル |
| **材料科学** | MatterSim | [microsoft/mattersim](https://github.com/microsoft/mattersim) | 524 | 深層学習原子シミュレーション |
| | MatterGen | [microsoft/mattergen](https://github.com/microsoft/mattergen) | 1,657 | 無機材料生成AIモデル |
| | Skala | [microsoft/skala](https://github.com/microsoft/skala) | 195 | NN交換相関汎関数 (DFT) |
| | Graphormer | [microsoft/Graphormer](https://github.com/microsoft/Graphormer) | 2,435 | 分子モデリングバックボーン |
| | DiG | [Graphormer/distributional_graphormer](https://github.com/microsoft/Graphormer/tree/main/distributional_graphormer) | — | 分子平衡分布予測 |
| **創薬** | TamGen | [microsoft/TamGen](https://github.com/microsoft/TamGen) | 41 | ターゲット認識型分子生成 |
| | RetroChimera | [microsoft/retrochimera](https://github.com/microsoft/retrochimera) | 23 | 逆合成予測 |
| | MoLeR | [microsoft/molecule-generation](https://github.com/microsoft/molecule-generation) | 323 | スキャフォールド制約付き分子生成 |
| **タンパク質** | BioEmu | [microsoft/bioemu](https://github.com/microsoft/bioemu) | 782 | 生体分子平衡アンサンブル |
| | EvoDiff | [microsoft/evodiff](https://github.com/microsoft/evodiff) | 665 | 進化的拡散タンパク質設計 |
| | protein-uq | [microsoft/protein-uq](https://github.com/microsoft/protein-uq) | 21 | 不確実性定量化ベンチマーク |
| **気象・気候** | Aurora | [microsoft/aurora](https://github.com/microsoft/aurora) | 861 | 地球システム予測基盤モデル |
| | ClimaX | [microsoft/ClimaX](https://github.com/microsoft/ClimaX) | 687 | 気象・気候基盤モデル |
| | ADAF | [microsoft/ADAF](https://github.com/microsoft/ADAF) | 12 | AIデータ同化フレームワーク |
| | WeatherReal | [microsoft/WeatherReal-Benchmark](https://github.com/microsoft/WeatherReal-Benchmark) | 43 | 気象予報ベンチマーク |
| | SolarSeer | [microsoft/SolarSeer](https://github.com/microsoft/SolarSeer) | 13 | 太陽放射照度予測 |
| **農業** | FarmVibes.AI | [microsoft/farmvibes-ai](https://github.com/microsoft/farmvibes-ai) | 845 | マルチモーダル地理空間ML |
| **プラットフォーム** | Microsoft Discovery | — (Azure サービス) | — | エージェント型科学R&D基盤 |
| | Azure Quantum Elements | — (Azure サービス) | — | 量子化学クラウドプラットフォーム |
| | Azure AI Foundry | — (Azure サービス) | — | AI for Science モデルカタログ |

---

## 信頼性評価

- **高信頼**: MatterSim, MatterGen, Aurora, ClimaX, EvoDiff, BioEmu, Graphormer, TamGen, RetroChimera, MoLeR, Skala — いずれも GitHub 公開リポジトリと学術論文で確認済み
- **高信頼**: MACE / MACE-MP-0 — ACEsuit 管理だが Microsoft Research 共著・公式掲載で関係が確認済み
- **中信頼**: Microsoft Discovery — Build 2025 で発表されたが、一般提供のタイミングは流動的
- **中信頼**: Azure Quantum Elements の個別機能（Generative Chemistry, Accelerated DFT）— プレビュー・限定アクセスの可能性

---

## 脚注

[^1]: [Microsoft Research AI for Science ラボページ](https://www.microsoft.com/en-us/research/lab/microsoft-research-ai-for-science/)
[^2]: [Azure AI Foundry: Empowering Scientific Discovery with AI](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/azure-ai-foundry-empowering-scientific-discovery-with-ai/4368470)
[^3]: Batatia, I., Kovács, D.P., et al. "MACE: Higher Order Equivariant Message Passing Neural Networks for Fast and Accurate Force Fields." NeurIPS 2022. [arXiv:2206.07697](https://arxiv.org/abs/2206.07697)
[^4]: [Microsoft Research — MACE 公式掲載ページ](https://www.microsoft.com/en-us/research/publication/mace-higher-order-equivariant-message-passing-neural-networks-for-fast-and-accurate-force-fields/)
[^5]: Batatia, I., et al. "A foundation model for atomistic materials chemistry." [arXiv:2401.00096](https://arxiv.org/abs/2401.00096)
[^6]: Han, Y., et al. "MatterSim: A Deep Learning Atomistic Model Across Elements, Temperatures and Pressures." [arXiv:2405.04967](https://arxiv.org/abs/2405.04967)
[^7]: "Accurate and scalable exchange-correlation with deep learning." [arXiv:2506.14665](https://arxiv.org/abs/2506.14665)
[^8]: Zheng, S., et al. "Predicting equilibrium distributions for molecular systems with deep learning." Nature Machine Intelligence (2024). [doi:10.1038/s42256-024-00837-3](https://www.nature.com/articles/s42256-024-00837-3)
[^9]: Wu, Z., et al. "TamGen: drug design with target-aware molecule generation through a chemical language model." Nature Communications (2024). [doi:10.1038/s41467-024-53632-4](https://www.nature.com/articles/s41467-024-53632-4)
[^10]: "Chemist-aligned retrosynthesis by ensembling diverse inductive bias models." [arXiv:2412.05269](https://arxiv.org/abs/2412.05269)
[^11]: Maziarz, K., et al. "Learning to Extend Molecular Scaffolds with Structural Motifs." [arXiv:2103.03864](https://arxiv.org/abs/2103.03864)
[^12]: [Adaptyv Bio: Validating proteins designed by EvoDiff](https://www.adaptyvbio.com/blog/evodiff/)
[^13]: Nguyen, T., et al. "ClimaX: A foundation model for weather and climate." [arXiv:2301.10343](https://arxiv.org/abs/2301.10343)
[^14]: "ADAF: An Artificial Intelligence Data Assimilation Framework for Weather Forecasting." [arXiv:2411.16807](https://arxiv.org/abs/2411.16807)
[^15]: [Transforming R&D with agentic AI: Introducing Microsoft Discovery](https://azure.microsoft.com/en-us/blog/transforming-rd-with-agentic-ai-introducing-microsoft-discovery/)
[^16]: [Azure Quantum Elements](https://azure.microsoft.com/en-us/products/quantum/elements/)
