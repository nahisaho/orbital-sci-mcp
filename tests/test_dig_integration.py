"""DiG integration tests.

When the corresponding DIG_*_RUN_INTEGRATION env vars are set and a local
Graphormer checkout is available, tests run against the real infrastructure.

Otherwise, the full ExecutionService → DigAdapter → subprocess pipeline is
exercised with a mocked subprocess and a temporary fake checkout.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from orbital_sci_mcp.execution import ExecutionService
from orbital_sci_mcp.registry import create_default_registry


# ---------------------------------------------------------------------------
# Env helpers – return options dict when real env is available, else None
# ---------------------------------------------------------------------------


def _dig_integration_env() -> dict[str, str] | None:
    required = {
        "graphormer_repo_path": os.getenv("DIG_REPO_PATH", ""),
        "dig_workflow": os.getenv("DIG_WORKFLOW", ""),
        "pdbid": os.getenv("DIG_PDBID", ""),
    }
    if not os.getenv("DIG_RUN_INTEGRATION"):
        return None
    if not all(required.values()):
        return None
    repo_path = Path(required["graphormer_repo_path"]).expanduser().resolve()
    sampling_script = (
        repo_path
        / "distributional_graphormer"
        / "protein-ligand"
        / "evaluation"
        / "single_datapoint_sampling.sh"
    )
    if not sampling_script.exists():
        return None
    return required


def _dig_protein_integration_env() -> dict[str, str] | None:
    required = {
        "graphormer_repo_path": os.getenv("DIG_PROTEIN_REPO_PATH", ""),
        "dig_workflow": "protein_system_sampling",
        "pdbid": os.getenv("DIG_PROTEIN_PDBID", ""),
    }
    if not os.getenv("DIG_PROTEIN_RUN_INTEGRATION"):
        return None
    if not all(required.values()):
        return None
    repo_path = Path(required["graphormer_repo_path"]).expanduser().resolve()
    inference_script = repo_path / "distributional_graphormer" / "protein" / "run_inference.py"
    if not inference_script.exists():
        return None
    return required


def _dig_equilibrium_integration_env() -> dict[str, str] | None:
    required = {
        "graphormer_repo_path": os.getenv("DIG_EQUILIBRIUM_REPO_PATH", ""),
        "dig_workflow": "catalyst_adsorption_density",
    }
    if not os.getenv("DIG_EQUILIBRIUM_RUN_INTEGRATION"):
        return None
    if not all(required.values()):
        return None
    repo_path = Path(required["graphormer_repo_path"]).expanduser().resolve()
    density_script = (
        repo_path
        / "distributional_graphormer"
        / "catalyst-adsorption"
        / "scripts"
        / "density.sh"
    )
    if not density_script.exists():
        return None
    return required


def _dig_property_integration_env() -> dict[str, str] | None:
    required = {
        "graphormer_repo_path": os.getenv("DIG_PROPERTY_REPO_PATH", ""),
        "dig_workflow": "property_guided_sampling",
        "num_gpus": os.getenv("DIG_PROPERTY_NUM_GPUS", ""),
        "batch_size_per_gpu": os.getenv("DIG_PROPERTY_BATCH_SIZE_PER_GPU", ""),
        "num_atoms": os.getenv("DIG_PROPERTY_NUM_ATOMS", ""),
        "target_bandgap": os.getenv("DIG_PROPERTY_TARGET_BANDGAP", ""),
    }
    if not os.getenv("DIG_PROPERTY_RUN_INTEGRATION"):
        return None
    if not all(required.values()):
        return None
    repo_path = Path(required["graphormer_repo_path"]).expanduser().resolve()
    sample_script = (
        repo_path
        / "distributional_graphormer"
        / "property-guided"
        / "scripts"
        / "sample.sh"
    )
    if not sample_script.exists():
        return None
    return required


# ---------------------------------------------------------------------------
# Helper: build fake checkout structure and mock subprocess
# ---------------------------------------------------------------------------


def _mock_subprocess(monkeypatch):
    def fake_run(command, cwd, capture_output, text, timeout, check):
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr("orbital_sci_mcp.adapters.dig.subprocess.run", fake_run)


def _setup_protein_ligand_fake(tmp_path):
    script = (
        tmp_path
        / "distributional_graphormer"
        / "protein-ligand"
        / "evaluation"
        / "single_datapoint_sampling.sh"
    )
    script.parent.mkdir(parents=True)
    script.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    return {
        "graphormer_repo_path": str(tmp_path),
        "dig_workflow": "protein_ligand_single_datapoint",
        "pdbid": "1a2k",
    }


def _setup_protein_system_fake(tmp_path):
    script = tmp_path / "distributional_graphormer" / "protein" / "run_inference.py"
    script.parent.mkdir(parents=True)
    script.write_text("print('ok')\n", encoding="utf-8")
    return {
        "graphormer_repo_path": str(tmp_path),
        "dig_workflow": "protein_system_sampling",
        "pdbid": "6lu7",
    }


def _setup_equilibrium_fake(tmp_path):
    script = (
        tmp_path
        / "distributional_graphormer"
        / "catalyst-adsorption"
        / "scripts"
        / "density.sh"
    )
    script.parent.mkdir(parents=True)
    script.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    return {
        "graphormer_repo_path": str(tmp_path),
        "dig_workflow": "catalyst_adsorption_density",
    }


def _setup_property_guided_fake(tmp_path):
    script = (
        tmp_path
        / "distributional_graphormer"
        / "property-guided"
        / "scripts"
        / "sample.sh"
    )
    script.parent.mkdir(parents=True)
    script.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    return {
        "graphormer_repo_path": str(tmp_path),
        "dig_workflow": "property_guided_sampling",
        "num_gpus": "1",
        "batch_size_per_gpu": "2",
        "num_atoms": "16",
        "target_bandgap": "1.5",
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_dig_protein_ligand_integration(tmp_path, monkeypatch) -> None:
    options = _dig_integration_env()
    use_real = options is not None

    if not use_real:
        options = _setup_protein_ligand_fake(tmp_path)
        _mock_subprocess(monkeypatch)

    registry = create_default_registry()
    service = ExecutionService(registry=registry, transport="stdio", default_timeout=1800)

    response = service.execute_tool(
        "dig_sample_conformations",
        {
            "conformer_count": int(os.getenv("DIG_SAMPLE_COUNT", "5")),
            "inference_options": {
                **options,
                "sample_count": int(os.getenv("DIG_SAMPLE_COUNT", "5")),
            },
        },
    )

    assert response.success is True, response.model_dump()
    assert response.data is not None
    assert response.data["mode"] == "protein_ligand_single_datapoint"
    assert response.data["returncode"] == 0
    assert response.data["pdbid"] == options["pdbid"]


@pytest.mark.integration
def test_dig_protein_system_integration(tmp_path, monkeypatch) -> None:
    options = _dig_protein_integration_env()
    use_real = options is not None

    if not use_real:
        options = _setup_protein_system_fake(tmp_path)
        _mock_subprocess(monkeypatch)

    registry = create_default_registry()
    service = ExecutionService(registry=registry, transport="stdio", default_timeout=1800)

    response = service.execute_tool(
        "dig_sample_conformations",
        {
            "conformer_count": int(os.getenv("DIG_PROTEIN_SAMPLE_COUNT", "3")),
            "inference_options": {
                **options,
                "sample_count": int(os.getenv("DIG_PROTEIN_SAMPLE_COUNT", "3")),
                "checkpoint_path": os.getenv("DIG_PROTEIN_CHECKPOINT_PATH") or None,
                "feature_path": os.getenv("DIG_PROTEIN_FEATURE_PATH") or None,
                "fasta_path": os.getenv("DIG_PROTEIN_FASTA_PATH") or None,
                "output_prefix": os.getenv("DIG_PROTEIN_OUTPUT_PREFIX") or None,
                "use_gpu": os.getenv("DIG_PROTEIN_USE_GPU", "1") in {"1", "true", "yes", "on"},
                "use_tqdm": os.getenv("DIG_PROTEIN_USE_TQDM", "1") in {"1", "true", "yes", "on"},
            },
        },
    )

    assert response.success is True, response.model_dump()
    assert response.data is not None
    assert response.data["mode"] == "protein_system_sampling"
    assert response.data["returncode"] == 0
    assert response.data["pdbid"] == options["pdbid"]


@pytest.mark.integration
def test_dig_equilibrium_integration(tmp_path, monkeypatch) -> None:
    options = _dig_equilibrium_integration_env()
    use_real = options is not None

    if not use_real:
        options = _setup_equilibrium_fake(tmp_path)
        _mock_subprocess(monkeypatch)

    registry = create_default_registry()
    service = ExecutionService(registry=registry, transport="stdio", default_timeout=1800)
    height_indices = [
        int(value)
        for value in os.getenv("DIG_EQUILIBRIUM_HEIGHT_INDICES", "0,1,2").split(",")
        if value.strip()
    ]

    response = service.execute_tool(
        "dig_predict_equilibrium",
        {
            "inference_options": {
                **options,
                "num_gpus": int(os.getenv("DIG_EQUILIBRIUM_NUM_GPUS", "1")),
                "batch_size_per_gpu": int(os.getenv("DIG_EQUILIBRIUM_BATCH_SIZE_PER_GPU", "2")),
                "save_dir": os.getenv("DIG_EQUILIBRIUM_SAVE_DIR") or None,
                "height_indices": height_indices,
            },
        },
    )

    assert response.success is True, response.model_dump()
    assert response.data is not None
    assert response.data["mode"] == "catalyst_adsorption_density"
    assert response.data["height_indices"] == height_indices
    assert response.data["summary"] == {
        "requested_height_count": len(height_indices),
        "completed_height_count": len(height_indices),
        "successful_height_count": len(height_indices),
        "failed_height_count": 0,
        "last_completed_height_index": height_indices[-1],
    }
    assert len(response.data["runs"]) == len(height_indices)
    assert all(run["returncode"] == 0 for run in response.data["runs"])


@pytest.mark.integration
def test_dig_property_guided_integration(tmp_path, monkeypatch) -> None:
    options = _dig_property_integration_env()
    use_real = options is not None

    if not use_real:
        options = _setup_property_guided_fake(tmp_path)
        _mock_subprocess(monkeypatch)

    registry = create_default_registry()
    service = ExecutionService(registry=registry, transport="stdio", default_timeout=1800)

    response = service.execute_tool(
        "dig_sample_conformations",
        {
            "inference_options": {
                **options,
                "save_dir": os.getenv("DIG_PROPERTY_SAVE_DIR") or None,
            },
        },
    )

    assert response.success is True, response.model_dump()
    assert response.data is not None
    assert response.data["mode"] == "property_guided_sampling"
    assert response.data["returncode"] == 0
    assert response.data["num_atoms"] == int(options["num_atoms"])
    assert response.data["target_bandgap"] == float(options["target_bandgap"])
