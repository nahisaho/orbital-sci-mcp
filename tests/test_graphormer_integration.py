from __future__ import annotations

import importlib.util
import os
import subprocess

import pytest

from orbital_sci_mcp.execution import ExecutionService
from orbital_sci_mcp.registry import create_default_registry


def _graphormer_integration_env() -> dict[str, str] | None:
    required = {
        "graphormer_repo_path": os.getenv("GRAPHORMER_REPO_PATH", ""),
        "dataset_name": os.getenv("GRAPHORMER_DATASET_NAME", ""),
        "dataset_source": os.getenv("GRAPHORMER_DATASET_SOURCE", ""),
        "pretrained_model_name": os.getenv("GRAPHORMER_PRETRAINED_MODEL_NAME", ""),
    }
    if not os.getenv("GRAPHORMER_RUN_INTEGRATION"):
        return None
    if not all(required.values()):
        return None
    if importlib.util.find_spec("fairseq") is None:
        return None
    return required


@pytest.mark.integration
def test_graphormer_fairseq_evaluate_integration(tmp_path, monkeypatch) -> None:
    options = _graphormer_integration_env()
    use_real = options is not None

    if not use_real:
        evaluate_script = tmp_path / "graphormer" / "evaluate" / "evaluate.py"
        evaluate_script.parent.mkdir(parents=True)
        evaluate_script.write_text("print('ok')\n", encoding="utf-8")

        options = {
            "graphormer_repo_path": str(tmp_path),
            "dataset_name": "pcqm4m",
            "dataset_source": "ogb",
            "pretrained_model_name": "pcqm4mv1_graphormer_base",
        }

        monkeypatch.setattr(
            "orbital_sci_mcp.adapters.graphormer.importlib.import_module",
            lambda name: None,
        )

        def fake_run(command, cwd, capture_output, text, timeout, check):
            return subprocess.CompletedProcess(
                command, 0, stdout="metric: 0.1234", stderr=""
            )

        monkeypatch.setattr(
            "orbital_sci_mcp.adapters.graphormer.subprocess.run", fake_run
        )

    registry = create_default_registry()

    if not use_real:
        from orbital_sci_mcp.models import AvailabilityResult

        original_create = registry.create_adapter

        def _patched_create(name):
            adapter = original_create(name)
            if name == "graphormer_predict_property":
                adapter.check_availability = lambda: AvailabilityResult(available=True, status="available")
            return adapter

        monkeypatch.setattr(registry, "create_adapter", _patched_create)
    service = ExecutionService(
        registry=registry, transport="stdio", default_timeout=1800
    )

    response = service.execute_tool(
        "graphormer_predict_property",
        {
            "smiles": "CCO",
            "inference_options": {
                **options,
                "task": os.getenv("GRAPHORMER_TASK", "graph_prediction"),
                "arch": os.getenv("GRAPHORMER_ARCH", "graphormer_base"),
                "num_classes": int(os.getenv("GRAPHORMER_NUM_CLASSES", "1")),
                "batch_size": int(os.getenv("GRAPHORMER_BATCH_SIZE", "64")),
                "split": os.getenv("GRAPHORMER_SPLIT", "valid"),
                "seed": int(os.getenv("GRAPHORMER_SEED", "1")),
                "num_workers": int(os.getenv("GRAPHORMER_NUM_WORKERS", "0")),
                "criterion": os.getenv("GRAPHORMER_CRITERION", "l1_loss"),
                "load_pretrained_model_output_layer": os.getenv(
                    "GRAPHORMER_LOAD_OUTPUT_LAYER", "1"
                )
                in {"1", "true", "yes", "on"},
                "metric": os.getenv("GRAPHORMER_METRIC") or None,
                "save_dir": os.getenv("GRAPHORMER_SAVE_DIR") or None,
            },
        },
    )

    assert response.success is True, response.model_dump()
    assert response.data is not None
    assert response.data["mode"] == "fairseq_evaluate"
    assert response.data["returncode"] == 0
