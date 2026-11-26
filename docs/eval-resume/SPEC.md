# Resume contract

```text
CLI settings + hashes of prompt/selection files
    -> canonical manifest -> validation at SWE-bench entry point
    -> existing evaluator -> existing output files and grader
```

The manifest contains a schema version and scalar settings. Path fields are represented by SHA-256 of file contents. Explicitly allowlisted non-secret LLM settings are stored. Provider routing and environment remain operator-controlled and must be kept fixed for a comparison.

| Failure | Detection | Outcome |
| --- | --- | --- |
| Different tool preset or prompt bytes | Field-by-field comparison | Refuse before inference |
| Existing legacy output | Nonempty directory without manifest | Preserve data and request a fresh output directory |
| Malformed manifest | Decode or shape check | Preserve data and request a fresh output directory |
| Interrupted first write | Atomic replacement after writing a sibling temporary file | No partially written manifest |
| Provider error | Existing evaluator error output | Existing retry policy applies |

Use a sibling manifest so the existing JSONL schemas and graders keep working. Use explicit field selection so an added provider credential cannot silently become a persisted field. Concurrent dispatch into one directory is outside the upstream runner's supported contract for this branch.
