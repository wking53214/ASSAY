# GSA-GATEWAY

**Name is provisional.** This repo consolidates GSA-lineage content that
was previously scattered across many separately-archived repos with no
unified home. Renaming a GitHub repo afterward is trivial (Settings →
rename), so this name wasn't a blocker on doing the consolidation.

## Contents

- `secure/` — the full former [SECURE](https://github.com/wking53214/SECURE)
  repo: a working SECURE-sandbox + GSA-adapter kernel.
- `uztc/` — the full former [UZTC](https://github.com/wking53214/UZTC)
  repo: the Universal Zero-Trust Construct, a 7-layer registry including
  a named Provenance layer.
- `wrapper/` — the full former [WRAPPER](https://github.com/wking53214/WRAPPER)
  repo: the GSA Universal Interlock Wrapper + sandbox kernel. Confirmed
  origin session for `secure/`'s sandbox-kernel content — keep
  `wrapper/artifact_3.py` as canonical; it has real line breaks where the
  copy under `secure/artifact_1.py` was flattened.
- `governance-stack/` — governance-stack material pulled from two other
  repos:
  - From DGK: `sovereign-governance-stack-v2-expanded.py` (the
    `SovereignGovernanceStack V10.0` architecture wiring VANGUARD + SRE +
    DIT + a consensus/quorum engine together) and
    `citadel-processor-router-flattened.py` (a duplicate of CITADEL's
    real regex-enforcement logic).
  - From EDDP (formerly Data_files): `governance_os_security_source.py`/
    `_adapter.py` (a working `BaseGate`/`BoundaryGate`/`InvariantGate`
    pattern), `solvar_stability_governance_source.py`/`_adapter.py`/
    `_cleanup.py` (connects to "Fortress/SOLVAR" per DIT's own
    provenance notes), and `quorum_state_governance_source.py`/
    `_adapter.py` (moved here provisionally as GSA-lineage content
    regardless of the still-open question of whether it's also ATS's
    missing `gov4_kernel` dependency — checked once already: the import
    names didn't line up cleanly, see ATS's `ats_seam_inventory.md`).

The original three repos (`SECURE`, `UZTC`, `WRAPPER`) still exist on
GitHub but are now empty of code — left in place for William to review
and delete manually, not auto-deleted.

## Related repos, not folded in here

- [CITADEL](https://github.com/wking53214/CITADEL) — a Deterministic LLM
  Output Enforcement Engine, substantial enough to stay its own repo.
  `wrapper/`'s content includes "Zero-Trust Citadel Linguistic
  Interceptors" as a component, consuming CITADEL's enforcement logic.
- [STRIDE](https://github.com/wking53214/STRIDE) (renamed from CLIP) — a
  gateway system, also substantial enough to stay its own repo, also
  consuming CITADEL's enforcement logic.

This is a pure content move (files relocated, git history not
preserved cross-repo) — no code edits, bug fixes, or class renames were
made as part of this pass. That's a separate, later pass.
