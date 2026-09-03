# governance-stack/archive

Superseded or orphaned material, kept for provenance. Nothing here is imported.

The first three files are sketches of one thing: the top-level governance
wrapper that sits a master orchestrator (policy, audit, linguistic parity) in
front of a hybrid quorum-consensus execution engine. Each references collaborator
classes that were never defined in this repo (`GSARuntimeOrchestrator`,
`TraceStore`, `UnifiedGovernanceKernel`, `initialize_hybrid_cluster`,
`QuorumConsensusEngine`, `SignatureVerifier`, `SystemResilienceEvaluator`,
`KeystoneNode`, `TelemetryMetrics`, ...) and raises `NameError` on import.

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

Near-identical. Both add two ideas the working wrapper does not yet cover:

  * an SRE / system-resilience stability check as **step 1**, before the
    VANGUARD perimeter - reject on `EvaluationVerdict.CRITICAL` drift. The SRE
    modules in this folder (`sre-*`, `ure-*`) are still flattened, so this is
    not buildable yet.
  * a named 4-plane framing: Observatory (SRE + VANGUARD), Governance /
    Orchestrator (GSA-Master), Execution (DGK consensus), plus a KeystoneNode.

v2-expanded additionally records a critical-failure entry to an audit ledger on
SRE rejection, and carries a `main()` demo. v1 has neither. Neither runs.

The README one level up describes v2-expanded as "the SovereignGovernanceStack
V10.0 architecture"; that line points at this archived path now.

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

When `sovereign_kernel.py`'s linguistic step is built, it should draw on
CITADEL's deterministic engine, not this variant.

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
