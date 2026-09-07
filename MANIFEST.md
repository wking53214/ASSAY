# Specimen Manifest

Every specimen in this corpus, what it is, and **what the correct answer is**.

The last column is the point. A corpus without stated correct answers is just
files; a verifier scored against material whose answers nobody wrote down is
scored against nothing. Where the correct answer is genuinely unknown, this
manifest says so rather than inventing one.

**How to read a specimen entry**

- **Is** — what the file physically is, verified by execution, not by its own
  claims about itself.
- **Proves** — what a system consuming it can legitimately be tested on.
- **Correct answer** — the verdict a working verifier must reach. This is the
  falsifiable part.

---

## 1. Reconstruction pairs — `specimens/pairs/`

Five matched pairs: a **degraded original** and the **verified reconstruction**
built from it. These are the corpus's core asset, because both halves exist and
the relationship between them is known.

Every degraded source here is *flattened* — all line breaks destroyed by a
copy-paste through a chat interface, leaving one enormous line. Measured: each
reports **0 lines** to `wc -l` while carrying 10–33 KB of content.

| Degraded source | Bytes | Reconstruction | Lines | Correct answer |
|---|---|---|---|---|
| `governance_os_security_source.py` | 11,700 | `governance_os_security_adapter.py` | 299 | **Faithful — 13 debris classes, 10 adapter classes, 7 covered after normalisation (2026-09-07).** Source content is two concatenated AI-chat drafts of one design; all of it appears in the adapter's `*Module` classes. A verifier must accept this pair. |
| `quorum_state_governance_source.py` | 14,162 | `quorum_state_governance_adapter.py` | 310 | **CONSOLIDATED / LOSSY — measured 2026-09-07.** 7 class-shaped tokens in the debris, 7 classes in the adapter, **2 covered after name normalisation**. Not a faithful reconstruction: a re-architecture into `*Module` classes. Confirmed 2026-09-03 this is *not* ATS's `gov4_kernel` — that question is closed. |
| `solvar_stability_governance_source.py` | 33,137 | **`solvar_stability_governance_cleanup.py`** | 32 classes | **FAITHFUL — 31 of 32 debris classes covered (97%), corrected 2026-09-07.** The specimen was originally paired with `solvar_stability_governance_adapter.py` (8 classes, 3 covered, 10%) and recorded as the most divergent artifact in the corpus. **That was a pairing error, not a lossy reconstruction.** An ecosystem-wide inventory diff found a second reconstruction of the same source carrying all 32 classes, including every capability the earlier note said had been dropped — `EthicsValidationEngine`, `EthicsViolation`, `OperationalReplayHasher`, `AdvisoryDirectiveEngine`, `HorizonForecastingEngine` are all present. The 8-class adapter is a genuine *consolidation* of the same material and is kept beside the pair as a second, lossier reconstruction of one source — which is itself the more interesting specimen. |
| `sre-system-resilience-evaluator-flattened.py` | 15,520 | `sre_system_resilience_evaluator_adapter.py` | 570 | **FAITHFUL — measured 2026-09-07: 11 debris classes, 11 adapter classes, 11/11 covered.** With one documented divergence — see failure-mode 4 below. Thresholds were made configurable rather than hardcoded; SRE's weights, field mapping and output are otherwise a literal reconstruction, regression-checked against the original numpy formula. |
| `vanguard-behavioral-simulation-flattened.py` | 9,877 | `vanguard-behavioral-simulation.py` | 239 | **FAITHFUL — measured 2026-09-07: 6 debris classes, 6 adapter classes, 5/6 covered (83%); the miss is the rename below.** One deliberate rename: `PipelineCycleManager` → `VanguardBehavioralPipeline`, to resolve a name clash with an unrelated class of the same name in the GSA core file. A verifier that flags the rename as unfaithful is being too strict; one that misses it is not reading names. |

**Measured 2026-09-07 — the first real use of this corpus, and it corrected
the corpus.** Every "Faithful" verdict above was inherited prose from an
earlier README and had never been checked. Running
`blackhole_extrapolator`'s residue detector over each flattened source and
diffing the surviving class-name debris against the adapter beside it gives:

| specimen | debris | adapter | covered | verdict |
|---|---|---|---|---|
| sre-system-resilience | 11 | 11 | 11 (100%) | faithful |
| vanguard-behavioral | 6 | 6 | 5 (83%) | faithful |
| governance_os_security | 13 | 10 | 7 (70%) | faithful |
| quorum_state_governance | 7 | 7 | 2 (29%) | **consolidated / lossy** |
| solvar_stability (vs `_cleanup`) | 32 | 32 | 31 (97%) | faithful |
| solvar_stability (vs `_adapter`) | 32 | 8 | 3 (10%) | consolidation of the same source |

Two of five verdicts were wrong on the first pass, and one of those
corrections was itself wrong: solvar was recorded as the corpus's most
divergent artifact on the strength of a comparison against the wrong file. An
ecosystem-wide inventory diff found a second reconstruction of the same source
at 97% coverage sitting in another directory. Nothing had been lost; the pair
had been assembled from the wrong half.

Both errors are the same shape and worth naming: a verdict recorded without
the measurement that would support it. The first came from inherited prose,
the second from measuring against the first candidate found rather than
looking for all of them. An answer key whose answers have never been measured
is an assertion; one measured against an unverified counterpart is a
better-dressed assertion.

Read the coverage number for what it is. It compares class-name inventories
after normalising common suffixes, so it detects **dropped or re-architected
surface**, not semantic infidelity. A reconstruction could score 100% and
still have changed behaviour, and a heavy but honest re-architecture scores
low without anything being lost. What the low scores establish is that
"faithful" was never checked and is not supported for those two.

**What consumes this:** Conservation Kernel (does it accept a faithful
transformation on material it did not author?), CCC's anti-probability matcher
(does it recognise source and adapter as the same content, not two findings?),
TIE (what does its coverage layer honestly report as un-inspected given a
0-line input?).

---

## 2. Version progression — `specimens/progressions/uztc/`

One construct across three states, with the intent of each step recorded.

| Version | Lines | Is | Correct answer |
|---|---|---|---|
| `uztc-construct-v1.0-flattened.py` | 0 (1,078 bytes) | Flattened original | Does not parse. |
| `uztc-construct-v1.1-purged.py` | 23 | "Purged" | Parses and imports. |
| `uztc-construct-v1.2-validated.py` | 20 | "Validated" | Parses and imports — **and is non-functional**, see failure-mode 2. |

**Correct answer for the progression as a whole:** a verifier that measures
only *parses / imports* will report steady improvement across all three
versions. It will be wrong. The v1.2 endpoint is the least functional thing in
this corpus while presenting as the most refined. **A progression that looks
monotonically better and is not is exactly what this specimen is for.**

---

## 3. Failure modes — the named specimens

### 3.1 Silent pass — `specimens/pairs/governance_os_security_source.py`

**Is:** A flattened file, like the others — except its single line begins with
`#`. Python therefore treats the *entire 11,700-byte file* as one comment.

**Measured:** imports cleanly, raises nothing, **defines 0 names**.

**Proves:** the difference between *"the check passed"* and *"the thing works"*.
Every other flattened source in this corpus fails loudly with a `SyntaxError`.
This one fails silently, and an importability check reports it as healthy.

**Correct answer:** **REFUSE.** A verifier that accepts this file because it
imports has learned nothing about it. The correct verdict is that a module
defining zero names is not a module. Any tool asked *"is this code intact?"*
that answers yes here has failed the corpus.

> This is the ecosystem's canonical specimen of a failure class it has now met
> five times: a dead lazy-import whose `NameError` was caught and reported as a
> principled governance refusal; three tests whose assertions sat behind guards
> that were never true; a HERALD adapter stamping schema-valid events with the
> wrong date; and integrity validation of an artifact the validator itself had
> just sealed. Something satisfies its check without doing its job.

### 3.2 Overclaim — `specimens/progressions/uztc/`

**Is:** 20 lines. The provenance record describes it as *"the Universal
Zero-Trust Construct, a 7-layer registry including a named Provenance layer."*
The named Provenance layer is `self.provenance = {"status":
"AGNOSTIC_FRAMEWORK_INITIALIZED"}` — a dict containing a string. Layer
constants are placeholders: `[ETHICIST_NODE_ALPHA]`,
`[NON_UNIVERSAL_ID_STRING]`.

**Measured:** its only method, `validate_synthesis`, calls
`self._check_node_compliance`, **which is never defined anywhere**. Calling it
raises `AttributeError`.

**Proves:** the gap between what a repository says about itself and what its
code does — with both halves preserved, so the gap is measurable rather than
alleged.

**Correct answer:** the documentation claim is **false**, and a verifier
reading only the description will accept a component that cannot run. The
description is preserved verbatim in `README.md` under *Preserved overclaim*
precisely so this specimen keeps working.

### 3.3 Flattening duplicate — `specimens/reference/wrapper/artifact_3.py` vs `specimens/reference/secure/artifact_1.py`

**Is:** the same sandbox-kernel content, twice. The `wrapper/` copy retains
real line breaks; the `secure/` copy was flattened.

**Proves:** duplicate detection on content that is genuinely identical but
textually very different — the hard case, where a matcher keyed on formatting
will miss a real duplicate.

**Correct answer:** **the same content.** `wrapper/artifact_3.py` is canonical.
A matcher that calls these two unrelated has failed; one that calls them a
coincidence has failed harder.

### 3.4 Unreachable branch — `specimens/pairs/sre_system_resilience_evaluator_adapter.py`

**Is:** a faithful reconstruction that surfaced a defect in the original.
`EvaluationVerdict.CRITICAL` is **mathematically unreachable** through
`evaluate_system_telemetry()` as originally designed — DEGRADED's energy gate
always trips first. Proven during reconstruction, documented, not silently
"fixed".

**Proves:** dead-by-construction code that no import check, no type check and
no test-coverage tool reports, because the branch exists and is syntactically
reachable.

**Correct answer:** the verdict is unreachable. A verifier claiming full
behavioural coverage of this module without noticing is overstating.

### 3.5 Reskinned duplicate — `solvar_stability_governance_adapter.py` vs `sre_system_resilience_evaluator_adapter.py`

**Is:** SOLVAR's `LyapunovStabilityModule` and SRE's
`SystemStabilityValidator` implement the **identical** weighted-deviation
energy formula with **identical** thresholds (`1e-4` / `1e-2`), under different
class names in files from different source repositories.

**Proves:** cross-repository semantic duplication that no textual matcher will
find — different names, different files, different lineage, same design.

**Correct answer:** **the same design, reskinned — not a coincidence.** The
shared formula has since been extracted once into
`specimens/reference/resilience_stability_kernel.py` and property-verified.
This is the specimen for *"can your duplicate detection see past naming?"*

---

## 4. Superseded — `specimens/superseded/`

Approaches that were tried and replaced, kept beside what replaced them:
the three `sovereign-governance-stack*` / `unified-sovereign-kernel-wrapper`
architecture sketches, a diverged `citadel-processor-router-flattened.py`
variant, an unreferenced `resilience-config-dataclass.py`, and
`ure-universal-resilience-engine-flattened.py` (unreferenced, and its regime
classifier is hardcoded rather than derived from its inputs).

**Correct answer:** these are negative examples. A system asked to pick the
best available implementation of an idea should not choose from here. Their
value is that the *reason* each was rejected is recorded rather than lost.

---

## 5. Reference implementations — `specimens/reference/`

Things in this corpus that genuinely run, kept because a corpus of only broken
material cannot test whether a verifier ever says yes.

| File | Verified | What it is |
|---|---|---|
| `sovereign_kernel.py` | runs | `UnifiedSovereignKernel` — a working four-stage pipeline: SRE precheck → linguistic scrub → perimeter (VANGUARD) → execution (quorum). **Superseded as a system** by the observe-perceive chain; kept as a reference implementation, not a live orchestrator. |
| `secure/artifact_2.py` | runs, enforces | Capability-based sandbox. `validate_capabilities({'net.exfiltrate'})` genuinely raises `CapabilityError`. Also `SecurityEngine`, `CryptographicAuditFramework`, `PipelineCycleManager`, `GsaUniversalAdapter.execute_interlock`, side-effect tracing. |
| `code-repo-governance-and-gsa-core.py` | runs | GSA core controller + temporal doorway gate. Four methods reference an undefined `SYSTEM_GLOBALS` — documented, unfixed, no definition exists anywhere. A sixth specimen if anyone wants it. |
| `resilience_stability_kernel.py` | runs | The shared SOLVAR/SRE formula, extracted once and property-verified. |
| `citadel_v1.2.py`, `agent-factory-tactical-agents.py`, `solvar_stability_governance_cleanup.py` | run (cleanup needs matplotlib) | Working GSA-lineage material. |

**Correct answer:** these must be **accepted**. A verifier that refuses
everything scores perfectly on the broken half of this corpus and is useless.
That is what these are here to catch.

---

## Scoring against this corpus

A verifier run over TOUCHSTONE should be reported as four numbers, not one:

1. **Faithful pairs accepted** — of 5.
2. **Failure modes caught** — of 5 (silent pass, overclaim, flattening
   duplicate, unreachable branch, reskinned duplicate).
3. **Reference implementations accepted** — the false-refusal check.
4. **Specimens where it returned no opinion** — abstention, reported
   separately from success. A verifier that abstains on everything has not
   passed; it has declined to sit the exam.

## Verifying the corpus itself

`python3 verify_manifest.py` checks that every specimen still behaves the way
this manifest says it does — 26 claims, all asserted by execution.

It deliberately asserts the **damage**. A specimen that quietly got fixed
(someone reformatting a flattened file, someone defining UZTC's missing method)
is reported as drift, not as an improvement: repairing a specimen destroys the
thing that made it one. An answer key that has drifted from its corpus is
worse than no corpus, because it scores verifiers confidently against claims
that are no longer true.
