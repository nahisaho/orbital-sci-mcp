# AI for Science 向け MCP サーバー包括調査

**科学研究を変革する MCP エコシステムが急速に成熟しつつある。** 2025年後半から2026年にかけて、生物学・化学・物理学・データ解析の各分野で **100以上の科学特化型 MCP サーバー** が登場し、PubMed・UniProt・ChEMBL・Materials Project など主要な科学データベースへのAIアシスタント経由のアクセスが実現した。特に Augmented Nature（19+サーバー）、BioMCP（466スター）、mcp.science（112スター）の3大プロジェクトが中核的な役割を果たしている。本調査では、分野・用途ごとに主要な MCP サーバーを網羅的に整理する。

---

## 主要プロジェクトとエコシステムの全体像

科学向け MCP サーバーは、個別データベースへの接続サーバーと、複数データベースを統合するアグリゲーター型サーバーに大別できる。開発組織としては以下が特に重要である。

**Augmented Nature**（https://github.com/Augmented-Nature）は、UniProt・ChEMBL・PDB・PubChem・Ensembl など **19以上の生命科学データベース** を個別の MCP サーバーとしてラップする最大規模のプロジェクトである。すべて Node.js/TypeScript で統一されており、`npm install` または Docker でインストールできる。

**BioMCP**（https://github.com/genomoncology/biomcp、**466スター**）は GenomOncology 社が開発するオープンソースの統合バイオメディカル MCP サーバーで、PubMed・ClinicalTrials.gov・MyVariant.info・cBioPortal など **15以上のデータソース** に単一インターフェースからアクセスできる。`pip install biomcp-cli` でインストール可能で、STDIO・SSE・HTTP の各トランスポートに対応する。

**mcp.science**（https://github.com/pathintegral-institute/mcp.science、**112スター**）は Path Integral Institute が開発する物理・材料科学中心のサーバーコレクションで、Materials Project・GPAW（DFT計算）・Jupyter カーネル・Wolfram Language など科学計算に必要な機能を集約している。`uvx mcp-science <server-name>` で各サーバーを起動できる。

**BioContextAI**（https://github.com/biocontext-ai/knowledgebase-mcp）は **Nature Biotechnology** に掲載された統合バイオメディカル MCP サーバーで、20以上のデータベースに統一アクセスを提供する。コミュニティレジストリ（https://biocontext.ai/registry）も運営しており、`uvx biocontext_kb@latest` でインストールする。

---

## 文献検索・論文調査に使える MCP サーバー

文献検索は MCP エコシステムで最も成熟したカテゴリであり、**20以上のサーバー** が存在する。用途に応じた選択指針を以下に示す。

### 多分野横断型（最も網羅的）

| サーバー名 | GitHub URL | 対応データソース | インストール |
|-----------|-----------|----------------|------------|
| **paper-search-mcp** | https://github.com/openags/paper-search-mcp | arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, Semantic Scholar, Crossref, OpenAlex, PMC, CORE, Europe PMC, DBLP, OpenAIRE, CiteSeerX, DOAJ, BASE, Zenodo, HAL, SSRN, Unpaywall（**22ソース**） | `uvx paper-search-mcp` / Docker: `mcp/paper-search` |
| **paper-distill-mcp** | https://github.com/Eclipse-Cj/paper-distill-mcp | OpenAlex, Semantic Scholar, PubMed, arXiv, Papers with Code, CrossRef, Europe PMC, bioRxiv, DBLP, CORE, Unpaywall（**11ソース**、AI ランキング付き） | `uvx paper-distill-mcp` |
| **PaperMCP** | https://github.com/ScienceAIHub/PaperMCP | arXiv, HuggingFace, Google Scholar, OpenReview, DBLP, PapersWithCode（32ツール） | `claude mcp add paper-mcp` |
| **Academix** | https://github.com/xingyulu23/Academix | OpenAlex, DBLP, Semantic Scholar, arXiv, CrossRef | `uv run academix` |
| **Scientific-Papers-MCP** | https://github.com/benedict2310/Scientific-Papers-MCP | arXiv, OpenAlex, bioRxiv, PMC, Europe PMC, CORE（200M+論文） | `npx @futurelab-studio/latest-science-mcp@latest` |

**paper-search-mcp** が22ソースをカバーし最も網羅的で、Docker Hub 公式イメージも提供される。**paper-distill-mcp** は独自のAIランキング（関連性×新しさ×インパクト×新規性の4次元重み付け）が特徴的である。

### arXiv 特化型

| サーバー名 | GitHub URL | 特徴 | インストール |
|-----------|-----------|------|------------|
| **arxiv-mcp-server** | https://github.com/blazickjp/arxiv-mcp-server | 検索・ダウンロード・Markdown変換・カテゴリフィルタ | `uvx arxiv-mcp-server` |
| **mcp-simple-arxiv** | https://github.com/andybrandt/mcp-simple-arxiv | PDF→Markdown変換、カテゴリ閲覧 | Smithery CLI |
| **arxiv-latex-mcp** | https://github.com/takashiishida/arxiv-latex-mcp | LaTeXソース取得（数式の正確な解釈に最適） | uv設定 |

物理学・数学の論文には **arxiv-latex-mcp** が特に有用で、PDF ではなく LaTeX ソースを直接取得するため、数式を正確にAIに読ませることができる。

### PubMed 特化型（10以上の実装あり）

| サーバー名 | GitHub URL | 特徴 | インストール |
|-----------|-----------|------|------------|
| **cyanheads/pubmed-mcp-server** | https://github.com/cyanheads/pubmed-mcp-server | 7ツール、NCBI E-utilities、PMC全文取得、MeSH対応 | `npx @cyanheads/pubmed-mcp-server` |
| **Augmented-Nature/PubMed-MCP-Server** | https://github.com/Augmented-Nature/PubMed-MCP-Server | 16ツール、著者・ジャーナル・MeSH検索 | Node.js |
| **mcp-simple-pubmed** | https://github.com/andybrandt/mcp-simple-pubmed | シンプル実装 | `pip install mcp-simple-pubmed` |
| **pubmedmcp** | https://github.com/grll/pubmedmcp | 軽量実装 | `uvx pubmedmcp@latest` |

### Semantic Scholar 特化型

| サーバー名 | GitHub URL | インストール |
|-----------|-----------|------------|
| **semantic-scholar-fastmcp** | https://github.com/zongmin-yu/semantic-scholar-fastmcp-mcp-server | `uvx semantic-scholar-fastmcp`（16ツール） |
| **semanticscholar-MCP-Server** | https://github.com/JackKuo666/semanticscholar-MCP-Server | pip / Smithery |
| **AIRA-SemanticScholar** | https://github.com/hamid-vakilzadeh/AIRA-SemanticScholar | `npx -y aira-semanticscholar`（Wiley TDM統合） |

### その他の学術検索

**NASA ADS MCP**（https://github.com/prtc/nasa-ads-mcp）は天文学・宇宙物理学の論文検索に特化し、**Google Scholar MCP**（https://github.com/JackKuo666/Google-Scholar-MCP-Server）は Google Scholar のラッパーとして機能する。**ScholarAI MCP**（https://scholarai.io/blog/mcp）は HIPAA 準拠のセキュアな研究アクセスを提供する商用サービスである。

---

## 生物学・バイオインフォマティクス分野の MCP サーバー

この分野は MCP エコシステムで最も充実しており、タンパク質データベース、ゲノミクス、パスウェイ解析、バイオインフォマティクスツールの各領域に専用サーバーが存在する。

### タンパク質データベース・構造生物学

| サーバー名 | GitHub URL | 接続先DB | 主な機能 | インストール |
|-----------|-----------|---------|---------|------------|
| **UniProt MCP**（Augmented Nature） | https://github.com/Augmented-Nature/Augmented-Nature-UniProt-MCP-Server | UniProt REST API | **26ツール**：タンパク質検索、配列取得、機能解析、ホモログ発見、KEGG/Reactome連携、相互作用、バッチ処理 | npm / Docker |
| **UniProt MCP**（TakumiY235） | https://github.com/TakumiY235/uniprot-mcp-server | UniProt | アクセッション番号による検索、機能・配列・生物種情報（9スター） | `uv pip install` |
| **PDB MCP Server** | https://github.com/Augmented-Nature/PDB-MCP-Server | Protein Data Bank | 構造検索、PDB/mmCIF/mmTF ダウンロード、品質メトリクス、UniProt連携（**21スター**） | npm |
| **AlphaFold MCP Server** | https://github.com/Augmented-Nature/AlphaFold-MCP-Server | AlphaFold DB | 構造予測取得、信頼度スコア分析、PyMOL/ChimeraX エクスポート、バッチ処理 | npm |
| **STRING-db MCP** | https://github.com/Augmented-Nature/STRING-db-MCP-Server | STRING | タンパク質相互作用ネットワーク、機能エンリッチメント | npm |
| **ProteinAtlas MCP** | https://github.com/Augmented-Nature/ProteinAtlas-MCP-Server | Human Protein Atlas | 組織別発現、細胞内局在、病理データ | npm |

### 分子可視化・MD シミュレーション

**molecule-mcp**（https://github.com/ChatMol/molecule-mcp）は PyMOL・ChimeraX・GROMACS を MCP 経由で制御でき、分子可視化から MD シミュレーションまでを自然言語で操作できる。**pymol-mcp**（https://github.com/vrtejus/pymol-mcp）は PyMOL との双方向通信に特化し、**pymol-mcp-vis**（https://github.com/ryannmperez/pymol-mcp-vis）はスクリーンショットキャプチャによるビジュアルフィードバック機能を追加している。

### ゲノミクス・遺伝子発現

| サーバー名 | GitHub URL | 接続先DB | 主な機能 |
|-----------|-----------|---------|---------|
| **Ensembl MCP** | https://github.com/Augmented-Nature/Ensembl-MCP-Server | Ensembl REST API | **25ツール**：遺伝子・転写産物検索、配列取得、相同性、変異アノテーション |
| **NCBI Datasets MCP** | https://github.com/Augmented-Nature/NCBI-Datasets-MCP-Server | NCBI Datasets | **31ツール**：ゲノムアセンブリ、遺伝子モデル、分類、配列 |
| **GTEx MCP** | https://github.com/Augmented-Nature/GTEx-MCP-Server | GTEx | **25ツール**：組織特異的遺伝子発現、eQTL データ |
| **gget-mcp** | https://github.com/longevity-genie/gget-mcp | Ensembl, BLAST, PDB, COSMIC | gget ライブラリのラッパー：遺伝子検索、配列取得、BLAST、アラインメント |
| **BioThings MCP** | https://github.com/Augmented-Nature/BioThings-MCP-Server | MyGene.info, MyVariant.info | 22M+遺伝子、400M+変異のバッチクエリ |
| **NCBI SRA MCP** | https://github.com/CSI-Genomics-and-Data-Analytics-Core/ncbi-sra-mcp-server | NCBI SRA, ENA | シーケンスリードアーカイブのデータアクセス |

### パスウェイ・オントロジー・システム生物学

| サーバー名 | GitHub URL | 接続先DB |
|-----------|-----------|---------|
| **Reactome MCP** | https://github.com/Augmented-Nature/Reactome-MCP-Server | Reactome（**10スター**） |
| **KEGG MCP** | https://github.com/Augmented-Nature/KEGG-MCP-Server | KEGG |
| **Gene Ontology MCP** | https://github.com/Augmented-Nature/GeneOntology-MCP-Server | Gene Ontology（**7スター**） |
| **BioOntology MCP** | https://github.com/Augmented-Nature/BioOntology-MCP-Server | BioPortal（1,200+オントロジー、**8スター**） |

### バイオインフォマティクスCLIツール（bio-mcp）

**bio-mcp**（https://github.com/bio-mcp）は、従来コマンドラインで使われてきたバイオインフォマティクスツールを MCP サーバーとしてラップした画期的なプロジェクトである。

- **bio-mcp-blast** — NCBI BLAST（blastn/blastp/blastx/tblastn/tblastx）
- **bio-mcp-bwa** — BWA リードアラインメント
- **bio-mcp-samtools / bcftools** — SAM/BAM ファイル操作、バリアントコーリング
- **bio-mcp-seqkit** — SeqKit 配列ツールキット
- **bio-mcp-amber** — AMBER 分子動力学
- **bio-mcp-interpro** — InterPro タンパク質ドメイン分類
- **bio-mcp-evo2** — Evo2 DNA言語モデル

すべて Python ベースで Docker / Conda でインストールする。AIエージェントが BLAST 検索やアラインメントを自律的に実行できる点が画期的である。

### 統合型バイオメディカルサーバー

**Biotools MCP**（https://github.com/BACH-AI-Tools/biotools-mcp-server）は「スイスアーミーナイフ」を自称し、PubMed・UniProt・NCBI GenBank・KEGG・PDB など11以上のデータベースに **37ツール** でアクセスできる。`npx -y biotools-mcp-server` でインストール可能。

**Medical MCPs**（https://github.com/pascalwhoop/medical-mcps）は **14のAPI に100以上のツール** を提供し、Reactome・KEGG・UniProt・OMIM・GWAS Catalog・ChEMBL・ClinicalTrials.gov・PubMed・OpenFDA 等を網羅する。

**mcp-biomodelling-servers**（https://github.com/marcorusc/mcp-biomodelling-servers）は計算生物学に特化し、MaBoSS（ブーリアンモデル）、NeKo（ネットワーク生物学）、PhysiCell（マルチセルシミュレーション）を提供する。

---

## 化学・創薬分野の MCP サーバー

### 化合物データベース

| サーバー名 | GitHub URL | 接続先DB | 主な機能 | インストール |
|-----------|-----------|---------|---------|------------|
| **ChEMBL MCP**（Augmented Nature） | https://github.com/Augmented-Nature/ChEMBL-MCP-Server | ChEMBL REST API | **22ツール**：化合物検索、類似性検索、部分構造検索、ターゲット解析、活性データ、ADMET、薬物ステータス（**77スター**） | npm / Docker |
| **PubChem MCP**（cyanheads） | https://github.com/cyanheads/pubchem-mcp-server | PubChem | 10ツール：名前/SMILES/InChIKey 検索、物性、構造画像、類似性検索、バイオアッセイ | npm |
| **PubChem MCP**（Augmented Nature） | https://github.com/Augmented-Nature/PubChem-MCP-Server | PubChem | **1.1億以上の化合物**、薬物様性評価、安全性データ | npm |
| **PubChem MCP**（JackKuo666） | https://github.com/JackKuo666/PubChem-MCP-Server | PubChem | 名前/SMILES/CID 検索、2D/3D 可視化 | pip |
| **PubChem MCP**（PhelanShao） | https://github.com/PhelanShao/pubchem-mcp-server | PubChem | XYZ/SDF 構造ファイル生成、RDKit 連携 | pip |

### ケモインフォマティクス（RDKit）

**tandemai-inc/rdkit-mcp-server**（https://github.com/tandemai-inc/rdkit-mcp-server）は RDKit 2025.3.1 の全機能を MCP 経由で利用可能にする野心的なサーバーで、自然言語による分子操作と CLI クライアントを備える。**mcp_rdkit**（https://github.com/s20ss/mcp_rdkit、`pip install mcp-rdkit`）は分子可視化と記述子計算に特化する。

### 創薬・ターゲット探索

| サーバー名 | GitHub URL | 接続先DB | 特徴 |
|-----------|-----------|---------|------|
| **Open Targets MCP**（公式） | https://github.com/opentargets/open-targets-platform-mcp | Open Targets Platform | **公式サーバー**。ホスト版あり：https://mcp.platform.opentargets.org/mcp/ |
| **opentargets-mcp**（nickzren） | https://github.com/nickzren/opentargets-mcp | Open Targets | **49の GraphQL 操作**、`pip install opentargets-mcp` |
| **DrugBank MCP** | https://github.com/openpharma-org/drugbank-mcp-server | DrugBank（SQLite、17,430+薬物） | 16メソッド：名前/構造/カテゴリ検索、薬物相互作用、経路 |
| **SureChEMBL MCP** | https://github.com/Augmented-Nature/SureChEMBL-MCP-Server | SureChEMBL | 化学特許検索、先行技術調査 |
| **OpenFDA MCP** | https://github.com/Augmented-Nature/OpenFDA-MCP-Server | OpenFDA | FDA 医薬品ラベル、有害事象、リコール、承認情報 |
| **ClinicalTrials MCP** | https://github.com/Augmented-Nature/ClinicalTrials-MCP-Server | ClinicalTrials.gov | 臨床試験検索・詳細取得 |

Open Targets の**公式 MCP サーバー**が存在する点は特筆に値する。遺伝子-薬物-疾患の関連性を GraphQL で直接クエリでき、創薬パイプラインの標的探索に不可欠なリソースである。

---

## 物理学・材料科学分野の MCP サーバー

物理学・材料科学は他の分野と比べると MCP サーバーの数はまだ少ないが、**mcp.science** を中心に重要なツールが整備されつつある。

### 材料科学

| サーバー名 | GitHub URL | 接続先DB/ツール | 主な機能 |
|-----------|-----------|---------------|---------|
| **Materials Project MCP**（mcp.science内） | https://github.com/pathintegral-institute/mcp.science | Materials Project API | 材料データの検索・可視化・操作（API キー必要） |
| **OPTIMADE MCP** | https://github.com/dianfengxiaobo/optimade-mcp-server | Materials Project, Materials Cloud, COD, GNoME | OPTIMADE 準拠の材料データベースへの統一アクセス |
| **MatMCP** | Glama.ai 掲載 | GNoME（DeepMind） | 数百万の予測安定結晶構造へのアクセス |

**OPTIMADE MCP** は、Materials Project・Materials Cloud・COD（Crystallography Open Database）・GNoME（Google DeepMind の安定結晶構造予測データセット）など複数の結晶構造データベースに統一プロトコルでアクセスでき、材料探索ワークフローを効率化する。

### 計算物理・DFT 計算

**GPAW MCP**（mcp.science 内）は密度汎関数理論（DFT）計算を GPAW パッケージ経由で実行する。**VASPilot** は最近 arXiv に発表された研究（arXiv:2508.07035）で、MCP を活用したマルチエージェントシステムにより VASP での DFT シミュレーション（バンド構造・状態密度計算）を自律的に実行する手法を示している。

### 量子力学・量子コンピューティング

| サーバー名 | GitHub URL | 特徴 | インストール |
|-----------|-----------|------|------------|
| **PsiAnimator-MCP** | https://github.com/manasp21/PsiAnimator-MCP | 量子力学エンジン＋Manim アニメーション、ブロッホ球・ウィグナー関数 | `pip install psianimator-mcp` |
| **scicomp-quantum-mcp** | https://github.com/andylbrummer/math-mcp | GPU加速の量子物理シミュレーション | `pip install scicomp-quantum-mcp` |
| **Qiskit MCP** | https://github.com/barvhaim/qiskit-mcp-server | IBM Qiskit SDK のラッパー | Python |

### 宇宙科学・天文学

**NASA MCP Server**（https://github.com/ProgramComputer/NASA-MCP-server）は 20以上の NASA API（APOD、火星探査車画像、近地球天体、衛星画像、宇宙天気など）にアクセスでき、`npx @programcomputer/nasa-mcp-server` でインストールする。天文学論文の検索には前述の **NASA ADS MCP**（https://github.com/prtc/nasa-ads-mcp）が有用である。

### 物理シミュレーション

**Genesis World MCP**（https://github.com/dustland/genesis-mcp）は Genesis World 物理プラットフォーム上でロボティクス・具身化 AI のシミュレーションを制御する。**scicomp-molecular-mcp**（math-mcp 内）は分子動力学シミュレーション用の GPU 加速計算を提供する。

---

## データ解析・統計・コード実行の MCP サーバー

### Jupyter ノートブック連携

データ解析ワークフローの中核となる Jupyter 連携は複数の成熟した実装がある。

| サーバー名 | GitHub URL / パッケージ | 特徴 | インストール |
|-----------|----------------------|------|------------|
| **jupyter-mcp-server**（datalayer） | https://github.com/datalayer/jupyter-mcp-server | **最も充実**：12+ツール、セル追加/挿入/実行、マルチモーダル（画像・プロット） | `pip install jupyter-mcp-tools>=0.1.4` |
| **mcp-jupyter**（Block/Goose） | PyPI: mcp-jupyter | JupyterLab 統合、永続変数状態、stdio/HTTP 対応 | `uvx mcp-jupyter` |
| **Jupyter-Act**（mcp.science内） | mcp.science モノレポ | 実行中の Jupyter カーネルとの対話 | `uvx mcp-science jupyter-act` |

### Python コード実行サンドボックス

| サーバー名 | GitHub URL | 特徴 | インストール |
|-----------|-----------|------|------------|
| **mcp-run-python**（Pydantic） | https://github.com/pydantic/mcp-run-python | WebAssembly（Pyodide）サンドボックス、依存関係自動検出 | `uvx mcp-run-python` |
| **code-sandbox-mcp**（Automata-Labs） | https://github.com/Automata-Labs-team/code-sandbox-mcp | Docker ベース、ファイル操作、リアルタイムログ | curl インストーラ |
| **llm-sandbox** | https://github.com/vndee/llm-sandbox | **7言語対応**（Python, JS, Java, C++, Go, R, Ruby）、自動可視化キャプチャ | `pip install 'llm-sandbox[mcp-docker]'` |
| **mcp-sandbox** | https://github.com/JohanLi233/mcp-sandbox | Docker 隔離 Python 実行、パッケージ管理、Web UI | git clone + uv |

科学計算には **llm-sandbox** が特に適している。Python・R を含む7言語に対応し、Docker/Podman/Kubernetes バックエンドで安全に実行でき、matplotlib のプロット自動キャプチャ機能を備える。

### データ可視化

**matplotlib_mcp**（https://github.com/newsbubbles/matplotlib_mcp）は Matplotlib の全機能を MCP 経由で提供し、折れ線グラフ、散布図、ヒストグラム、ヒートマップ、3D 可視化、ベクトル場、極座標プロットなどを生成できる。**visualization-mcp-server**（xlisp）は matplotlib・numpy・pandas・networkx を統合した8種類の専用可視化ツールを提供する。

### R 言語対応

**rlang-mcp-server**（https://github.com/gdbelvin/rlang-mcp-server）は R スクリプト実行と ggplot2 による可視化（PNG/JPEG/PDF/SVG）を提供する。**rlang-mcp-python**（https://github.com/saidsurucu/rlang-mcp-python）はその Python 再実装版で、Docker ベースの R 実行環境とスマートキャッシングを備える。

### 数学・記号計算

**Mathematica-Check**（mcp.science 内）は Wolfram Language のコードをヘッドレス Mathematica インスタンスで評価する。**scicomp-math-mcp**（https://github.com/andylbrummer/math-mcp）は GPU 加速の計算数学サーバーである。

### データベース接続

科学データの格納・クエリには **postgres-mcp**（https://github.com/crystaldba/postgres-mcp）が有用で、pgvector（ベクトル検索）や PostGIS（地理空間データ）などの拡張にも対応する。公式 MCP サーバーリポジトリには **SQLite** と **PostgreSQL** のリファレンス実装も含まれる。

---

## 実践的な導入ガイド：用途別の推奨構成

### 創薬研究のワークフロー例

創薬パイプラインを AI アシスタントで支援する場合、以下の構成が推奨される。ターゲット探索には **Open Targets 公式 MCP** と **UniProt MCP** を、化合物スクリーニングには **ChEMBL MCP** と **PubChem MCP** を、構造解析には **PDB MCP** と **AlphaFold MCP** を、文献調査には **paper-search-mcp** を、データ解析には **jupyter-mcp-server** を組み合わせる。Augmented Nature のサーバー群はすべて Node.js で統一されており、同一環境で一括導入しやすい。

### ゲノム解析のワークフロー例

ゲノム解析では **bio-mcp**（BLAST・BWA・samtools）でシーケンスデータの処理を行い、**Ensembl MCP** と **NCBI Datasets MCP** でアノテーションを取得し、**BioThings MCP** でバリアントの機能的意義を調査し、**KEGG/Reactome MCP** でパスウェイ解析を実行する構成が効率的である。

### 材料科学のワークフロー例

材料探索には **Materials Project MCP** または **OPTIMADE MCP** で候補材料を検索し、**GPAW MCP** で DFT 計算を実行し、結果を **Jupyter MCP** で解析する流れが自然である。mcp.science プロジェクトはこれらすべてを単一のモノレポで提供しており、`uvx mcp-science <server-name>` で統一的にインストールできる。

---

## 成熟度とメンテナンス状況の評価

| プロジェクト | スター数 | 最終更新 | 成熟度評価 |
|------------|---------|---------|-----------|
| **BioMCP**（genomoncology） | **466** | アクティブ（2025-2026） | ★★★★★ 本番利用可、CLI + MCP + Docker |
| **mcp.science** | **112** | アクティブ（2025-2026） | ★★★★☆ 科学計算に特化、良好なドキュメント |
| **ChEMBL MCP**（Augmented Nature） | **77** | 2025年7月 | ★★★★☆ 創薬特化、22ツール |
| **BioContextAI** | ~15 | アクティブ | ★★★★☆ Nature Biotechnology 掲載 |
| **PDB MCP** | **21** | 2025年 | ★★★☆☆ 安定動作 |
| **Reactome MCP** | **10** | 2025年 | ★★★☆☆ 安定動作 |
| **Open Targets MCP**（公式） | — | アクティブ | ★★★★☆ 公式提供、リモートサーバーあり |
| **paper-search-mcp** | — | アクティブ | ★★★★☆ Docker Hub 公式イメージ |

エコシステム全体として、大半のサーバーは **2025年に登場した比較的新しいプロジェクト** であり、スター数は一桁〜数十が多い。しかし BioMCP（466スター）や mcp.science（112スター）のように一定の利用者基盤を確立しているものもある。BioContextAI が Nature Biotechnology に掲載された事実は、学術コミュニティでの認知度向上を示す重要な指標である。

---

## Conclusion

科学研究向け MCP エコシステムは2025年に爆発的に成長し、特に **生命科学・創薬領域では主要データベースのほぼすべてに MCP サーバー経由でアクセスできる** 段階に達した。Augmented Nature の19サーバー群、BioMCP の統合アプローチ、bio-mcp のCLIツールラッパーという3つの異なるアーキテクチャが共存し、研究者は用途に応じて選択できる。

物理学・材料科学はまだ発展途上だが、mcp.science の Materials Project・GPAW サーバーや OPTIMADE MCP が基盤を築いている。VASPilot のような MCP ベースのマルチエージェント DFT ワークフロー自動化は、今後の計算物理学における AI 活用の方向性を示唆している。

最も実用的な導入方法は、まず **BioMCP**（生命科学統合）または **mcp.science**（物理・材料科学）をベースとして導入し、不足する機能を Augmented Nature の個別サーバーや paper-search-mcp で補完するアプローチである。コード実行環境として **jupyter-mcp-server** を加えることで、データ取得から解析・可視化までの一貫したAI支援研究ワークフローが構築できる。