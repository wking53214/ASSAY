# governance-stack/archive

Superseded or orphaned material, kept for provenance. Nothing here is imported.

The first three files are sketches of one thing: the top-level governance
wrapper that sits a master orchestrator (policy, audit, linguistic parity) in
front of a hybrid quorum-consensus execution engine. Each references collaborator
classes that were never defined anywhere in this repo at the time
(`GSARuntimeOrchestrator`, `TraceStore`, `UnifiedGovernanceKernel`,
`initialize_hybrid_cluster`, `QuorumConsensusEngine`, `SignatureVerifier`,
`KeystoneNode`, ...) and raises `NameError` on import. Two of the names they
also reference, `SystemResilienceEvaluator` and `TelemetryMetrics`, are real
now - see `../sre_system_resilience_evaluator_adapter.py` - but these three
sketch files still don't run: none of the others exist, and none of these
three were updated to use the real SRE module.

They are superseded 2026-08-27 by `../sovereign_kernel.py`, which builds the same
composition from the modules that now work in `governance-stack/` (VANGUARD
behavioral pipeline; GsaCoreController + GsaTemporalDoorwayGate; the
quorum-consensus adapter).

## unified-sovereign-kernel-wrapper.py

The narrowest of the three. Master layer + hybrid execution engine only.
The layer it describes that `sovereign_kernel.py` still does not build is the
linguistic-neutrality scrub - carried there as a labelled pass-through hook.

## sovereign-governance-stack-v1.py
## sovereign-governance-stack-v2-expanded.py

Near-identical. Both add two ideas the working wrapper did not originally cover:

  * an SRE / system-resilience stability check as **step 1**, before the
    VANGUARD perimeter - reject on `EvaluationVerdict.CRITICAL` drift. Built
    2026-09-03: `../sre_system_resilience_evaluator_adapter.py`, wired into
    `../sovereign_kernel.py` as its own step 0. One deliberate divergence from
    what's sketched here: reconstruction verification found
    `EvaluationVerdict.CRITICAL` is mathematically unreachable through SRE's
    `evaluate_system_telemetry()` as originally designed (DEGRADED's energy
    gate always trips first - proven by exhaustive search in
    `sre_system_resilience_evaluator_adapter.py`'s own `__main__`). Rejecting
    on CRITICAL alone would be a decorative check that can never fire, so
    `sovereign_kernel.py` rejects on DEGRADED or CRITICAL instead - SRE's own
    file, weights, and thresholds are untouched; this is a wiring-layer
    decision, documented in `sovereign_kernel.py`'s header.
  * a named 4-plane framing: Observatory (SRE + VANGUARD), Governance /
    Orchestrator (GSA-Master), Execution (DGK consensus), plus a KeystoneNode.
    Not adopted - `sovereign_kernel.py` keeps its existing layer framing.

v2-expanded additionally records a critical-failure entry to an audit ledger on
SRE rejection, and carries a `main()` demo. v1 has neither. Neither runs.

The README one level up describes v2-expanded as "the SovereignGovernanceStack
V10.0 architecture"; that line points at this archived path now.

## ure-universal-resilience-engine-flattened.py

Moved here 2026-09-03. URE and SRE cover the same conceptual ground - both
compute a weighted-squared-deviation "energy" drift score against a baseline
and classify it into a tri-level verdict, and in fact share an identical
formula shape with SOLVAR's `LyapunovStabilityModule` (all three use the same
`1e-4` / `1e-2` stability thresholds - not a coincidence, the same design
reskinned per source repo; see `../resilience_stability_kernel.py`'s header).
But unlike SRE, nothing in this repo references URE by name - not the
sketches above, not `sovereign_kernel.py`, nothing - and its regime classifier
(`SystemRegimeClassifier.classify_current_regime`) is hardcoded
(`0.70 if metrics.backlog_depth < 10.0 else 0.10`, ...) rather than derived
from its actual inputs, unlike SRE's entropy-based classifier or SOLVAR's
input-driven one. Flattened (does not parse) and evidence-only: preserved
here rather than reconstructed, since there is no consumer for it and its own
central classification step doesn't do what its docstring claims.

## citadel-processor-router-flattened.py

A separate thing: a linguistic-enforcement engine that shares CITADEL's five
detection patterns and its four profile names but is built around a different
mechanism. Rather than CITADEL's deterministic in-process detect / score /
transform, this one runs a model-retry loop: it calls a language-model
`generator`, scores the result with an external `simplicity_logic.SimplicityScore`
(which exists in neither this repo nor CITADEL), and if the score is below the
profile threshold it re-prompts the model with the list of rule violations, up
to 3 times, detecting output loops and forcing a rephrase. Flattened; cannot run.

CITADEL's own repo (`citadel_v1.2.py`) holds the canonical deterministic engine,
and it also carries two constraints this file lacks (em-dash / punctuation
control, and a prohibited-verbs check from the STRIDE lineage). This file is not
the "duplicate" the parent README calls it. Its genuinely distinct pieces, kept
here as a record:

  * `StructureNormalizer` - a corporate-jargon synonym map (methodology ->
    approach, facilitate -> help, functionality -> features, prioritize -> rank,
    ...), broader than CITADEL's verb normalization.
  * a `VARIATION` constraint - an anti-loop rule that forces a different
    structure when the model returns text it has already produced.
  * `SimplicityTelemetry` - aggregate pass/bypass telemetry across calls.

`sovereign_kernel.py`'s linguistic step was built 2026-09-03 drawing on
CITADEL's deterministic engine (vendored as `../citadel_v1.2.py`), not this
variant.

## resilience-config-dataclass.py

A clean, syntactically intact `@dataclass ResilienceConfig` with a `validate()`
hysteresis check. Referenced by nothing - not in this repo, not by the resilience
engine files it was committed alongside (`ure-*` has its own separate, larger
`SystemResilienceConfig`). Its docstring says it defines the "Safety Envelopes"
for "the Orchestrator, Fortress, and Iceberg modules", but:

  * Iceberg is not a repo - it is the internal name for the IVR/telephony
    simulator lineage extracted from sentinel_os into GSA-815, which has its own
    `adaptive_config.py` and uses none of these field names;
  * FORTRESS's predictive controller carries its own local config with the
    overlapping fields (`nominal_slew`, `surprisal_weight`,
    `causal_divergence_cap`, same defaults).

So no module ever imported the shared envelope; each would-be consumer localized
its own. Field values, preserved here:

    stability_stable        1e-4      stability_marginal     1e-2
    volatility_weight       0.05      surprisal_weight       0.02
    causal_divergence_cap   0.45      causal_divergence_scale 25.0
    enter_threshold         0.55      exit_threshold         0.35   (hysteresis band)
    queue_max               5000.0    abandon_max            0.95
    nominal_slew            0.20      sensitivity            15.0

    validate(): raises if enter_threshold <= exit_threshold.

## vanguard-behavioral-simulation-flattened.py
## vanguard-unified-governance-wrapper.py

Folded in 2026-09-03 from the [VANGUARD](https://github.com/wking53214/VANGUARD)
repo (commit `e0329513fd4335172999da73251c8f80e5451d84`), which is now archived.
Unlike CITADEL (kept as its own repo deliberately - a general-purpose tool, not
GSA-specific), nothing argued for VANGUARD staying separate: its own README
said it existed only because it was "moved here from DGK once this repo
existed - previously kept there deliberately as 'raw VANGUARD material, not
something that needs its own destination' until now," and nothing outside
GSA-GATEWAY referenced it. VANGUARD's README is preserved in full below.

`vanguard-behavioral-simulation-flattened.py` is the flattened raw paste
`../vanguard-behavioral-simulation.py` was reconstructed from (see that
file's own header) - preserved evidence, same as everything else in this
folder. It was already reconstructed before this fold-in; this is just its
last remaining home for the original.

`vanguard-unified-governance-wrapper.py` is `VanguardUnifiedGovernanceStack`
("VANGUARD-MASTER-HYBRID WRAPPER V10.0") - the same sketch as the three files
at the top of this document (a perimeter check, then delegate to a
`UnifiedSovereignKernel`), just under VANGUARD's own branding, and superseded
the same way: by `../sovereign_kernel.py`. Doesn't run - no imports at all,
so `Dict`/`Any` in its type annotations raise `NameError` at class-definition
time, and `system_logger` is referenced but never defined. VANGUARD's own
README already documented this honestly ("not a working integration").

### VANGUARD's README, as it stood before archival

> # VANGUARD
>
> Raw VANGUARD material, moved here from [DGK](https://github.com/wking53214/DGK)
> once this repo existed — previously kept there deliberately as "raw
> VANGUARD material, not something that needs its own destination" until
> now.
>
> ## Contents
>
> - **`vanguard-unified-governance-wrapper.py`**: `VanguardUnifiedGovernanceStack`
>   ("VANGUARD-MASTER-HYBRID WRAPPER V10.0") — a perimeter-gate wrapper
>   that runs a `PipelineCycleManager` forecast check before delegating to
>   a `UnifiedSovereignKernel` ("DIT-GOV4-DGK Hybrid Kernel"). Both
>   `PipelineCycleManager` and `UnifiedSovereignKernel` are defined in
>   [GSA-GATEWAY](https://github.com/wking53214/GSA-GATEWAY)'s
>   `governance-stack/` — this file doesn't define its own governance
>   logic, it's VANGUARD's own branding wrapped around those two classes.
>   Parses cleanly (real line breaks, no corruption).
>
> - **`vanguard-behavioral-simulation-flattened.py`**: self-declared
>   `SYSTEM NAME: VANGUARD (Validation Matrix & Neutral Governance
>   Automated Routing Engine)` — "an advanced closed-loop behavioral
>   simulation kernel designed to model, forecast..." per its own header.
>   A single unbroken line (no real newlines at all — the filename says
>   so), same flattening defect seen throughout this week's sweep. Kept
>   as-is, not reconstructed; reconstructing real structure from a
>   flattened file this size would mean guessing at intent.
>
> The `SovereignGovernanceStack` files in GSA-GATEWAY's `governance-stack/`
> also reference VANGUARD conceptually (as one of several subsystems it
> wires together, alongside SRE, DIT, and a consensus engine) — those
> stay in GSA-GATEWAY since they're multi-system integration code, not
> VANGUARD-specific content.
>
> ## Runnable status
>
> Neither file executes on its own. The wrapper parses but references
> `PipelineCycleManager` / `UnifiedSovereignKernel` (supplied by GSA-GATEWAY)
> and is a ~45-line sketch of the perimeter-gate pattern, not a working
> integration. The behavioral-simulation file does not parse — it is a single
> flattened line. This repository is a preserved architectural baseline, not
> an executable system.
>
> ## License
>
> Apache-2.0 — see `LICENSE` (matching the rest of this repo ecosystem).
