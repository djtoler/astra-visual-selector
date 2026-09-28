# After Effects template technical specifications

This directory contains the reusable code used to inventory, inspect, reconcile, freeze, and summarize the technical capacity of existing After Effects templates.

It measures, per composition:

- independent media inputs;
- maximum simultaneously enabled inputs;
- exact editable text layers and their native properties;
- duration, frame rate, frame count, and work area;
- nested composition use without double-counting inputs;
- missing dependencies and unresolved replacement-slot claims.

The workflow is inspection-only. It does not render previews, modify source projects, or merge results into a selector or catalog.

## Contents

- `capacity_inventory.py` and `zip_inventory.py`: source discovery, hashing, duplicate handling, and inventory freezing.
- `static_inspect.py`: static `.aep`/`.aepx` extraction through `py-aep`.
- `vendor/capacity-inspector/`: native After Effects inspection runner and JSX inspector.
- `prepare_native_batch.py`, `run_native_batch.py`, and `derive_native_batch.py`: isolated native batch preparation and execution.
- `derive_capacity.py`: per-composition technical-capacity derivation.
- `reconcile_passes.py`: static/native comparison without silently resolving disagreements.
- `freeze_batch.py`, `build_batch_summary.py`, and `build_master_summary.py`: immutable measurement and summary generation.
- `audit_existing_reports.py`, `match_existing_reports.py`, and `materialize_recovered_batch.py`: recovery and source-binding of earlier native reports.
- `restage_with_packages.py`: the original local package-restaging helper used for this run; its source-root map is machine-specific.
- `test_*.py`: the software test suite used during the measurement run.
- `PLAN.md`: scope, measurement rules, execution order, and accuracy-test boundary.

Generated reports, staged templates, `.aep` files, preview media, caches, and machine-specific run logs are intentionally excluded.

## Requirements

- Python 3.12 or newer
- `py-aep==0.17.0` for static inspection
- Adobe After Effects 2025 for native inspection
- macOS for the included native runner

The inventory command accepts `--root`; use that instead of the original local default. Native jobs supply their template and output paths in JSON. The vendored runner's `inspect` mode is read-only; its build/render modes belong to the parent repository's separately gated rendering system and are not part of this technical-spec workflow.

## Tests

Run from this directory:

```sh
python3 -m unittest discover -p 'test_*.py'
```

The tests validate inventory classification, recursive capacity derivation, pass reconciliation, native-path handling, and ZIP inventory behavior. They do not replace manual accuracy testing against real After Effects projects.
