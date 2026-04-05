from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

from pydantic import BaseModel

from ..errors import ToolExecutionException, StructuredToolError, unsupported_operation
from ..models import ExecutionContext
from ..schemas.molecules import MoleculeInput
from .base import BaseAdapter


class GraphormerAdapter(BaseAdapter):
    package_names = ["fairseq"]
    backend_name = "graphormer"

    def validate_input(self, payload: dict) -> BaseModel:
        return MoleculeInput.model_validate(payload)

    def execute(self, validated_input: BaseModel, context: ExecutionContext) -> dict:
        payload = validated_input.model_dump()
        options = payload.get("inference_options") or {}
        if not options:
            raise ToolExecutionException(
                unsupported_operation(
                    "Graphormer upstream exposes evaluation primarily through fairseq-based CLI workflows, not an ad hoc SMILES prediction API.",
                    details={
                        "tool_name": context.tool_name,
                        "supported_mode": "fairseq_evaluate",
                        "required_inference_options": [
                            "graphormer_repo_path",
                            "dataset_name",
                            "dataset_source",
                            "pretrained_model_name",
                        ],
                    },
                )
            )

        missing = [
            key
            for key in ["graphormer_repo_path", "dataset_name", "dataset_source", "pretrained_model_name"]
            if options.get(key) in {None, ""}
        ]
        if missing:
            raise ToolExecutionException(
                StructuredToolError(
                    code="INPUT_VALIDATION_FAILED",
                    message="Required inference options are missing for the Graphormer fairseq evaluate workflow.",
                    details={"missing_inference_options": missing},
                    remediation=(
                        "Provide graphormer_repo_path, dataset_name, dataset_source, and "
                        "pretrained_model_name in inference_options."
                    ),
                    retryable=False,
                )
            )

        repo_path = Path(options.get("graphormer_repo_path", "")).expanduser().resolve()
        if not repo_path.exists():
            raise ToolExecutionException(
                StructuredToolError(
                    code="INPUT_VALIDATION_FAILED",
                    message="graphormer_repo_path does not exist.",
                    details={"graphormer_repo_path": str(repo_path)},
                    remediation="Provide a local checkout path for the Graphormer repository.",
                    retryable=False,
                )
            )

        evaluate_script = repo_path / "graphormer" / "evaluate" / "evaluate.py"
        user_dir = repo_path / "graphormer"
        if not evaluate_script.exists():
            raise ToolExecutionException(
                StructuredToolError(
                    code="UNSUPPORTED_OPERATION",
                    message="Graphormer evaluate.py was not found in the provided repository path.",
                    details={"evaluate_script": str(evaluate_script)},
                    remediation="Point graphormer_repo_path at a Graphormer checkout that contains graphormer/evaluate/evaluate.py.",
                    retryable=False,
                )
            )

        importlib.import_module("fairseq")

        command = [
            sys.executable,
            str(evaluate_script),
            "--user-dir",
            str(user_dir),
            "--dataset-name",
            options["dataset_name"],
            "--dataset-source",
            options["dataset_source"],
            "--task",
            options.get("task", "graph_prediction"),
            "--arch",
            options.get("arch", "graphormer_base"),
            "--num-classes",
            str(options.get("num_classes", 1)),
            "--batch-size",
            str(options.get("batch_size", 64)),
            "--pretrained-model-name",
            options["pretrained_model_name"],
            "--split",
            options.get("split", "valid"),
            "--seed",
            str(options.get("seed", 1)),
        ]
        if options.get("criterion"):
            command.extend(["--criterion", options["criterion"]])
        if options.get("num_workers") is not None:
            command.extend(["--num-workers", str(options["num_workers"])])
        if options.get("load_pretrained_model_output_layer", True):
            command.append("--load-pretrained-model-output-layer")
        if options.get("metric"):
            command.extend(["--metric", options["metric"]])
        if options.get("save_dir"):
            command.extend(["--save-dir", str(options["save_dir"])])

        completed = subprocess.run(
            command,
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=context.timeout_seconds,
            check=False,
        )
        if completed.returncode != 0:
            raise ToolExecutionException(
                StructuredToolError(
                    code="EXECUTION_FAILED",
                    message="Graphormer evaluation command failed.",
                    details={
                        "returncode": completed.returncode,
                        "stdout": completed.stdout,
                        "stderr": completed.stderr,
                        "command": command,
                    },
                    remediation="Check the Graphormer environment, dataset configuration, and pretrained model arguments.",
                    retryable=False,
                )
            )

        return {
            "mode": "fairseq_evaluate",
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
