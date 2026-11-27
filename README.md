# OpenHands SWE-bench resume integrity

The SWE-bench runner reuses an output directory when its model, SDK revision,
iteration cap and note match. Its tool preset can change without changing that
path. The attempt selector may then skip results from the earlier run, leaving
one evaluation with rows from two tool configurations.

This branch starts from OpenHands Benchmarks commit
`60b3548cea8b41276ac0d44ea36a01b82936bbe4` and keeps its evaluator, task setup,
and grading path. The resume contract records the checked settings before
inference. It validates that contract on a subsequent run and reports changed
fields before the evaluator starts. The original results remain in place.

Run the focused tests from the checkout root with Python 3.12 or newer and
pytest installed.

```sh
python -m pytest -q --noconftest tests/test_eval_resume_contract.py
```

The tests exercise the contract using local fixture files. Keep the provider,
image, benchmark dataset revision, and workspace setup fixed when comparing
runs. Use a fresh output directory for legacy results or intentionally changed
settings. Concurrent writers and custom critic configuration are outside the
scope of this check. The fixture suite measures the resume decision without
making claims about agent resolution rates.

See the [problem statement](docs/eval-resume/PRD.md),
[resume spec](docs/eval-resume/SPEC.md), and
[upstream setup and evaluation instructions](https://github.com/OpenHands/benchmarks/blob/60b3548cea8b41276ac0d44ea36a01b82936bbe4/README.md).
