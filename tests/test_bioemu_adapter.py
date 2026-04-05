from __future__ import annotations

import types
from pathlib import Path

import pytest

from orbital_sci_mcp.adapters.bioemu import BioEmuAdapter
from orbital_sci_mcp.errors import ToolExecutionException
from orbital_sci_mcp.models import ExecutionContext


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        request_id="req-be",
        tool_name="bioemu_sample_ensemble",
        transport="stdio",
        timeout_seconds=300,
    )


# --- INPUT_VALIDATION_FAILED: no sequence ---


def test_rejects_empty_sequence() -> None:
    adapter = BioEmuAdapter()
    validated = adapter.validate_input({})
    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx())
    assert exc_info.value.error.code == "INPUT_VALIDATION_FAILED"


# --- UNSUPPORTED_OPERATION: import fails ---


def test_import_failure(monkeypatch) -> None:
    adapter = BioEmuAdapter()
    validated = adapter.validate_input({"sequence": "MKTIIALSYIFCLVFA"})

    import builtins

    real_import = builtins.__import__

    def block_bioemu(name, *args, **kwargs):
        if "bioemu" in name:
            raise ImportError("no bioemu")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", block_bioemu)

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx())
    assert exc_info.value.error.code == "UNSUPPORTED_OPERATION"


# --- success: sample with temp dir ---


def test_sample_ensemble_success_tempdir(monkeypatch) -> None:
    adapter = BioEmuAdapter()
    validated = adapter.validate_input(
        {"sequence": "MKTIIALSYIFCLVFA", "sample_count": 3}
    )

    def fake_sample(**kwargs):
        output_dir = Path(kwargs["output_dir"])
        (output_dir / "topology.pdb").write_text("ATOM ...\n")
        (output_dir / "samples.xtc").write_bytes(b"\x00")
        (output_dir / "sequence.fasta").write_text(">seq\nMKTIIALSYIFCLVFA\n")

    _inject_fake_bioemu(monkeypatch, fake_sample)

    result = adapter.execute(validated, _ctx())
    assert result["requested_count"] == 3
    assert result["model_name"] == "bioemu-v1.1"
    assert result["artifacts"]["topology_pdb_exists"] is True
    assert result["artifacts"]["samples_xtc_exists"] is True
    assert result["artifacts"]["sequence_fasta_exists"] is True
    assert "output_dir" not in result


# --- success: sample with explicit output dir ---


def test_sample_ensemble_success_explicit_dir(monkeypatch, tmp_path) -> None:
    adapter = BioEmuAdapter()
    out = tmp_path / "bioemu-out"
    out.mkdir()
    validated = adapter.validate_input(
        {
            "sequence": "MKTIIALSYIFCLVFA",
            "sample_count": 1,
            "inference_options": {"output_dir": str(out)},
        }
    )

    def fake_sample(**kwargs):
        output_dir = Path(kwargs["output_dir"])
        (output_dir / "topology.pdb").write_text("ATOM ...\n")
        (output_dir / "samples.xtc").write_bytes(b"\x00")
        (output_dir / "sequence.fasta").write_text(">seq\nMKTIIALSYIFCLVFA\n")

    _inject_fake_bioemu(monkeypatch, fake_sample)

    result = adapter.execute(validated, _ctx())
    assert result["output_dir"] == str(out)
    assert result["topology_pdb"] is not None
    assert result["samples_xtc"] is not None
    assert result["sequence_fasta"] is not None


# --- success: fasta_text instead of sequence ---


def test_fasta_text_input(monkeypatch) -> None:
    adapter = BioEmuAdapter()
    validated = adapter.validate_input(
        {"fasta_text": ">test\nACDEFG", "sample_count": 1}
    )

    captured: dict = {}

    def fake_sample(**kwargs):
        captured["sequence"] = kwargs["sequence"]
        output_dir = Path(kwargs["output_dir"])
        (output_dir / "topology.pdb").write_text("")
        (output_dir / "samples.xtc").write_bytes(b"")
        (output_dir / "sequence.fasta").write_text("")

    _inject_fake_bioemu(monkeypatch, fake_sample)

    result = adapter.execute(validated, _ctx())
    assert captured["sequence"] == ">test\nACDEFG"
    assert result["requested_count"] == 1


# --- helper ---


def _inject_fake_bioemu(monkeypatch, fake_sample_fn):
    import builtins

    real_import = builtins.__import__

    def patched_import(name, *args, **kwargs):
        if name == "bioemu.sample":
            mod = types.ModuleType("bioemu.sample")
            mod.main = fake_sample_fn
            return mod
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", patched_import)
