"""Offline checks for the pinned SWE-bench resume boundary."""

import ast
from pathlib import Path


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
