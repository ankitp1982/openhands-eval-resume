"""Offline checks for the pinned SWE-bench resume boundary."""

import ast
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]


def test_output_layout_does_not_include_tool_preset() -> None:
    path = ROOT / "benchmarks/utils/evaluation_utils.py"
    tree = ast.parse(path.read_text())
    function = next(
        item
        for item in tree.body
        if isinstance(item, ast.FunctionDef)
        and item.name == "construct_eval_output_dir"
    )
    parameters = {arg.arg for arg in function.args.args}
    assert {"model_name", "max_iterations", "eval_note"} <= parameters
    assert "tool_preset" not in parameters


def load_contract() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "resume_contract", ROOT / "benchmarks/swebench/resume_contract.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manifest_accepts_same_settings_and_rejects_drift(tmp_path: Path) -> None:
    contract_module = load_contract()
    ensure_resume_contract = contract_module.ensure_resume_contract
    build_manifest = contract_module.build_manifest

    prompt = tmp_path / "prompt"
    prompt.write_text("Fix the issue.")
    output = tmp_path / "output"
    output.mkdir()
    arguments = {"prompt_path": str(prompt), "tool_preset": "default"}
    model = {"model": "fixture-model", "api_key": "private"}
    contract = build_manifest(arguments, model, enable_condenser=False)
    ensure_resume_contract(output, contract)
    ensure_resume_contract(output, contract)
    original = (output / "resume-contract.json").read_text()
    assert "private" not in original
    prompt.write_text("Fix the issue and add a test.")
    arguments["tool_preset"] = "planning"
    changed = build_manifest(arguments, model, enable_condenser=False)
    with pytest.raises(
        contract_module.ResumeContractError, match="prompt_path_sha256, tool_preset"
    ):
        ensure_resume_contract(output, changed)
    assert (output / "resume-contract.json").read_text() == original


def test_swebench_checks_contract_before_inference() -> None:
    tree = ast.parse((ROOT / "benchmarks/swebench/run_infer.py").read_text())
    main = next(
        n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"
    )
    calls = {
        n.func.id: n.lineno
        for n in ast.walk(main)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    }
    assert calls["ensure_resume_contract"] < calls["SWEBenchEvaluation"]
