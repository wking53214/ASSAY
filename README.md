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
  - From DGK: the `SovereignGovernanceStack` architecture sketches and a
    CITADEL-derived processor/router. All now under
    `governance-stack/archive/` — see the cleanup note below.
  - From EDDP (formerly Data_files): `governance_os_security_source.py`/
    `_adapter.py` (a working `BaseGate`/`BoundaryGate`/`InvariantGate`
    pattern), `solvar_stability_governance_source.py`/`_adapter.py`/
    `_cleanup.py` (connects to "Fortress/SOLVAR" per DIT's own
    provenance notes), and `quorum_state_governance_source.py`/
    `_adapter.py` (moved here provisionally as GSA-lineage content
    regardless of the still-open question of whether it's also ATS's
    missing `gov4_kernel` dependency — checked once already: the import
    names didn't line up cleanly, see ATS's `ats_seam_inventory.md`).
  - `_source.py` files are the flattened raw pastes (preserved evidence,
    several do not parse); the matching `_adapter.py` files are the working
    reconstructions.

### governance-stack cleanup, step 1 (2026-09-02)

The first reconciliation pass over `governance-stack/` — no longer "a
separate, later pass":

- **`code-repo-governance-and-gsa-core.py`** — added `GsaCoreController` +
  `GsaTemporalDoorwayGate` (reconstructed from CODE's flattened paste) and
  the registry/decorator, `gsa_deep_freeze`, and `@dataclass` the file
  needed to import at all.
- **`vanguard-behavioral-simulation.py`** (new) — VANGUARD's behavioral
  kernel, reconstructed from its flattened source. Its
  `PipelineCycleManager` is renamed `VanguardBehavioralPipeline` here (name
  clash with the unrelated one in the GSA core file).
- **`sovereign_kernel.py`** (new) — a working `UnifiedSovereignKernel` that
  wires perimeter (VANGUARD) → linguistic (a labelled pass-through hook, not
  yet built) → master (GSA doorway handshake) → execution (quorum
  consensus). The running version of what the archived sketches described.
- **`agent-factory-tactical-agents.py`** — one-line import fix (`Any`).
- **`governance-stack/archive/`** (new) — 5 files moved out with a README:
  the three `sovereign-governance-stack*` / `unified-sovereign-kernel-wrapper`
  sketches, the diverged `citadel-processor-router-flattened.py` variant, and
  the unreferenced `resilience-config-dataclass.py`.

Still not done: the linguistic scrub (needs CITADEL's engine), an SRE
stability pre-check (SRE modules still flattened), the `_source.py`
reconstructions, and reconciling `quorum_state_governance` against ATS's
`gov4_kernel`.

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

The initial consolidation (commits through `f0934b1`) was a pure content
move — files relocated, git history not preserved cross-repo, no code
edits. The `governance-stack/` cleanup described above is the first pass of
the follow-up code work.
