# Job 1 audit plan — approved baseline and ordered acceptance

User authorization: 2026-10-04, after prompt pre-review. Run Job 1 only.
Matching baseline: `1276d0ca1daece81b5b7b38c8b5f5280046e5077`.
Story baseline: `d5117a6de0fd0c640a336c6f456946ec8b40f319`.

## Approved clarifications

- Freeze implementation and evidence at the two commits. Audit documents and receipts are separate additions; they do not redefine baseline bytes.
- Audit blocker owners include `you`, `data`, `story`, `media`, `matching`, `none`. This clarification applies to audit reports, not an unapproved production contract patch.
- PASS means the audit job's required checks completed, even if it identifies system defects. FAIL means an executed required acceptance check failed. BLOCKED means required evidence/access prevents completion. Preserve individual check states when multiple conditions apply.
- Gold references remain editor-designated positive target evidence. Compare revisions by exact narration and provenance before interpreting semantic differences; do not mistake changed scripts for regressions.
- Job 1 inventories, verifies integrity and maps actual execution. Semantic quality, root-cause attribution and redesign remain Jobs 2–8.

## Ordered stages

1. **Freeze and configuration.** Read policy, verify clean baseline and session model/effort, preserve exact input hashes. Check: Astra/Medium recorded; no production mutation.
2. **Source inventory.** Resolve every manifest path at its pinned commit, expand listed directories, follow source manifests and note external evidence paths. Check: each source is accounted for as present or a precise gap.
3. **Evidence integrity.** Use existing evidence validation and JSON Schema, verify source hashes and JSON pointers, recount all 439 records and current 12/48 reviews, inspect mirror deduplication and authorship. Verify both gold digests. Check: exact successes/failures recorded without rebuilding the canonical evidence.
4. **System map.** Read actual Story and Matching code, contracts and artifacts. Map owner, input, implementation symbol, output, validation, bypass risk and consumer for each required stage. Check: all stages resolve to code or explicit human work; no semantic audit or redesign.
5. **Reference and boundary reconciliation.** Search named references and their source links for the original transcript-to-beat/job mapping. Record exact missing role/spans if unresolved. Check: no invented reference; gold revision alignment documented for later jobs.
6. **Publish Job 1 reports.** Save `reports/astra-root-cause/01-system-map.md` and `.json` with execution receipt, evidence citations, stage receipts and status. Check required stage receipts and report fields; test omission by removing each required stage from an in-memory validation copy. Recheck baseline production/evidence hashes and workflow checkpoint. Do not run Job 2.

Execution uses existing readers, Python standard library, installed JSON Schema validation and existing audit tests; no new production implementation, renderer or template is introduced. Missing tools/evidence are disclosed, not silently replaced. Human semantic evaluation is explicitly pending in later jobs.
