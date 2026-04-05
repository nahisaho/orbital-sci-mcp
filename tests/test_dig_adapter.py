from __future__ import annotations

import subprocess

import pytest

from orbital_sci_mcp.adapters.dig import DigAdapter
from orbital_sci_mcp.errors import ToolExecutionException
from orbital_sci_mcp.models import ExecutionContext


def test_dig_adapter_runs_protein_ligand_sampling_command(tmp_path, monkeypatch) -> None:
    workflow_root = tmp_path / "distributional_graphormer" / "protein-ligand"
    script_path = workflow_root / "evaluation" / "single_datapoint_sampling.sh"
    script_path.parent.mkdir(parents=True)
    script_path.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_run(command, cwd, capture_output, text, timeout, check):
        captured["command"] = command
        captured["cwd"] = cwd
        captured["timeout"] = timeout
        captured["check"] = check
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr("orbital_sci_mcp.adapters.dig.subprocess.run", fake_run)

    adapter = DigAdapter()
    validated = adapter.validate_input(
        {
            "conformer_count": 12,
            "inference_options": {
                "graphormer_repo_path": str(tmp_path),
                "dig_workflow": "protein_ligand_single_datapoint",
                "pdbid": "1a2k",
            },
        }
    )

    result = adapter.execute(
        validated,
        ExecutionContext(
            request_id="req-1",
            tool_name="dig_sample_conformations",
            transport="stdio",
            timeout_seconds=321,
        ),
    )

    assert result["mode"] == "protein_ligand_single_datapoint"
    assert result["pdbid"] == "1a2k"
    assert result["sample_count"] == 12
    assert result["returncode"] == 0
    assert captured["cwd"] == str(workflow_root)
    assert captured["timeout"] == 321
    assert captured["check"] is False
    assert captured["command"] == [
        "bash",
        str(script_path),
        "--pdbid",
        "1a2k",
        "--number",
        "12",
    ]


def test_dig_adapter_runs_protein_system_sampling_command(tmp_path, monkeypatch) -> None:
    workflow_root = tmp_path / "distributional_graphormer" / "protein"
    inference_script = workflow_root / "run_inference.py"
    inference_script.parent.mkdir(parents=True)
    inference_script.write_text("print('ok')\n", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_run(command, cwd, capture_output, text, timeout, check):
        captured["command"] = command
        captured["cwd"] = cwd
        captured["timeout"] = timeout
        captured["check"] = check
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr("orbital_sci_mcp.adapters.dig.subprocess.run", fake_run)

    adapter = DigAdapter()
    validated = adapter.validate_input(
        {
            "conformer_count": 3,
            "inference_options": {
                "graphormer_repo_path": str(tmp_path),
                "dig_workflow": "protein_system_sampling",
                "pdbid": "6lu7",
            },
        }
    )

    result = adapter.execute(
        validated,
        ExecutionContext(
            request_id="req-3",
            tool_name="dig_sample_conformations",
            transport="stdio",
            timeout_seconds=654,
        ),
    )

    assert result["mode"] == "protein_system_sampling"
    assert result["pdbid"] == "6lu7"
    assert result["sample_count"] == 3
    assert result["returncode"] == 0
    assert captured["cwd"] == str(workflow_root)
    assert captured["timeout"] == 654
    assert captured["check"] is False
    assert captured["command"] == [
        "python",
        str(inference_script),
        "-c",
        str(workflow_root / "checkpoints" / "checkpoint-520k.pth"),
        "-i",
        str(workflow_root / "dataset" / "6lu7.pkl"),
        "-s",
        str(workflow_root / "dataset" / "6lu7.fasta"),
        "-o",
        "6lu7",
        "--output-prefix",
        str(workflow_root / "output"),
        "-n",
        "3",
        "--use-gpu",
        "--use-tqdm",
    ]


def test_dig_adapter_rejects_unknown_workflow(tmp_path) -> None:
    adapter = DigAdapter()
    validated = adapter.validate_input(
        {
            "inference_options": {
                "graphormer_repo_path": str(tmp_path),
                "dig_workflow": "unknown_workflow",
                "pdbid": "1a2k",
            },
        }
    )

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(
            validated,
            ExecutionContext(
                request_id="req-2",
                tool_name="dig_sample_conformations",
                transport="stdio",
            ),
        )

    assert exc_info.value.error.code == "UNSUPPORTED_OPERATION"


def test_dig_adapter_runs_catalyst_density_commands(tmp_path, monkeypatch) -> None:
    workflow_root = tmp_path / "distributional_graphormer" / "catalyst-adsorption"
    density_script = workflow_root / "scripts" / "density.sh"
    density_script.parent.mkdir(parents=True)
    density_script.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")

    calls: list[dict[str, object]] = []

    def fake_run(command, cwd, capture_output, text, timeout, check):
        calls.append(
            {
                "command": command,
                "cwd": cwd,
                "timeout": timeout,
                "check": check,
            }
        )
        return subprocess.CompletedProcess(command, 0, stdout="density-ok", stderr="")

    monkeypatch.setattr("orbital_sci_mcp.adapters.dig.subprocess.run", fake_run)

    adapter = DigAdapter()
    validated = adapter.validate_input(
        {
            "inference_options": {
                "graphormer_repo_path": str(tmp_path),
                "dig_workflow": "catalyst_adsorption_density",
                "num_gpus": 2,
                "batch_size_per_gpu": 4,
                "save_dir": str(workflow_root / "density-output"),
                "height_indices": [0, 2, 5],
            },
        }
    )

    result = adapter.execute(
        validated,
        ExecutionContext(
            request_id="req-4",
            tool_name="dig_predict_equilibrium",
            transport="stdio",
            timeout_seconds=222,
        ),
    )

    assert result["mode"] == "catalyst_adsorption_density"
    assert result["num_gpus"] == 2
    assert result["batch_size_per_gpu"] == 4
    assert result["height_indices"] == [0, 2, 5]
    assert result["summary"] == {
        "requested_height_count": 3,
        "completed_height_count": 3,
        "successful_height_count": 3,
        "failed_height_count": 0,
        "last_completed_height_index": 5,
    }
    assert len(result["runs"]) == 3
    assert [run["height_index"] for run in result["runs"]] == [0, 2, 5]
    assert all(call["cwd"] == str(workflow_root) for call in calls)
    assert all(call["timeout"] == 222 for call in calls)
    assert all(call["check"] is False for call in calls)
    assert calls[0]["command"] == [
        "bash",
        str(density_script),
        "2",
        "4",
        str(workflow_root / "density-output"),
        "0",
    ]


def test_dig_adapter_runs_property_guided_sampling_command(tmp_path, monkeypatch) -> None:
    workflow_root = tmp_path / "distributional_graphormer" / "property-guided"
    sample_script = workflow_root / "scripts" / "sample.sh"
    sample_script.parent.mkdir(parents=True)
    sample_script.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_run(command, cwd, capture_output, text, timeout, check):
        captured["command"] = command
        captured["cwd"] = cwd
        captured["timeout"] = timeout
        captured["check"] = check
        return subprocess.CompletedProcess(command, 0, stdout="property-ok", stderr="")

    monkeypatch.setattr("orbital_sci_mcp.adapters.dig.subprocess.run", fake_run)

    adapter = DigAdapter()
    validated = adapter.validate_input(
        {
            "inference_options": {
                "graphormer_repo_path": str(tmp_path),
                "dig_workflow": "property_guided_sampling",
                "num_gpus": 2,
                "batch_size_per_gpu": 4,
                "save_dir": str(workflow_root / "property-output"),
                "num_atoms": 16,
                "target_bandgap": 1.5,
            },
        }
    )

    result = adapter.execute(
        validated,
        ExecutionContext(
            request_id="req-5",
            tool_name="dig_sample_conformations",
            transport="stdio",
            timeout_seconds=333,
        ),
    )

    assert result["mode"] == "property_guided_sampling"
    assert result["num_gpus"] == 2
    assert result["batch_size_per_gpu"] == 4
    assert result["num_atoms"] == 16
    assert result["target_bandgap"] == 1.5
    assert result["returncode"] == 0
    assert captured["cwd"] == str(workflow_root)
    assert captured["timeout"] == 333
    assert captured["check"] is False
    assert captured["command"] == [
        "bash",
        str(sample_script),
        "2",
        "4",
        str(workflow_root / "property-output"),
        "16",
        "1.5",
    ]


def test_dig_adapter_rejects_empty_equilibrium_height_indices(tmp_path) -> None:
    workflow_root = tmp_path / "distributional_graphormer" / "catalyst-adsorption"
    density_script = workflow_root / "scripts" / "density.sh"
    density_script.parent.mkdir(parents=True)
    density_script.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")

    adapter = DigAdapter()
    validated = adapter.validate_input(
        {
            "inference_options": {
                "graphormer_repo_path": str(tmp_path),
                "dig_workflow": "catalyst_adsorption_density",
                "height_indices": [],
            },
        }
    )

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(
            validated,
            ExecutionContext(
                request_id="req-6",
                tool_name="dig_predict_equilibrium",
                transport="stdio",
                timeout_seconds=111,
            ),
        )

    assert exc_info.value.error.code == "INPUT_VALIDATION_FAILED"
    assert exc_info.value.error.details == {"height_indices": []}


def test_dig_adapter_reports_failed_equilibrium_height_index(tmp_path, monkeypatch) -> None:
    workflow_root = tmp_path / "distributional_graphormer" / "catalyst-adsorption"
    density_script = workflow_root / "scripts" / "density.sh"
    density_script.parent.mkdir(parents=True)
    density_script.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")

    def fake_run(command, cwd, capture_output, text, timeout, check):
        if command[-1] == "2":
            return subprocess.CompletedProcess(command, 17, stdout="partial", stderr="boom")
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr("orbital_sci_mcp.adapters.dig.subprocess.run", fake_run)

    adapter = DigAdapter()
    validated = adapter.validate_input(
        {
            "inference_options": {
                "graphormer_repo_path": str(tmp_path),
                "dig_workflow": "catalyst_adsorption_density",
                "num_gpus": 1,
                "batch_size_per_gpu": 2,
                "height_indices": [0, 2, 5],
            },
        }
    )

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(
            validated,
            ExecutionContext(
                request_id="req-7",
                tool_name="dig_predict_equilibrium",
                transport="stdio",
                timeout_seconds=222,
            ),
        )

    assert exc_info.value.error.code == "EXECUTION_FAILED"
    assert exc_info.value.error.details is not None
    assert exc_info.value.error.details["height_index"] == 2
    assert exc_info.value.error.details["returncode"] == 17

