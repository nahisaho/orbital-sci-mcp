# orbital-sci-mcp

English | [日本語](README_ja.md)

orbital-sci-mcp is a Model Context Protocol (MCP) server that connects AI agents to AI for Science tool workflows offered in the Microsoft Foundry ecosystem.

The server provides a unified MCP interface for materials science, molecular modeling, and protein science workflows, while handling backend differences through adapters.

## What This Server Is For

- Expose Foundry-oriented AI for Science workflows through MCP tools.
- Let MCP clients discover tools and execute them with a consistent schema.
- Support both lightweight discovery mode and full per-tool publishing mode.
- Keep optional scientific dependencies isolated so the server can still start in limited environments.

## Implemented Tool Set

Current registry includes 9 scientific tools across 3 domains.

### Materials

- mattersim_predict_energy
- mattersim_relax_structure
- mattergen_generate_material
- mace_predict_energy
- mace_calculate_forces

### Molecules

- graphormer_predict_property (fairseq evaluate workflow launcher)
- dig_sample_conformations (protein_ligand_single_datapoint, protein_system_sampling, property_guided_sampling)
- dig_predict_equilibrium (catalyst_adsorption_density)

### Proteins

- bioemu_sample_ensemble (GPU-required)

## Build and Install

### 1) Requirements

- Python 3.11+
- pip

### 2) Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 3) Install in editable mode (recommended for development)

```bash
pip install -e .[dev]
```

Optional domain extras:

```bash
pip install -e .[dev,materials]
pip install -e .[dev,molecules]
pip install -e .[dev,proteins]
```

Or install all optional domains:

```bash
pip install -e .[dev,materials,molecules,proteins]
```

### 4) Build a distribution package (optional)

```bash
python -m pip install --upgrade build
python -m build
```

Install from built wheel:

```bash
pip install dist/*.whl
```

## Run the MCP Server

CLI entrypoint:

```bash
orbital-sci-mcp --transport stdio
```

### Common run modes

Run over stdio:

```bash
orbital-sci-mcp --transport stdio
```

Run in compact mode (discovery tools + execute_tool):

```bash
orbital-sci-mcp --transport stdio --compact-mode
```

Run over HTTP (streamable-http):

```bash
orbital-sci-mcp --transport http --host 127.0.0.1 --port 7000
```

Filter domains:

```bash
orbital-sci-mcp --enable-domain materials --enable-domain proteins
```

Filter tools:

```bash
orbital-sci-mcp --enable-tool mattersim_predict_energy --disable-tool bioemu_sample_ensemble
```

## Configuration via Environment Variables

- ORBITAL_SCI_MCP_TRANSPORT
- ORBITAL_SCI_MCP_HOST
- ORBITAL_SCI_MCP_PORT
- ORBITAL_SCI_MCP_LOG_LEVEL
- ORBITAL_SCI_MCP_COMPACT_MODE
- ORBITAL_SCI_MCP_ENABLED_DOMAINS (CSV)
- ORBITAL_SCI_MCP_ENABLED_TOOLS (CSV)
- ORBITAL_SCI_MCP_DISABLED_TOOLS (CSV)
- ORBITAL_SCI_MCP_DEFAULT_TIMEOUT

Example:

```bash
export ORBITAL_SCI_MCP_ENABLED_DOMAINS=materials,proteins
export ORBITAL_SCI_MCP_DISABLED_TOOLS=bioemu_sample_ensemble
```

## MCP Surface

### Discovery tools (always registered)

- list_tools
- get_tool_info
- search_tools
- execute_tool

### Publishing behavior

- compact mode: only discovery tools are top-level MCP tools.
- normal mode: discovery tools + each scientific tool are registered as MCP tools.

## Quick Client Example (stdio)

```json
{
  "command": "orbital-sci-mcp",
  "args": ["--transport", "stdio", "--compact-mode"]
}
```

## Testing

Run unit/smoke tests:

```bash
pytest -q
```

Graphormer and DiG integration tests are opt-in.

Prepare environment variables:

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

## Notes and Limitations

- graphormer_predict_property launches the upstream fairseq evaluate workflow, not interactive single-SMILES inference.
- DiG support is workflow-oriented and script-driven, not a generic one-shot molecular API.
- Some tools require GPU and/or local upstream repositories and artifacts.
- In dependency-missing environments, discovery still works while execution may return structured availability errors.

## Related Docs

- dev/ai4science-mcp-requirements.md
- dev/ai4science-mcp-design.md
- dev/graphormer-dig-operations-guide.md
- dev/graphormer-fairseq-evaluate-guide.md
- dev/dig-protein-ligand-guide.md
- dev/examples/
