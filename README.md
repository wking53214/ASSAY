# ASSAY

**Specimen corpus, not a system.** Real code, really damaged, with independently-known correct answers. Fuel for [`ghost_tools`](https://github.com/wking53214/ghost_tools), [`SWIZZLE`](https://github.com/wking53214/SWIZZLE) and [`Warden`](https://github.com/wking53214/Warden), which read the answer key as data from `assay_production/registry.json`. Absorbed retired [`VANGUARD`](https://github.com/wking53214/VANGUARD) files as evidence.

## 1. Pipeline Position & Role

**ASSURANCE FIXTURES.** Not Admission, Observe, Policy, Decision, Conservation, Execution, or Custody.

## 2. Full System Scope & Architectural Depth

`MANIFEST.md` + `verify_manifest.py` + specimen trees (including `.ghost_archive`). Known-damage cases with expected findings. matplotlib/numpy appear in some specimens (not a product stack). 4 TODOs.

## 3. What It Does NOT Do / Non-Goals

Does not run a governance kernel. Does not pass CI as "the app." Shipping it as a product is a category error (commercial: **NOT COMMERCIALLY RELEVANT**; possibly test data).

## 4. Brutally Honest Current Status & Gaps

If `verify_manifest.py` and the archive disagree, the corpus is lying — treat that as a P0 for assurance. VANGUARD wrapper does not run; it is preserved damage, not a dependency.

## 5. Core Invariants & Guarantees

Independently-known answers. Manifest verification. Specimens must not be "fixed" into green code without updating the known-answer file (that would poison SWIZZLE).

## 6. Inputs, Outputs & Type Contracts

Manifest records: specimen path, specimen class, expected verdict, MANIFEST section. Published as `assay_production/registry.json`; regenerate with `python3 -m assay_production.manifest_registry --write`.

## 7. Stack Integration Topology

```text
VANGUARD (retired) → specimens here
MANIFEST.md → assay_production/registry.json (generated; guarded by verify_manifest.py)
registry.json → swizzle assay → ghost_buster scored (also in ghost_tools CI)
registry.json → Warden AssayAdapter
```

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). Copyright 2026 William N. King.
