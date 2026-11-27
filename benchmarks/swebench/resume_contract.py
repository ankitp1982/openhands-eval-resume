from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import TypeAlias


Scalar: TypeAlias = str | int | float | bool | None
Manifest: TypeAlias = dict[str, Scalar]
MANIFEST = "resume-contract.json"

RUN_FIELDS = (
    "dataset",
    "split",
    "workspace",
    "max_iterations",
    "n_limit",
    "n_critic_runs",
    "critic",
    "max_retries",
    "tool_preset",
    "enable_delegation",
    "agent_type",
    "condenser_max_size",
    "condenser_max_tokens",
    "condenser_max_output_tokens",
    "condenser_keep_first",
)
MODEL_FIELDS = (
    "model",
    "temperature",
    "top_p",
    "max_input_tokens",
    "max_output_tokens",
    "reasoning_effort",
)


class ResumeContractError(ValueError):
    """Existing evaluation state cannot be reused safely."""


def build_manifest(
    arguments: dict[str, Scalar], model: dict[str, Scalar], *, enable_condenser: bool
) -> Manifest:
    if arguments.get("critic_config"):
        raise ResumeContractError(
            "Custom critic configuration is outside this resume contract."
        )
    manifest: Manifest = {"schema": 1, "enable_condenser": enable_condenser}
    manifest.update({field: arguments.get(field) for field in RUN_FIELDS})
    manifest.update({f"llm.{field}": model.get(field) for field in MODEL_FIELDS})
    for field in ("prompt_path", "select"):
        value = arguments.get(field)
        manifest[f"{field}_sha256"] = (
            hashlib.sha256(Path(value).read_bytes()).hexdigest()
            if isinstance(value, str)
            else None
        )
    if not all(
        value is None or isinstance(value, (str, int, float, bool))
        for value in manifest.values()
    ):
        raise ResumeContractError("Evaluation settings must be scalar.")
    return manifest


def ensure_resume_contract(directory: Path, expected: Manifest) -> None:
    path = directory / MANIFEST
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeError, ValueError) as error:
            raise ResumeContractError(
                "Invalid resume manifest. Use a fresh --output-dir."
            ) from error
        if not isinstance(existing, dict):
            raise ResumeContractError(
                "Invalid resume manifest. Use a fresh --output-dir."
            )
        mismatches = sorted(
            key
            for key in expected
            if key not in existing or existing[key] != expected[key]
        )
        if existing.keys() - expected.keys():
            mismatches.append("unknown manifest fields")
        if mismatches:
            fields = ", ".join(mismatches)
            raise ResumeContractError(
                f"Resume configuration changed ({fields}). Use a fresh --output-dir."
            )
        return
    if any(directory.iterdir()):
        raise ResumeContractError(
            "Existing output has no resume manifest. Use a fresh --output-dir."
        )
    payload = json.dumps(expected, sort_keys=True, allow_nan=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=directory, delete=False
    ) as temporary:
        temp_path = Path(temporary.name)
        try:
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
            os.replace(temp_path, path)
        finally:
            temp_path.unlink(missing_ok=True)
