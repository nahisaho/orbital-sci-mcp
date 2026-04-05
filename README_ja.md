# orbital-sci-mcp

[English](README.md) | 日本語

orbital-sci-mcp は、Microsoft Foundry エコシステムで提供される AI for Science 向けツールのワークフローと、AI エージェントをつなぐための Model Context Protocol (MCP) サーバーです。

材料科学、分子モデリング、タンパク質科学の処理を、アダプター構成で統一インターフェイス化して公開します。

## この MCP Server の役割

- Foundry 指向の AI for Science ワークフローを MCP ツールとして公開する
- クライアント側から同一形式でツール探索と実行を行えるようにする
- discovery 中心の軽量運用（compact mode）と通常運用を切り替えられるようにする
- 科学計算依存を optional に分離し、依存が欠ける環境でもサーバー起動を維持する

## 実装済みツール

現在は 3 ドメイン・9 ツールを登録しています。

### Materials

- mattersim_predict_energy
- mattersim_relax_structure
- mattergen_generate_material
- mace_predict_energy
- mace_calculate_forces

### Molecules

- graphormer_predict_property（fairseq evaluate workflow の起動）
- dig_sample_conformations（protein_ligand_single_datapoint / protein_system_sampling / property_guided_sampling）
- dig_predict_equilibrium（catalyst_adsorption_density）

### Proteins

- bioemu_sample_ensemble（GPU 必須）

## 対応している Microsoft AI Foundry AI for Science Tools

本サーバーが現在連携している Microsoft AI Foundry の AI for Science ツール系統は以下です。

| Foundry ツール系統 | 本サーバーで公開している MCP ツール | 現在の連携方式 |
|---|---|---|
| MatterSim | mattersim_predict_energy, mattersim_relax_structure | Python アダプター |
| MatterGen | mattergen_generate_material | Python アダプター |
| MACE | mace_predict_energy, mace_calculate_forces | Python アダプター |
| Graphormer | graphormer_predict_property | fairseq evaluate workflow 起動 |
| DiG (Distributional Graphormer) | dig_sample_conformations, dig_predict_equilibrium | task/workflow スクリプト起動 |
| BioEmu | bioemu_sample_ensemble | Python アダプター（GPU 必須） |

補足:

- 一部バックエンドはローカルのリポジトリ資材や GPU 実行環境を必要とします。
- ツール利用可否は実行時に判定され、MCP の構造化レスポンスとして返されます。

## ビルドとインストール

### 1) 前提

- Python 3.11 以上
- pip

### 2) 仮想環境作成

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 3) 開発向けインストール（推奨）

```bash
pip install -e .[dev]
```

ドメイン別 extras の例:

```bash
pip install -e .[dev,materials]
pip install -e .[dev,molecules]
pip install -e .[dev,proteins]
```

全ドメインをまとめて入れる場合:

```bash
pip install -e .[dev,materials,molecules,proteins]
```

### 4) 配布パッケージのビルド（任意）

```bash
python -m pip install --upgrade build
python -m build
```

生成済み wheel からインストール:

```bash
pip install dist/*.whl
```

## MCP Server 起動方法

CLI エントリポイント:

```bash
orbital-sci-mcp --transport stdio
```

### よく使う起動パターン

stdio で起動:

```bash
orbital-sci-mcp --transport stdio
```

compact mode で起動（discovery + execute_tool）:

```bash
orbital-sci-mcp --transport stdio --compact-mode
```

HTTP（streamable-http）で起動:

```bash
orbital-sci-mcp --transport http --host 127.0.0.1 --port 7000
```

ドメインを制限して起動:

```bash
orbital-sci-mcp --enable-domain materials --enable-domain proteins
```

個別ツールを制御:

```bash
orbital-sci-mcp --enable-tool mattersim_predict_energy --disable-tool bioemu_sample_ensemble
```

## 環境変数設定

- ORBITAL_SCI_MCP_TRANSPORT
- ORBITAL_SCI_MCP_HOST
- ORBITAL_SCI_MCP_PORT
- ORBITAL_SCI_MCP_LOG_LEVEL
- ORBITAL_SCI_MCP_COMPACT_MODE
- ORBITAL_SCI_MCP_ENABLED_DOMAINS（CSV）
- ORBITAL_SCI_MCP_ENABLED_TOOLS（CSV）
- ORBITAL_SCI_MCP_DISABLED_TOOLS（CSV）
- ORBITAL_SCI_MCP_DEFAULT_TIMEOUT

例:

```bash
export ORBITAL_SCI_MCP_ENABLED_DOMAINS=materials,proteins
export ORBITAL_SCI_MCP_DISABLED_TOOLS=bioemu_sample_ensemble
```

## MCP 公開面

### 常に公開される discovery ツール

- list_tools
- get_tool_info
- search_tools
- execute_tool

### 公開ルール

- compact mode: discovery ツールのみをトップレベル公開
- 通常モード: discovery ツール + 各科学ツールを公開

## クライアント設定例（stdio）

```json
{
  "command": "orbital-sci-mcp",
  "args": ["--transport", "stdio", "--compact-mode"]
}
```

## テスト

単体・スモークテスト:

```bash
pytest -q
```

Graphormer/DiG の integration test は opt-in です。

準備:

```bash
cp .env.example .env
set -a
source .env
set +a
```

Graphormer integration test:

```bash
PYTHONPATH=src pytest -q tests/test_graphormer_integration.py -m integration
```

DiG integration test:

```bash
PYTHONPATH=src pytest -q tests/test_dig_integration.py -m integration
```

## 制約と注意点

- graphormer_predict_property は単一 SMILES の対話推論ではなく、upstream の fairseq evaluate workflow を起動する方式です。
- DiG は汎用 1-shot API ではなく、workflow ごとのスクリプト起動方式です。
- 一部ツールは GPU やローカルの upstream リポジトリ／アーティファクトを必要とします。
- 依存不足環境では discovery は利用可能ですが、実行時は構造化された availability エラーが返る場合があります。

## 関連ドキュメント

- dev/ai4science-mcp-requirements.md
- dev/ai4science-mcp-design.md
- dev/graphormer-dig-operations-guide.md
- dev/graphormer-fairseq-evaluate-guide.md
- dev/dig-protein-ligand-guide.md
- dev/examples/
