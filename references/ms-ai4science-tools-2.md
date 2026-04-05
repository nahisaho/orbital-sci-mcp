# MicrosoftのAI for Scienceオープンソースツール全体像

MicrosoftはAI for Science（科学研究向けAI）領域で**40以上のオープンソースプロジェクト**を公開しており、創薬からタンパク質設計、材料科学、気象予測、地球観測まで幅広い分野をカバーしている。これらの多くは「Microsoft Research AI for Science」ラボから生まれ、Nature・Scienceなどのトップジャーナルに掲載された研究成果に基づく。2024〜2025年にかけて**BioEmu**（タンパク質構造アンサンブル、Science掲載）、**MatterGen**（材料生成、Nature掲載）、**Aurora**（地球システム基盤モデル、Nature掲載）、**NatureLM**（マルチドメイン科学基盤モデル）など、インパクトの大きいツールが相次いで公開された。本レポートではこれらを7つのカテゴリに分類し、網羅的に整理する。

---

## 創薬・バイオインフォマティクスは最大の集積地

Microsoftが最も多くのオープンソースツールを投入している分野が創薬・タンパク質科学である。タンパク質の構造予測から分子生成、バイオメディカルNLPまで、パイプラインの各段階に対応するツール群が揃っている。

| ツール名 | 概要 | GitHub URL |
|---------|------|-----------|
| **BioEmu** | アミノ酸配列からタンパク質の平衡構造アンサンブルをサンプリングする大規模深層学習モデル。単一GPUで1時間に数千の独立した構造を生成可能。Science誌掲載 | https://github.com/microsoft/bioemu |
| **BioEmu-Benchmarks** | BioEmuの評価用ベンチマーク。ドメイン運動・局所的アンフォールディング・クリプティックポケットなどの評価基準を提供 | https://github.com/microsoft/bioemu-benchmarks |
| **EvoDiff** | 配列空間における拡散モデルベースのタンパク質生成フレームワーク。UniRef50の4,200万配列で訓練。天然変性領域など構造ベースモデルでは到達困難な領域も生成可能 | https://github.com/microsoft/evodiff |
| **FoldingDiff** | 三角関数とアテンション機構を用いた拡散モデルにより新規タンパク質バックボーン構造を生成 | https://github.com/microsoft/foldingdiff |
| **FrameFlow** | SE(3)フローマッチングによる高速タンパク質バックボーン生成。モチーフ条件付き生成も対応。TMLR 2024掲載 | https://github.com/microsoft/protein-frame-flow |
| **Dayhoff** | 33.4億タンパク質配列を統合したアトラスと生成言語モデル。Mamba+Transformerハイブリッド＋MoEアーキテクチャ。ゼロショット変異効果予測や新規タンパク質生成が可能 | https://github.com/microsoft/dayhoff |
| **TamGen** | ターゲットタンパク質の3D結合ポケット情報を統合したGPT型化学言語モデル。結核ClpPプロテアーゼ阻害剤14種を同定。Nature Communications 2024掲載 | https://github.com/microsoft/TamGen |
| **MoLeR** | スキャフォールド制約付き分子生成モデル。Novartisとの共同開発。分子グラフの段階的構築と可視化をサポート | https://github.com/microsoft/molecule-generation |
| **DVMP** | グラフ表現とSMILES配列の二重ビューによる分子事前学習モデル。分子特性予測に活用 | https://github.com/microsoft/DVMP |
| **Protein-sequence-models** | CARP（畳み込み自己回帰タンパク質モデル）やMIF（マスク逆フォールディング）などの事前学習済みタンパク質配列・構造モデル群 | https://github.com/microsoft/protein-sequence-models |
| **PEFT Proteomics** | タンパク質言語モデルへのLoRA（Low-Rank Adaptation）適用。タンパク質間相互作用予測などに対応 | https://github.com/microsoft/peft_proteomics |
| **BioGPT** | PubMed文献で事前学習したバイオメディカル特化GPTモデル。テキスト生成・関係抽出・QAをサポート。MIT License | https://github.com/microsoft/BioGPT |
| **BiomedBERT** | PubMed抄録からスクラッチで事前学習した生物医学BERT。BLURBベンチマーク13データセットでSOTA達成 | HuggingFace: microsoft/BiomedNLP-BiomedBERT-* |
| **Prov-GigaPath** | **13億枚**の病理画像タイルで事前学習したデジタル病理基盤モデル。Providence Health Systemとの共同開発。Nature掲載 | https://github.com/prov-gigapath/prov-gigapath |
| **GigaTIME** | H&E染色スライドから仮想多重免疫蛍光画像を生成し、腫瘍微小環境を解析。24がん種・14,256患者に適用。Cell 2025掲載 | https://github.com/prov-gigatime/GigaTIME |
| **CromwellOnAzure** | Broad InstituteのCromwellワークフローエンジンのAzure実装。GATKパイプラインなどのゲノム解析を大規模実行可能 | https://github.com/microsoft/CromwellOnAzure |
| **Genomics Notebooks** | Azure上でのゲノムデータ解析用Jupyterノートブック集。GATKワークフロー・放射線ゲノミクス・FHIR統合をカバー | https://github.com/microsoft/genomicsnotebook |

BioEmuはとくに注目すべきツールで、分子動力学シミュレーションの数桁高速化を実現し、タンパク質の「構造アンサンブル」を直接予測する新しいパラダイムを切り開いた。EvoDiffやDayhoffと組み合わせることで、タンパク質設計から動態解析までの一貫したワークフローが構築できる。

---

## 化学・分子モデリングのコアとなるGraphormerエコシステム

分子モデリングの中核をなすのがGraphormerファミリーである。グラフTransformerアーキテクチャをベースに、分子特性予測から平衡分布推定、生体分子動力学シミュレーションまで広がるエコシステムを形成している。

| ツール名 | 概要 | GitHub URL |
|---------|------|-----------|
| **Graphormer** | グラフTransformerベースの汎用分子モデリング基盤。KDD Cup 2021・Open Catalyst Challengeで1位。PyG/DGL/OGB/OCPインターフェース対応。NeurIPS 2021掲載 | https://github.com/microsoft/Graphormer |
| **Distributional Graphormer（DiG）** | 分子系の**平衡分布**を予測する深層学習フレームワーク。単一構造予測からアンサンブル予測へのパラダイムシフトを実現。タンパク質動態・リガンド結合・触媒系に適用。Nature Machine Intelligence 2024掲載 | https://github.com/microsoft/Graphormer （dig-v1.0ブランチ） |
| **AI2BMD（ViSNet / Geoformer）** | AI駆動のab initio生体分子動力学シミュレーションプラットフォーム。ViSNet（ベクトル-スカラー対話型メッセージパッシング）とGeoformer（幾何Transformer）を搭載。Nature Communications 2024掲載 | https://github.com/microsoft/AI2BMD |
| **QDK-Chemistry** | Microsoft Quantum Development Kitの化学計算ツールキット。量子アルゴリズムと古典的電子構造計算のエンドツーエンドパイプライン。Q#・Qiskit・Cirq対応 | https://github.com/microsoft/qdk-chemistry |
| **Accelerated DFT** | Azure Quantum Elements上のGPU加速DFTプログラムのベンチマーク・サンプル集。PySCF比**20倍**の高速化を実現 | https://github.com/microsoft/accelerated-dft |
| **Chemistry-QA** | 約4,500問・200トピックの化学QAベンチマーク。AI の化学的推論能力を評価 | https://github.com/microsoft/chemistry-qa |

Graphormerは**約2,400スター**を獲得しており、Microsoft AI for Science全体のフラッグシップ的存在である。DiGはその発展形として、従来の「1つの安定構造を予測する」アプローチから「平衡分布全体を予測する」アプローチへの転換を示し、創薬における自由エネルギー計算やタンパク質-リガンド相互作用の解析に新たな道を開いた。

---

## 材料科学はMatterGen＋MatterSimの二本柱

材料科学領域ではMatterGen（材料生成）とMatterSim（材料シミュレーション）が密接に連携する設計になっている。

| ツール名 | 概要 | GitHub URL |
|---------|------|-----------|
| **MatterGen** | 無機材料の**生成拡散モデル**。原子座標・元素種・格子ベクトルを同時予測。バルク弾性率・磁気密度・化学系などの特性制約付き生成が可能。Nature 2025掲載 | https://github.com/microsoft/mattergen |
| **MatterSim** | 全元素・0〜5000K・最大1000GPaに対応する機械学習力場（MLFF）。DFTの代替として材料特性を高速予測。M3GNetアーキテクチャ、1Mおよび5Mパラメータモデル。ASE統合対応 | https://github.com/microsoft/mattersim |

MatterGenで候補材料を生成し、MatterSimで構造緩和・安定性評価を行うワークフローが想定されている。Microsoftはこの組み合わせで367,000候補から新規データセンター冷却材を約200時間で発見したと報告しており、「Microsoft Discovery」プラットフォーム（Build 2025で発表）の中核技術となっている。MatterSimはv1.2.1（2025年2月）が最新版で、DFTレベルの精度を数桁高速に実現する。

---

## 気候・気象・地球科学では基盤モデルからデータ基盤まで完備

気象・地球科学は、Microsoftが最も幅広いスタックを提供している分野の一つである。基盤モデル（Aurora, ClimaX）から地理空間MLライブラリ（TorchGeo）、データプラットフォーム（Planetary Computer）、ベンチマーク（WeatherReal）まで、エコシステム全体が整備されている。

**気象・気候モデル：**

| ツール名 | 概要 | GitHub URL |
|---------|------|-----------|
| **Aurora** | **13億パラメータ**の地球システム基盤モデル。中解像度・高解像度気象予測、大気汚染予測、海洋波浪予測に対応。LoRAファインチューニング対応。Nature 2025掲載 | https://github.com/microsoft/aurora |
| **ClimaX** | Vision Transformerベースの気象・気候基盤モデル。異種データセット（変数・解像度が異なる）を吸収可能。CMIP6データで事前学習。ICML 2023掲載 | https://github.com/microsoft/ClimaX |
| **WeatherReal-Benchmark** | AIの気象モデルを**実観測データ**（再解析データではなく）で評価する初のベンチマーク。GraphCast・Pangu-Weather等を比較評価 | https://github.com/microsoft/WeatherReal-Benchmark |
| **Subseasonal Toolkit** | 2〜6週間先の季節内予測MLモデル群。NOAA/USBRとの共同開発。適応バイアス補正（ABC）手法を搭載 | https://github.com/microsoft/subseasonal_toolkit |
| **Subseasonal Data** | SubseasonalClimateUSAデータセットへのアクセスパッケージ。NeurIPS 2023掲載 | https://github.com/microsoft/subseasonal_data |

Auroraは気象AIモデルの中でも最大級の規模を持ち、**4つの専門モデル**（中解像度気象・高解像度気象・大気汚染・海洋波浪）を提供する。2025年11月には訓練パイプラインも公開された。ClimaXは「変数トークン化」というアプローチで異なる変数セット・解像度のデータを柔軟に取り込める点が特徴で、ファインチューニングにより多様な下流タスクに適応する。

**地理空間・リモートセンシング・環境データ：**

| ツール名 | 概要 | GitHub URL |
|---------|------|-----------|
| **TorchGeo** | PyTorchベースの地理空間MLライブラリ。30以上のデータローダー、120以上のベンチマークデータセット、**110以上の事前学習モデル**を搭載。OSGeoコミュニティプロジェクト | https://github.com/microsoft/torchgeo |
| **Earth Copilot** | 自然言語で地球科学データを探索・可視化するAIアプリ。Ignite 2024でサティア・ナデラが紹介 | https://github.com/microsoft/Earth-Copilot |
| **Planetary Computer** | ペタバイト規模の地理空間データプラットフォーム。STAC API・Python SDK・開発ハブを提供 | https://github.com/microsoft/PlanetaryComputer |
| **AIforEarthDataSets** | Azure上の地理空間データセット群のドキュメントとデモ。NOAA気象・Sentinel・Landsat等数十のデータセットをカバー | https://github.com/microsoft/AIforEarthDataSets |
| **Global Renewables Watch** | 衛星画像から全球の太陽光パネル・風力タービンを検出。**13兆ピクセル以上**を処理し375,197基の風力タービンと86,410の太陽光発電所を特定 | https://github.com/microsoft/global-renewables-watch |
| **Land Cover Mapping** | 衛星画像を用いた対話型土地被覆マッピングツール。推論とファインチューニングをブラウザ上で実行可能 | https://github.com/microsoft/landcover |

TorchGeoは地理空間ML分野のデファクトスタンダード的ライブラリに成長しており、マルチスペクトル衛星画像の事前学習モデルを最初に提供したライブラリでもある。Planetary Computerとの組み合わせにより、データ取得からモデル訓練・推論まで一貫したワークフローが構築可能である。

---

## 汎用科学基盤モデルとフレームワーク

特定分野に限定されない、横断的な科学研究プラットフォーム・フレームワークも複数公開されている。

| ツール名 | 概要 | GitHub URL |
|---------|------|-----------|
| **SFM / NatureLM** | 小分子・材料・タンパク質・DNA・RNAを統一的に扱う科学基盤モデル。GPTアーキテクチャベースで**1B・8B・46.7B（8×7B MoE）**の3サイズ。テキスト指示による生物・化学エンティティの生成・最適化が可能。22以上の科学タスクカテゴリでトップ性能 | https://github.com/microsoft/SFM |
| **LLM4ScientificDiscovery** | GPT-4の科学的発見への影響を評価する研究。創薬・生物学・計算化学・材料設計・PDEの各領域でLLMの能力を体系的に検証 | https://github.com/microsoft/LLM4ScientificDiscovery |
| **DeepSpeed4Science** | DeepSpeed内の科学計算特化イニシアティブ。ClimaXのスケーリング、AI駆動分子動力学（AI2MD）、国立研究機関との連携プロジェクトを推進 | https://github.com/deepspeedai/DeepSpeed |
| **Industrial Foundation Models** | 表形式データからの産業横断的知識抽出を強化するLLM。ヘルスケア・エネルギー・農業・輸送の各分野に適用 | https://github.com/microsoft/Industrial-Foundation-Models |

NatureLMは2024〜2025年に登場した最も野心的なプロジェクトの一つで、「分子・タンパク質・DNA・RNA・材料」という従来別々に扱われていたドメインを**単一のシーケンスモデル**で統合する。46.7Bパラメータの最大モデルはMixture-of-Expertsアーキテクチャを採用し、自然言語による指示でリガンド設計やCRISPRガイドRNA最適化などを実行できる。

---

## 生態系・農業・その他の科学応用

Microsoft AI for Earthプログラムの流れを汲む環境・生態系保全ツールも充実している。

| ツール名 | 概要 | GitHub URL |
|---------|------|-----------|
| **CameraTraps / PyTorch Wildlife** | カメラトラップ画像から動物・人・車両を検出する**MegaDetector**（v6）を搭載。世界100以上の保全機関が利用 | https://github.com/microsoft/CameraTraps |
| **FarmVibes.AI** | 農業・持続可能性向けマルチモーダル地理空間MLプラットフォーム。雲除去（SpaceEye）、マイクロ気候予測（DeepMC）、土壌炭素推定、作物セグメンテーション等を統合 | https://github.com/microsoft/farmvibes-ai |
| **Acoustic Bird Detection** | 音声録音からの鳥類検出ML ツール | https://github.com/microsoft/acoustic-bird-detection |
| **Bird Acoustics RCNN** | RCNNベースの100鳥種分類モデル | https://github.com/microsoft/bird-acoustics-rcnn |
| **Global ML Building Footprints** | Bing Maps衛星画像から生成した全球**14億棟**の建物フットプリント。2026年2月更新 | https://github.com/microsoft/GlobalMLBuildingFootprints |

FarmVibes.AIは農業分野における最も包括的なツールで、衛星画像・ドローン画像・気象データ・地形データを融合し、精密農業から炭素クレジット推定まで幅広いユースケースに対応する。Kubernetesベースのワークフローエンジンを内蔵し、大規模処理にも対応している。

---

## まとめと展望

Microsoftの AI for Scienceオープンソースエコシステムは、3つの明確なトレンドを示している。第一に、**基盤モデル化の加速**。NatureLM・Aurora・BioEmuなど、各分野で数億〜数十億パラメータの基盤モデルが登場し、ファインチューニングで多様なタスクに適応する設計が主流になった。第二に、**生成AIの科学への本格適用**。MatterGen（材料生成）・EvoDiff（タンパク質生成）・TamGen（薬物分子生成）・MoLeR（スキャフォールド制約付き分子生成）など、拡散モデルやGPTアーキテクチャによる「科学的実体の生成」が全分野で進んでいる。第三に、**エンドツーエンドのワークフロー統合**。生成（MatterGen）→評価（MatterSim）→発見（Microsoft Discovery）、あるいは配列設計（EvoDiff）→構造アンサンブル（BioEmu）→動力学シミュレーション（AI2BMD）といったパイプライン全体をカバーする設計思想が明確である。

2025年のMicrosoft Build で発表された「**Microsoft Discovery**」プラットフォームは、これらのオープンソースツールをAIエージェントとして統合し、研究者がCopilotインターフェースで科学的発見ワークフロー全体をオーケストレーションする未来を提示している。オープンソースの個別ツール群と商用プラットフォームの双方が揃ったことで、Microsoftは学術研究者から産業R&Dまでの幅広い層にアプローチする体制を構築している。