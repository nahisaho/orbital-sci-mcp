from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import BaseModel

from ..errors import StructuredToolError, ToolExecutionException, unsupported_operation
from ..models import ExecutionContext
from ..schemas.molecules import MoleculeInput
from .base import BaseAdapter


class DigAdapter(BaseAdapter):
    package_names = []
    backend_name = "dig"
    _SUPPORTED_WORKFLOWS = [
        "protein_ligand_single_datapoint",
        "protein_system_sampling",
        "property_guided_sampling",
    ]
    _SUPPORTED_EQUILIBRIUM_WORKFLOWS = ["catalyst_adsorption_density"]

    def validate_input(self, payload: dict) -> BaseModel:
        return MoleculeInput.model_validate(payload)

    def execute(self, validated_input: BaseModel, context: ExecutionContext) -> dict:
        payload = validated_input.model_dump()
        options = payload.get("inference_options") or {}
        requested_workflows = self._supported_workflows_for_tool(context.tool_name)
        if not options:
            raise ToolExecutionException(
                unsupported_operation(
                    "DiG upstream is organized as task-specific sampling workflows rather than a generic SMILES inference API.",
                    details={
                        "tool_name": context.tool_name,
                        "supported_workflows": requested_workflows,
                        "required_inference_options": ["graphormer_repo_path", "dig_workflow", "pdbid"],
                    },
                )
            )

        workflow = options.get("dig_workflow", requested_workflows[0])
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

        if workflow == "protein_ligand_single_datapoint" and context.tool_name == "dig_sample_conformations":
            return self._run_protein_ligand_workflow(payload, options, repo_path, context)
        if workflow == "protein_system_sampling" and context.tool_name == "dig_sample_conformations":
            return self._run_protein_system_workflow(payload, options, repo_path, context)
        if workflow == "property_guided_sampling" and context.tool_name == "dig_sample_conformations":
            return self._run_property_guided_workflow(options, repo_path, context)
        if workflow == "catalyst_adsorption_density" and context.tool_name == "dig_predict_equilibrium":
            return self._run_catalyst_adsorption_density_workflow(options, repo_path, context)

        raise ToolExecutionException(
            unsupported_operation(
                "The requested DiG workflow is not implemented.",
                details={
                    "tool_name": context.tool_name,
                    "requested_workflow": workflow,
                    "supported_workflows": requested_workflows,
                },
            )
        )

    def _supported_workflows_for_tool(self, tool_name: str) -> list[str]:
        if tool_name == "dig_predict_equilibrium":
            return self._SUPPORTED_EQUILIBRIUM_WORKFLOWS
        return self._SUPPORTED_WORKFLOWS

    def _run_protein_ligand_workflow(
        self,
        payload: dict,
        options: dict,
        repo_path: Path,
        context: ExecutionContext,
    ) -> dict:

        workflow_root = repo_path / "distributional_graphormer" / "protein-ligand"
        sampling_script = workflow_root / "evaluation" / "single_datapoint_sampling.sh"
        if not sampling_script.exists():
            raise ToolExecutionException(
                StructuredToolError(
                    code="UNSUPPORTED_OPERATION",
                    message="DiG protein-ligand sampling script was not found in the provided repository path.",
                    details={"sampling_script": str(sampling_script)},
                    remediation=(
                        "Point graphormer_repo_path at a Graphormer checkout that contains "
                        "distributional_graphormer/protein-ligand/evaluation/single_datapoint_sampling.sh."
                    ),
                    retryable=False,
                )
            )

        pdbid = options.get("pdbid")
        if not pdbid:
            raise ToolExecutionException(
                StructuredToolError(
                    code="INPUT_VALIDATION_FAILED",
                    message="pdbid is required for the DiG protein-ligand sampling workflow.",
                    details={"required_inference_options": ["pdbid"]},
                    remediation="Provide a dataset pdbid that exists in distributional_graphormer/protein-ligand/src/dataset/all_md.list.",
                    retryable=False,
                )
            )

        sample_count = int(options.get("sample_count", payload.get("conformer_count") or 1))
        if sample_count <= 0:
            raise ToolExecutionException(
                StructuredToolError(
                    code="INPUT_VALIDATION_FAILED",
                    message="sample_count must be a positive integer.",
                    details={"sample_count": sample_count},
                    remediation="Provide sample_count >= 1 or set conformer_count to a positive integer.",
                    retryable=False,
                )
            )

        command = ["bash", str(sampling_script), "--pdbid", str(pdbid), "--number", str(sample_count)]
        completed = subprocess.run(
            command,
            cwd=str(workflow_root),
            capture_output=True,
            text=True,
            timeout=context.timeout_seconds,
            check=False,
        )
        if completed.returncode != 0:
            raise ToolExecutionException(
                StructuredToolError(
                    code="EXECUTION_FAILED",
                    message="DiG protein-ligand sampling command failed.",
                    details={
                        "returncode": completed.returncode,
                        "stdout": completed.stdout,
                        "stderr": completed.stderr,
                        "command": command,
                    },
                    remediation="Check the DiG environment, dataset extraction, checkpoint placement, and pdbid value.",
                    retryable=False,
                )
            )

        return {
            "mode": "protein_ligand_single_datapoint",
            "command": command,
            "returncode": completed.returncode,
            "pdbid": str(pdbid),
            "sample_count": sample_count,
            "output_dir": str(workflow_root / "src" / "output"),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    def _run_protein_system_workflow(
        self,
        payload: dict,
        options: dict,
        repo_path: Path,
        context: ExecutionContext,
    ) -> dict:
        workflow_root = repo_path / "distributional_graphormer" / "protein"
        inference_script = workflow_root / "run_inference.py"
        if not inference_script.exists():
            raise ToolExecutionException(
                StructuredToolError(
                    code="UNSUPPORTED_OPERATION",
                    message="DiG protein system inference script was not found in the provided repository path.",
                    details={"inference_script": str(inference_script)},
                    remediation=(
                        "Point graphormer_repo_path at a Graphormer checkout that contains "
                        "distributional_graphormer/protein/run_inference.py."
                    ),
                    retryable=False,
                )
            )

        pdbid = options.get("pdbid")
        if not pdbid:
            raise ToolExecutionException(
                StructuredToolError(
                    code="INPUT_VALIDATION_FAILED",
                    message="pdbid is required for the DiG protein system workflow.",
                    details={"required_inference_options": ["pdbid"]},
                    remediation="Provide a dataset pdbid that has matching .pkl and .fasta files in distributional_graphormer/protein/dataset.",
                    retryable=False,
                )
            )

        sample_count = int(options.get("sample_count", payload.get("conformer_count") or 1))
        if sample_count <= 0:
            raise ToolExecutionException(
                StructuredToolError(
                    code="INPUT_VALIDATION_FAILED",
                    message="sample_count must be a positive integer.",
                    details={"sample_count": sample_count},
                    remediation="Provide sample_count >= 1 or set conformer_count to a positive integer.",
                    retryable=False,
                )
            )

        checkpoint_path = Path(
            options.get("checkpoint_path") or (workflow_root / "checkpoints" / "checkpoint-520k.pth")
        )
        feature_path = Path(options.get("feature_path") or (workflow_root / "dataset" / f"{pdbid}.pkl"))
        fasta_path = Path(options.get("fasta_path") or (workflow_root / "dataset" / f"{pdbid}.fasta"))
        output_prefix = Path(options.get("output_prefix") or (workflow_root / "output"))

        command = [
            "python",
            str(inference_script),
            "-c",
            str(checkpoint_path),
            "-i",
            str(feature_path),
            "-s",
            str(fasta_path),
            "-o",
            str(pdbid),
            "--output-prefix",
            str(output_prefix),
            "-n",
            str(sample_count),
        ]
        if options.get("use_gpu", True):
            command.append("--use-gpu")
        if options.get("use_tqdm", True):
            command.append("--use-tqdm")

        completed = subprocess.run(
            command,
            cwd=str(workflow_root),
            capture_output=True,
            text=True,
            timeout=context.timeout_seconds,
            check=False,
        )
        if completed.returncode != 0:
            raise ToolExecutionException(
                StructuredToolError(
                    code="EXECUTION_FAILED",
                    message="DiG protein system sampling command failed.",
                    details={
                        "returncode": completed.returncode,
                        "stdout": completed.stdout,
                        "stderr": completed.stderr,
                        "command": command,
                    },
                    remediation="Check the DiG environment, protein dataset files, checkpoint path, and pdbid value.",
                    retryable=False,
                )
            )

        return {
            "mode": "protein_system_sampling",
            "command": command,
            "returncode": completed.returncode,
            "pdbid": str(pdbid),
            "sample_count": sample_count,
            "checkpoint_path": str(checkpoint_path),
            "feature_path": str(feature_path),
            "fasta_path": str(fasta_path),
            "output_dir": str(output_prefix),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    def _run_property_guided_workflow(
        self,
        options: dict,
        repo_path: Path,
        context: ExecutionContext,
    ) -> dict:
        workflow_root = repo_path / "distributional_graphormer" / "property-guided"
        sample_script = workflow_root / "scripts" / "sample.sh"
        if not sample_script.exists():
            raise ToolExecutionException(
                StructuredToolError(
                    code="UNSUPPORTED_OPERATION",
                    message="DiG property-guided sampling script was not found in the provided repository path.",
                    details={"sample_script": str(sample_script)},
                    remediation=(
                        "Point graphormer_repo_path at a Graphormer checkout that contains "
                        "distributional_graphormer/property-guided/scripts/sample.sh."
                    ),
                    retryable=False,
                )
            )

        missing = [
            key
            for key in ["num_gpus", "batch_size_per_gpu", "num_atoms", "target_bandgap"]
            if options.get(key) in {None, ""}
        ]
        if missing:
            raise ToolExecutionException(
                StructuredToolError(
                    code="INPUT_VALIDATION_FAILED",
                    message="Required inference options are missing for the DiG property-guided workflow.",
                    details={"missing_inference_options": missing},
                    remediation="Provide num_gpus, batch_size_per_gpu, num_atoms, and target_bandgap in inference_options.",
                    retryable=False,
                )
            )

        num_gpus = int(options["num_gpus"])
        batch_size_per_gpu = int(options["batch_size_per_gpu"])
        num_atoms = int(options["num_atoms"])
        target_bandgap = float(options["target_bandgap"])
        save_dir = str(options.get("save_dir") or (workflow_root / "output" / "property-guided"))

        command = [
            "bash",
            str(sample_script),
            str(num_gpus),
            str(batch_size_per_gpu),
            save_dir,
            str(num_atoms),
            str(target_bandgap),
        ]
        completed = subprocess.run(
            command,
            cwd=str(workflow_root),
            capture_output=True,
            text=True,
            timeout=context.timeout_seconds,
            check=False,
        )
        if completed.returncode != 0:
            raise ToolExecutionException(
                StructuredToolError(
                    code="EXECUTION_FAILED",
                    message="DiG property-guided sampling command failed.",
                    details={
                        "returncode": completed.returncode,
                        "stdout": completed.stdout,
                        "stderr": completed.stderr,
                        "command": command,
                    },
                    remediation="Check the DiG environment, property-guided dataset, checkpoint placement, and sampling arguments.",
                    retryable=False,
                )
            )

        return {
            "mode": "property_guided_sampling",
            "command": command,
            "returncode": completed.returncode,
            "num_gpus": num_gpus,
            "batch_size_per_gpu": batch_size_per_gpu,
            "num_atoms": num_atoms,
            "target_bandgap": target_bandgap,
            "save_dir": save_dir,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    def _run_catalyst_adsorption_density_workflow(
        self,
        options: dict,
        repo_path: Path,
        context: ExecutionContext,
    ) -> dict:
        workflow_root = repo_path / "distributional_graphormer" / "catalyst-adsorption"
        density_script = workflow_root / "scripts" / "density.sh"
        if not density_script.exists():
            raise ToolExecutionException(
                StructuredToolError(
                    code="UNSUPPORTED_OPERATION",
                    message="DiG catalyst-adsorption density script was not found in the provided repository path.",
                    details={"density_script": str(density_script)},
                    remediation=(
                        "Point graphormer_repo_path at a Graphormer checkout that contains "
                        "distributional_graphormer/catalyst-adsorption/scripts/density.sh."
                    ),
                    retryable=False,
                )
            )

        num_gpus = int(options.get("num_gpus", 1))
        batch_size_per_gpu = int(options.get("batch_size_per_gpu", 1))
        save_dir = str(options.get("save_dir") or (workflow_root / "output" / "density"))
        raw_height_indices = options.get("height_indices")
        if raw_height_indices is None:
            height_indices = list(range(11))
        else:
            height_indices = [int(value) for value in raw_height_indices]
        if not height_indices:
            raise ToolExecutionException(
                StructuredToolError(
                    code="INPUT_VALIDATION_FAILED",
                    message="height_indices must contain at least one height index.",
                    details={"height_indices": raw_height_indices},
                    remediation="Provide one or more integer height indices, for example [0, 1, 2].",
                    retryable=False,
                )
            )

        results = []
        for height_index in height_indices:
            command = [
                "bash",
                str(density_script),
                str(num_gpus),
                str(batch_size_per_gpu),
                save_dir,
                str(height_index),
            ]
            completed = subprocess.run(
                command,
                cwd=str(workflow_root),
                capture_output=True,
                text=True,
                timeout=context.timeout_seconds,
                check=False,
            )
            if completed.returncode != 0:
                raise ToolExecutionException(
                    StructuredToolError(
                        code="EXECUTION_FAILED",
                        message="DiG catalyst-adsorption density command failed.",
                        details={
                            "returncode": completed.returncode,
                            "stdout": completed.stdout,
                            "stderr": completed.stderr,
                            "command": command,
                            "height_index": height_index,
                        },
                        remediation="Check the DiG environment, catalyst-adsorption dataset, checkpoint placement, and density script prerequisites.",
                        retryable=False,
                    )
                )
            results.append(
                {
                    "height_index": height_index,
                    "command": command,
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }
            )

        successful_runs = sum(1 for run in results if run["returncode"] == 0)
        failed_runs = len(results) - successful_runs

        return {
            "mode": "catalyst_adsorption_density",
            "num_gpus": num_gpus,
            "batch_size_per_gpu": batch_size_per_gpu,
            "save_dir": save_dir,
            "height_indices": height_indices,
            "summary": {
                "requested_height_count": len(height_indices),
                "completed_height_count": len(results),
                "successful_height_count": successful_runs,
                "failed_height_count": failed_runs,
                "last_completed_height_index": results[-1]["height_index"] if results else None,
            },
            "runs": results,
        }
