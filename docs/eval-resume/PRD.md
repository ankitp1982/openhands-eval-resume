# Resume integrity for SWE-bench

An engineer deciding whether to roll out a coding-agent configuration needs every result in a resumed batch to represent the same experiment. The output path groups runs by model, SDK, iteration limit and note. Some effective settings, including the tool preset and prompt bytes, can change while the path stays the same. The attempt selector can then skip rows produced with the earlier settings.

The operator needs a mismatch diagnosis before model dispatch and a separate output directory for the next run. OpenHands already provides task orchestration and retry selection. SWE-bench already provides a reference grader. This branch adds an input contract at the existing resume boundary.

Non-goals are cross-host coordination, model rankings, and recovering provenance for legacy outputs. Upstream remains responsible for provider retries and final grading.

Validation reads a bounded manifest independent of task count. Invalid, legacy or incompatible state fails closed before dispatch. Diagnostics name the field and explain how to keep the old run. Acceptance requires matching settings to resume, changed settings to refuse before evaluation, and stored fields and diagnostics to exclude credentials.
