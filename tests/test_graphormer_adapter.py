from __future__ import annotations

import subprocess
import sys

import pytest

from orbital_sci_mcp.adapters.graphormer import GraphormerAdapter
from orbital_sci_mcp.errors import ToolExecutionException
from orbital_sci_mcp.models import ExecutionContext


def _ctx(**overrides) -> ExecutionContext:
    defaults = {
        "request_id": "req-g",
        "tool_name": "graphormer_predict_property",
        "transport": "stdio",
        "timeout_seconds": 600,
    }
    defaults.update(overrides)
    return ExecutionContext(**defaults)


# --- UNSUPPORTED_OPERATION: no inference_options ---


def test_rejects_empty_inference_options() -> None:
    adapter = GraphormerAdapter()
    validated = adapter.validate_input({"smiles": "CCO"})

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx())

    assert exc_info.value.error.code == "UNSUPPORTED_OPERATION"
    assert "fairseq" in exc_info.value.error.message.lower()


# --- INPUT_VALIDATION_FAILED: missing required keys ---


def test_missing_required_inference_options() -> None:
    adapter = GraphormerAdapter()
    validated = adapter.validate_input(
        {
            "smiles": "CCO",
            "inference_options": {
                "graphormer_repo_path": "/tmp/fake",
            },
        }
    )

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx())

    err = exc_info.value.error
    assert err.code == "INPUT_VALIDATION_FAILED"
    assert set(err.details["missing_inference_options"]) == {
        "dataset_name",
        "dataset_source",
        "pretrained_model_name",
    }


# --- INPUT_VALIDATION_FAILED: repo path does not exist ---


def test_nonexistent_repo_path() -> None:
    adapter = GraphormerAdapter()
    validated = adapter.validate_input(
        {
            "smiles": "CCO",
            "inference_options": {
                "graphormer_repo_path": "/nonexistent/path/to/graphormer",
                "dataset_name": "pcqm4m",
                "dataset_source": "ogb",
                "pretrained_model_name": "pcqm4mv1_graphormer_base",
            },
        }
    )

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx())

    err = exc_info.value.error
    assert err.code == "INPUT_VALIDATION_FAILED"
    assert "graphormer_repo_path" in err.details


# --- UNSUPPORTED_OPERATION: evaluate.py missing from checkout ---


def test_evaluate_script_missing(tmp_path) -> None:
    adapter = GraphormerAdapter()
    validated = adapter.validate_input(
        {
            "smiles": "CCO",
            "inference_options": {
                "graphormer_repo_path": str(tmp_path),
                "dataset_name": "pcqm4m",
                "dataset_source": "ogb",
                "pretrained_model_name": "pcqm4mv1_graphormer_base",
            },
        }
    )

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx())

    err = exc_info.value.error
    assert err.code == "UNSUPPORTED_OPERATION"
    assert "evaluate.py" in err.message


# --- EXECUTION_FAILED: subprocess returns non-zero ---


def test_execution_failed_details(tmp_path, monkeypatch) -> None:
    evaluate_script = tmp_path / "graphormer" / "evaluate" / "evaluate.py"
    evaluate_script.parent.mkdir(parents=True)
    evaluate_script.write_text("import sys; sys.exit(42)\n", encoding="utf-8")

    monkeypatch.setattr("orbital_sci_mcp.adapters.graphormer.importlib.import_module", lambda name: None)

    def fake_run(command, cwd, capture_output, text, timeout, check):
        return subprocess.CompletedProcess(command, 42, stdout="partial output", stderr="some error")

    monkeypatch.setattr("orbital_sci_mcp.adapters.graphormer.subprocess.run", fake_run)

    adapter = GraphormerAdapter()
    validated = adapter.validate_input(
        {
            "smiles": "CCO",
            "inference_options": {
                "graphormer_repo_path": str(tmp_path),
                "dataset_name": "pcqm4m",
                "dataset_source": "ogb",
                "pretrained_model_name": "pcqm4mv1_graphormer_base",
            },
        }
    )

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx())

    err = exc_info.value.error
    assert err.code == "EXECUTION_FAILED"
    assert err.details["returncode"] == 42
    assert err.details["stdout"] == "partial output"
    assert err.details["stderr"] == "some error"
    assert isinstance(err.details["command"], list)


# --- success path: command construction ---


def test_success_returns_fairseq_evaluate_result(tmp_path, monkeypatch) -> None:
    evaluate_script = tmp_path / "graphormer" / "evaluate" / "evaluate.py"
    evaluate_script.parent.mkdir(parents=True)
    evaluate_script.write_text("print('ok')\n", encoding="utf-8")

    monkeypatch.setattr("orbital_sci_mcp.adapters.graphormer.importlib.import_module", lambda name: None)

    captured: dict[str, object] = {}

    def fake_run(command, cwd, capture_output, text, timeout, check):
        captured["command"] = command
        captured["cwd"] = cwd
        captured["timeout"] = timeout
        return subprocess.CompletedProcess(command, 0, stdout="metric: 0.123", stderr="")

    monkeypatch.setattr("orbital_sci_mcp.adapters.graphormer.subprocess.run", fake_run)

    adapter = GraphormerAdapter()
    validated = adapter.validate_input(
        {
            "smiles": "CCO",
            "inference_options": {
                "graphormer_repo_path": str(tmp_path),
                "dataset_name": "pcqm4m",
                "dataset_source": "ogb",
                "pretrained_model_name": "pcqm4mv1_graphormer_base",
                "criterion": "l1_loss",
                "num_workers": 4,
                "save_dir": str(tmp_path / "output"),
            },
        }
    )

    ctx = _ctx(timeout_seconds=999)
    result = adapter.execute(validated, ctx)

    assert result["mode"] == "fairseq_evaluate"
    assert result["returncode"] == 0
    assert result["stdout"] == "metric: 0.123"
    assert captured["cwd"] == str(tmp_path)
    assert captured["timeout"] == 999

    cmd = captured["command"]
    assert cmd[0] == sys.executable
    assert str(evaluate_script) in cmd
    assert "--dataset-name" in cmd
    assert cmd[cmd.index("--dataset-name") + 1] == "pcqm4m"
    assert "--criterion" in cmd
    assert cmd[cmd.index("--criterion") + 1] == "l1_loss"
    assert "--num-workers" in cmd
    assert cmd[cmd.index("--num-workers") + 1] == "4"
    assert "--save-dir" in cmd
    assert "--load-pretrained-model-output-layer" in cmd
