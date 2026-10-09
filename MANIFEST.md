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

A verifier run over ASSAY should be reported as four numbers, not one:

1. **Faithful pairs accepted** — of 5.
2. **Failure modes caught** — of 5 (silent pass, overclaim, flattening
   duplicate, unreachable branch, reskinned duplicate).
3. **Reference implementations accepted** — the false-refusal check.
4. **Specimens where it returned no opinion** — abstention, reported
   separately from success. A verifier that abstains on everything has not
   passed; it has declined to sit the exam.

## Verifying the corpus itself

`python3 verify_manifest.py` checks that every specimen still behaves the way this
manifest says it does. Where a claim can be run, the specimen is run, in a sandbox
(a separate process with a scratch folder, a stripped environment, a timeout, no
network where the machine allows it, and a guard that stops writes outside the
scratch folder). Where a claim is only a fact about file text, it compares text and
says so. It also checks that the four copies of this answer key agree (this prose, the
machine block at the end of this file, the table in
`assay_production/manifest_registry.py`, and `assay_production/registry.json`), that
every file under `specimens/` still has the SHA-256 recorded for it, and that each
registry entry's validation status is what the run really asserted.

A specimen edit is a change to the answer key and must be reviewed. To change an
answer on purpose: edit the prose here and the table, then run
`python3 -m assay_production.manifest_registry --write`, which refuses to run unless
the corpus still behaves as the claims say, and review what it rewrites.

It deliberately asserts the **damage**. A specimen that quietly got fixed
(someone reformatting a flattened file, someone defining UZTC's missing method)
is reported as drift, not as an improvement: repairing a specimen destroys the
thing that made it one. An answer key that has drifted from its corpus is
worse than no corpus, because it scores verifiers confidently against claims
that are no longer true.

---

## Machine-readable answer key

The block below is the same answer key as the prose above, as data. It is generated by
`python3 -m assay_production.manifest_registry --write` and checked by `verify_manifest.py`
on every run. Do not edit it by hand: any difference from the table in
`assay_production/manifest_registry.py`, from `assay_production/registry.json` or from the
files on disk makes verification fail. It also records the SHA-256 of every file under
`specimens/`, so a changed specimen is caught even if it still looks fine.

<!-- ASSAY-MACHINE-BLOCK:BEGIN (generated by `python3 -m assay_production.manifest_registry --write`; do not edit by hand) -->
```json
{
 "corpus_files": {
  "specimens/failure-modes/README.md": "58f7d814a0b97c47f84e355f580fbfec31e7de69dbe5ee0a81c4184fc9cee2ca",
  "specimens/pairs/governance_os_security_adapter.py": "629b8d601b83f8b231caa8f78275c34a73117d743ae192291564ea633aad5dc7",
  "specimens/pairs/governance_os_security_source.py": "8524f990c589199f55a71eaa7e9a08eef12e4c2549788e48501a5e222afadef5",
  "specimens/pairs/quorum_state_governance_adapter.py": "9933b252bd21401f1a8c9d7d27ce468be6859c326dfb0491a9f8848994bd9a32",
  "specimens/pairs/quorum_state_governance_source.py": "fac2de2337ad6d9702d08e7f7827ffd41177c5140e1d20fadf0a9f748a86e321",
  "specimens/pairs/solvar_stability_governance_adapter.py": "0ff2d5a6602a2b2bdfaba4ccb90eaa3828f8aa89eeca12b2605b0205f45762ab",
  "specimens/pairs/solvar_stability_governance_cleanup.py": "19968ebd42ed1c35f87c7a9cd2fa2b32235bc57c23e857fb4ff9d4fb9e553d8b",
  "specimens/pairs/solvar_stability_governance_source.py": "81935555240ddfbb7c2b85ba72a43220e30c5c8d44891d3279b5b4d6e295224c",
  "specimens/pairs/sre-system-resilience-evaluator-flattened.py": "7c7911fe682f9c949a96afa012860b04d89275ec2d74e8b793e9367eea795a37",
  "specimens/pairs/sre_system_resilience_evaluator_adapter.py": "792edfb4c2cf565ed526b4da76ad3d64cf3869cce2da4052580e61df19217ba1",
  "specimens/pairs/vanguard-behavioral-simulation-flattened.py": "c4341e110285f09f4cc3795c91e44be5fec84efb69a831f500e07902a6b99764",
  "specimens/pairs/vanguard-behavioral-simulation.py": "ed2a1f32bce6461c2fa5f4c5a3058b2817c4a55d6d09e1440d4ae6220db103d5",
  "specimens/progressions/uztc/PROVENANCE.md": "47dc1f67cf2190bc51ca1b4404f1f4fa2399d48fca340875fc2cb752857ca367",
  "specimens/progressions/uztc/README.md": "0ee4c403debfd8017e5f2ff322800ae9e976c546a5b40a5d3e49d55383ffd179",
  "specimens/progressions/uztc/TRANSCRIPT.md": "1d6a14ff6e472bd8b3d93506f62f62691e4714088734ec253a14961c44c0be79",
  "specimens/progressions/uztc/uztc-construct-v1.0-flattened.py": "d8262fef6bd17ad72ad0d8e111b4a49ff07fa30aea07f943e4b93dfce16fd9fa",
  "specimens/progressions/uztc/uztc-construct-v1.1-purged.py": "077c6b9f5a75b53f99861b6badf045feeb7ba2ef708dd3d59f1da8c6102f0cfb",
  "specimens/progressions/uztc/uztc-construct-v1.2-validated.py": "c9ccd55531d29d8ecdf76ab07f771c5108d6db36aedea1d9bd048226495d3b36",
  "specimens/reference/agent-factory-tactical-agents.py": "bc8ceb904a4d8e6b8776e859ae7cb63487b1b5ef043e2192b8ee2c17ae912f1a",
  "specimens/reference/citadel_v1.2.py": "86803a4ca3b30867007f469b237720ed161a627b9b9f38afa8e1ac3cd6855c42",
  "specimens/reference/code-repo-governance-and-gsa-core.py": "9921b7aaf4c3c505b5e9738d18820dcc93110d483ed40ebe2f6a6ae786647ac2",
  "specimens/reference/resilience_stability_kernel.py": "acfafed90652bb989a7694ac0e9a1e23093ca99e06f70583fc1bb4ea14e25691",
  "specimens/reference/secure/PROVENANCE.md": "2ba3a2bd05f6db1b2ce7c778e90243f2335b73c91a9b7f26cdde49cf774ef77b",
  "specimens/reference/secure/README.md": "5c145c6699e371e01fc82952cca2f14f98fbd5b034d0b72f26b99caa027574fd",
  "specimens/reference/secure/TRANSCRIPT.md": "cef1ad3892f2dc6c2dccdc26697fcfcd30d62c6f7ec6d74c16e933b1ba31132c",
  "specimens/reference/secure/artifact_1.py": "39dfe6d25542ababeb40e79690cdbe0a3099db98258101422b94b76e6a3d6bef",
  "specimens/reference/secure/artifact_2.py": "a5e0b6da365e3ee430297dd877f20d5572ec73debc2bfebfd843277b9e04a3f6",
  "specimens/reference/sovereign_kernel.py": "880207967555d514398a6a5cdf2fe1d061116e4a6efdb7846ef44c6a54ca0299",
  "specimens/reference/wrapper/PROVENANCE.md": "3c4848bc51d1b496cffb6f4698c55a8b8f12d4b827ef9887b85bc18d57599b04",
  "specimens/reference/wrapper/README.md": "3ede9d495627462256548be45f8afacaf7454de6ef84f933f32416a4cd3ccd51",
  "specimens/reference/wrapper/TRANSCRIPT.md": "290dbfaaecba3fd75dbaf033dcb52b935d5266b14aa9fe318cf809cdbf6209c1",
  "specimens/reference/wrapper/artifact_1.py": "b3c0bb79a5179530cf00456ef45a98f5116cd9c18b01a892566b645424104221",
  "specimens/reference/wrapper/artifact_2.py": "175afe7ce18d9a908fe4e860ec786d02c3e4893be07633dd1cefb66969a2c1f7",
  "specimens/reference/wrapper/artifact_3.py": "a1930a5332d19f46ae422ff99bd3d50579e35c7181cf5023a2f8ed51bd7b82dd",
  "specimens/superseded/ARCHIVE_README.md": "ec95fe77fb87957948432e40a06c64637d6c77bbb6f21320a150950854a8c47e",
  "specimens/superseded/citadel-processor-router-flattened.py": "275999d7639698dbb00f2da6c5d6b5f15e28fbab38ed4fd7751d420a7c8bc7d1",
  "specimens/superseded/resilience-config-dataclass.py": "78fb83b4e0b6f2757e782f952d4ce2dad5968a88b63722bb3777440bd8730de6",
  "specimens/superseded/sovereign-governance-stack-v1.py": "f1aa6c075b22667794667f7b71daef8366e60db177d87062b439a0357b56f5b7",
  "specimens/superseded/sovereign-governance-stack-v2-expanded.py": "b5123cbc9df3e54968c5ff95ec6bb07a4e2ec765f9d9ee2b1044f8992bbd0a1c",
  "specimens/superseded/unified-sovereign-kernel-wrapper.py": "597b61a5f183fce2241aa9298884cdcce9894c78bc19f10b59343ab82b5cda94",
  "specimens/superseded/ure-universal-resilience-engine-flattened.py": "f83b12c06b3b15eb4871988ce2eb0a53ad3544f791714856e149de4bb318cdde",
  "specimens/superseded/vanguard-unified-governance-wrapper.py": "6440b942196a31073c3af153d6a95e2a803e2333b1db613e720d24e019df06b6"
 },
 "format": 1,
 "records": [
  {
   "class": "RECONSTRUCTION_PAIR",
   "companion_sha256": {
    "specimens/pairs/governance_os_security_adapter.py": "629b8d601b83f8b231caa8f78275c34a73117d743ae192291564ea633aad5dc7"
   },
   "companions": [
    "specimens/pairs/governance_os_security_adapter.py"
   ],
   "failure_mode": null,
   "id": "pair_governance_os_security",
   "path": "specimens/pairs/governance_os_security_source.py",
   "prose": {
    "find": "| `governance_os_security_source.py` |",
    "says": [
     "**Faithful"
    ],
    "unit": "row"
   },
   "section": "1",
   "sha256": "8524f990c589199f55a71eaa7e9a08eef12e4c2549788e48501a5e222afadef5",
   "verdict": "FAITHFUL",
   "what": "Flattened source and its reconstruction; 7 of 13 debris classes covered after normalisation."
  },
  {
   "class": "RECONSTRUCTION_PAIR",
   "companion_sha256": {
    "specimens/pairs/quorum_state_governance_adapter.py": "9933b252bd21401f1a8c9d7d27ce468be6859c326dfb0491a9f8848994bd9a32"
   },
   "companions": [
    "specimens/pairs/quorum_state_governance_adapter.py"
   ],
   "failure_mode": "lossy_reconstruction",
   "id": "pair_quorum_state_governance",
   "path": "specimens/pairs/quorum_state_governance_source.py",
   "prose": {
    "find": "| `quorum_state_governance_source.py` |",
    "says": [
     "**CONSOLIDATED / LOSSY"
    ],
    "unit": "row"
   },
   "section": "1",
   "sha256": "fac2de2337ad6d9702d08e7f7827ffd41177c5140e1d20fadf0a9f748a86e321",
   "verdict": "CONSOLIDATED_LOSSY",
   "what": "Re-architecture into *Module classes; 2 of 7 debris classes covered."
  },
  {
   "class": "RECONSTRUCTION_PAIR",
   "companion_sha256": {
    "specimens/pairs/solvar_stability_governance_cleanup.py": "19968ebd42ed1c35f87c7a9cd2fa2b32235bc57c23e857fb4ff9d4fb9e553d8b"
   },
   "companions": [
    "specimens/pairs/solvar_stability_governance_cleanup.py"
   ],
   "failure_mode": null,
   "id": "pair_solvar_stability_governance",
   "path": "specimens/pairs/solvar_stability_governance_source.py",
   "prose": {
    "find": "| `solvar_stability_governance_source.py` |",
    "says": [
     "**FAITHFUL"
    ],
    "unit": "row"
   },
   "section": "1",
   "sha256": "81935555240ddfbb7c2b85ba72a43220e30c5c8d44891d3279b5b4d6e295224c",
   "verdict": "FAITHFUL",
   "what": "Paired with _cleanup: 31 of 32 debris classes covered."
  },
  {
   "class": "RECONSTRUCTION_PAIR",
   "companion_sha256": {
    "specimens/pairs/solvar_stability_governance_adapter.py": "0ff2d5a6602a2b2bdfaba4ccb90eaa3828f8aa89eeca12b2605b0205f45762ab"
   },
   "companions": [
    "specimens/pairs/solvar_stability_governance_adapter.py"
   ],
   "failure_mode": "lossy_reconstruction",
   "id": "pair_solvar_stability_consolidation",
   "path": "specimens/pairs/solvar_stability_governance_source.py",
   "prose": {
    "find": "| `solvar_stability_governance_source.py` |",
    "says": [
     "genuine *consolidation* of the same material"
    ],
    "unit": "row"
   },
   "section": "1",
   "sha256": "81935555240ddfbb7c2b85ba72a43220e30c5c8d44891d3279b5b4d6e295224c",
   "verdict": "CONSOLIDATION_OF_SAME_SOURCE",
   "what": "Second, lossier reconstruction of the same source: 3 of 32 debris classes covered."
  },
  {
   "class": "RECONSTRUCTION_PAIR",
   "companion_sha256": {
    "specimens/pairs/sre_system_resilience_evaluator_adapter.py": "792edfb4c2cf565ed526b4da76ad3d64cf3869cce2da4052580e61df19217ba1"
   },
   "companions": [
    "specimens/pairs/sre_system_resilience_evaluator_adapter.py"
   ],
   "failure_mode": null,
   "id": "pair_sre_system_resilience",
   "path": "specimens/pairs/sre-system-resilience-evaluator-flattened.py",
   "prose": {
    "find": "| `sre-system-resilience-evaluator-flattened.py` |",
    "says": [
     "**FAITHFUL"
    ],
    "unit": "row"
   },
   "section": "1",
   "sha256": "7c7911fe682f9c949a96afa012860b04d89275ec2d74e8b793e9367eea795a37",
   "verdict": "FAITHFUL",
   "what": "11 of 11 debris classes covered; thresholds made configurable."
  },
  {
   "class": "RECONSTRUCTION_PAIR",
   "companion_sha256": {
    "specimens/pairs/vanguard-behavioral-simulation.py": "ed2a1f32bce6461c2fa5f4c5a3058b2817c4a55d6d09e1440d4ae6220db103d5"
   },
   "companions": [
    "specimens/pairs/vanguard-behavioral-simulation.py"
   ],
   "failure_mode": null,
   "id": "pair_vanguard_behavioral_simulation",
   "path": "specimens/pairs/vanguard-behavioral-simulation-flattened.py",
   "prose": {
    "find": "| `vanguard-behavioral-simulation-flattened.py` |",
    "says": [
     "**FAITHFUL"
    ],
    "unit": "row"
   },
   "section": "1",
   "sha256": "c4341e110285f09f4cc3795c91e44be5fec84efb69a831f500e07902a6b99764",
   "verdict": "FAITHFUL",
   "what": "5 of 6 covered; the miss is a deliberate, documented rename."
  },
  {
   "class": "VERSION_PROGRESSION",
   "companion_sha256": {
    "specimens/progressions/uztc/uztc-construct-v1.0-flattened.py": "d8262fef6bd17ad72ad0d8e111b4a49ff07fa30aea07f943e4b93dfce16fd9fa",
    "specimens/progressions/uztc/uztc-construct-v1.1-purged.py": "077c6b9f5a75b53f99861b6badf045feeb7ba2ef708dd3d59f1da8c6102f0cfb"
   },
   "companions": [
    "specimens/progressions/uztc/uztc-construct-v1.0-flattened.py",
    "specimens/progressions/uztc/uztc-construct-v1.1-purged.py"
   ],
   "failure_mode": "false_progression",
   "id": "uztc_progression",
   "path": "specimens/progressions/uztc/uztc-construct-v1.2-validated.py",
   "prose": {
    "find": "## 2.",
    "says": [
     "A progression that looks monotonically better and is not is exactly what this specimen is for"
    ],
    "unit": "section"
   },
   "section": "2",
   "sha256": "c9ccd55531d29d8ecdf76ab07f771c5108d6db36aedea1d9bd048226495d3b36",
   "verdict": "NOT_MONOTONIC_IMPROVEMENT",
   "what": "Looks better at every step by parses/imports; the endpoint is the least functional."
  },
  {
   "class": "FAILURE_MODE",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": "silent_pass",
   "id": "fm_3_1_silent_pass",
   "path": "specimens/pairs/governance_os_security_source.py",
   "prose": {
    "find": "### 3.1",
    "says": [
     "**REFUSE.**"
    ],
    "unit": "section"
   },
   "section": "3.1",
   "sha256": "8524f990c589199f55a71eaa7e9a08eef12e4c2549788e48501a5e222afadef5",
   "verdict": "REFUSE",
   "what": "Whole file is one comment: imports cleanly, defines zero names."
  },
  {
   "class": "FAILURE_MODE",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": "overclaim",
   "id": "fm_3_2_overclaim",
   "path": "specimens/progressions/uztc/uztc-construct-v1.2-validated.py",
   "prose": {
    "find": "### 3.2",
    "says": [
     "the documentation claim is **false**"
    ],
    "unit": "section"
   },
   "section": "3.2",
   "sha256": "c9ccd55531d29d8ecdf76ab07f771c5108d6db36aedea1d9bd048226495d3b36",
   "verdict": "CLAIM_FALSE",
   "what": "Described as a 7-layer construct; its only method raises AttributeError."
  },
  {
   "class": "FAILURE_MODE",
   "companion_sha256": {
    "specimens/reference/secure/artifact_1.py": "39dfe6d25542ababeb40e79690cdbe0a3099db98258101422b94b76e6a3d6bef"
   },
   "companions": [
    "specimens/reference/secure/artifact_1.py"
   ],
   "failure_mode": "flattening_duplicate",
   "id": "fm_3_3_flattening_duplicate",
   "path": "specimens/reference/wrapper/artifact_3.py",
   "prose": {
    "find": "### 3.3",
    "says": [
     "**the same content.**"
    ],
    "unit": "section"
   },
   "section": "3.3",
   "sha256": "a1930a5332d19f46ae422ff99bd3d50579e35c7181cf5023a2f8ed51bd7b82dd",
   "verdict": "SAME_CONTENT",
   "what": "Same content twice, one flattened; wrapper/artifact_3.py is canonical."
  },
  {
   "class": "FAILURE_MODE",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": "unreachable_branch",
   "id": "fm_3_4_unreachable_branch",
   "path": "specimens/pairs/sre_system_resilience_evaluator_adapter.py",
   "prose": {
    "find": "### 3.4",
    "says": [
     "the verdict is unreachable"
    ],
    "unit": "section"
   },
   "section": "3.4",
   "sha256": "792edfb4c2cf565ed526b4da76ad3d64cf3869cce2da4052580e61df19217ba1",
   "verdict": "UNREACHABLE",
   "what": "EvaluationVerdict.CRITICAL cannot be reached through evaluate_system_telemetry()."
  },
  {
   "class": "FAILURE_MODE",
   "companion_sha256": {
    "specimens/pairs/sre_system_resilience_evaluator_adapter.py": "792edfb4c2cf565ed526b4da76ad3d64cf3869cce2da4052580e61df19217ba1"
   },
   "companions": [
    "specimens/pairs/sre_system_resilience_evaluator_adapter.py"
   ],
   "failure_mode": "reskinned_duplicate",
   "id": "fm_3_5_reskinned_duplicate",
   "path": "specimens/pairs/solvar_stability_governance_adapter.py",
   "prose": {
    "find": "### 3.5",
    "says": [
     "**the same design, reskinned"
    ],
    "unit": "section"
   },
   "section": "3.5",
   "sha256": "0ff2d5a6602a2b2bdfaba4ccb90eaa3828f8aa89eeca12b2605b0205f45762ab",
   "verdict": "SAME_DESIGN_RESKINNED",
   "what": "Identical energy formula and thresholds under different class names."
  },
  {
   "class": "SUPERSEDED",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": "superseded",
   "id": "superseded_sovereign_governance_stack_v1",
   "path": "specimens/superseded/sovereign-governance-stack-v1.py",
   "prose": {
    "find": "## 4.",
    "says": [
     "these are negative examples",
     "sovereign-governance-stack"
    ],
    "unit": "section"
   },
   "section": "4",
   "sha256": "f1aa6c075b22667794667f7b71daef8366e60db177d87062b439a0357b56f5b7",
   "verdict": "NOT_BEST_AVAILABLE",
   "what": "Tried and replaced; a verifier picking the best implementation must not choose this."
  },
  {
   "class": "SUPERSEDED",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": "superseded",
   "id": "superseded_sovereign_governance_stack_v2_expanded",
   "path": "specimens/superseded/sovereign-governance-stack-v2-expanded.py",
   "prose": {
    "find": "## 4.",
    "says": [
     "these are negative examples",
     "sovereign-governance-stack"
    ],
    "unit": "section"
   },
   "section": "4",
   "sha256": "b5123cbc9df3e54968c5ff95ec6bb07a4e2ec765f9d9ee2b1044f8992bbd0a1c",
   "verdict": "NOT_BEST_AVAILABLE",
   "what": "Tried and replaced; a verifier picking the best implementation must not choose this."
  },
  {
   "class": "SUPERSEDED",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": "superseded",
   "id": "superseded_unified_sovereign_kernel_wrapper",
   "path": "specimens/superseded/unified-sovereign-kernel-wrapper.py",
   "prose": {
    "find": "## 4.",
    "says": [
     "these are negative examples",
     "unified-sovereign-kernel-wrapper"
    ],
    "unit": "section"
   },
   "section": "4",
   "sha256": "597b61a5f183fce2241aa9298884cdcce9894c78bc19f10b59343ab82b5cda94",
   "verdict": "NOT_BEST_AVAILABLE",
   "what": "Tried and replaced; a verifier picking the best implementation must not choose this."
  },
  {
   "class": "SUPERSEDED",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": "superseded",
   "id": "superseded_citadel_processor_router_flattened",
   "path": "specimens/superseded/citadel-processor-router-flattened.py",
   "prose": {
    "find": "## 4.",
    "says": [
     "these are negative examples",
     "citadel-processor-router-flattened.py"
    ],
    "unit": "section"
   },
   "section": "4",
   "sha256": "275999d7639698dbb00f2da6c5d6b5f15e28fbab38ed4fd7751d420a7c8bc7d1",
   "verdict": "NOT_BEST_AVAILABLE",
   "what": "Tried and replaced; a verifier picking the best implementation must not choose this."
  },
  {
   "class": "SUPERSEDED",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": "superseded",
   "id": "superseded_resilience_config_dataclass",
   "path": "specimens/superseded/resilience-config-dataclass.py",
   "prose": {
    "find": "## 4.",
    "says": [
     "these are negative examples",
     "resilience-config-dataclass.py"
    ],
    "unit": "section"
   },
   "section": "4",
   "sha256": "78fb83b4e0b6f2757e782f952d4ce2dad5968a88b63722bb3777440bd8730de6",
   "verdict": "NOT_BEST_AVAILABLE",
   "what": "Tried and replaced; a verifier picking the best implementation must not choose this."
  },
  {
   "class": "SUPERSEDED",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": "superseded",
   "id": "superseded_ure_universal_resilience_engine_flattened",
   "path": "specimens/superseded/ure-universal-resilience-engine-flattened.py",
   "prose": {
    "find": "## 4.",
    "says": [
     "these are negative examples",
     "ure-universal-resilience-engine-flattened.py"
    ],
    "unit": "section"
   },
   "section": "4",
   "sha256": "f83b12c06b3b15eb4871988ce2eb0a53ad3544f791714856e149de4bb318cdde",
   "verdict": "NOT_BEST_AVAILABLE",
   "what": "Tried and replaced; a verifier picking the best implementation must not choose this."
  },
  {
   "class": "REFERENCE",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": null,
   "id": "reference_sovereign_kernel",
   "path": "specimens/reference/sovereign_kernel.py",
   "prose": {
    "find": "## 5.",
    "says": [
     "must be **accepted**",
     "sovereign_kernel.py"
    ],
    "unit": "section"
   },
   "section": "5",
   "sha256": "880207967555d514398a6a5cdf2fe1d061116e4a6efdb7846ef44c6a54ca0299",
   "verdict": "ACCEPT",
   "what": "Genuinely runs; refusing it is a false refusal."
  },
  {
   "class": "REFERENCE",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": null,
   "id": "reference_secure_artifact_2",
   "path": "specimens/reference/secure/artifact_2.py",
   "prose": {
    "find": "## 5.",
    "says": [
     "must be **accepted**",
     "secure/artifact_2.py"
    ],
    "unit": "section"
   },
   "section": "5",
   "sha256": "a5e0b6da365e3ee430297dd877f20d5572ec73debc2bfebfd843277b9e04a3f6",
   "verdict": "ACCEPT",
   "what": "Genuinely runs; refusing it is a false refusal."
  },
  {
   "class": "REFERENCE",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": null,
   "id": "reference_code_repo_governance_and_gsa_core",
   "path": "specimens/reference/code-repo-governance-and-gsa-core.py",
   "prose": {
    "find": "## 5.",
    "says": [
     "must be **accepted**",
     "code-repo-governance-and-gsa-core.py"
    ],
    "unit": "section"
   },
   "section": "5",
   "sha256": "9921b7aaf4c3c505b5e9738d18820dcc93110d483ed40ebe2f6a6ae786647ac2",
   "verdict": "ACCEPT",
   "what": "Genuinely runs; refusing it is a false refusal."
  },
  {
   "class": "REFERENCE",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": null,
   "id": "reference_resilience_stability_kernel",
   "path": "specimens/reference/resilience_stability_kernel.py",
   "prose": {
    "find": "## 5.",
    "says": [
     "must be **accepted**",
     "resilience_stability_kernel.py"
    ],
    "unit": "section"
   },
   "section": "5",
   "sha256": "acfafed90652bb989a7694ac0e9a1e23093ca99e06f70583fc1bb4ea14e25691",
   "verdict": "ACCEPT",
   "what": "Genuinely runs; refusing it is a false refusal."
  },
  {
   "class": "REFERENCE",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": null,
   "id": "reference_citadel_v1_2",
   "path": "specimens/reference/citadel_v1.2.py",
   "prose": {
    "find": "## 5.",
    "says": [
     "must be **accepted**",
     "citadel_v1.2.py"
    ],
    "unit": "section"
   },
   "section": "5",
   "sha256": "86803a4ca3b30867007f469b237720ed161a627b9b9f38afa8e1ac3cd6855c42",
   "verdict": "ACCEPT",
   "what": "Genuinely runs; refusing it is a false refusal."
  },
  {
   "class": "REFERENCE",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": null,
   "id": "reference_agent_factory_tactical_agents",
   "path": "specimens/reference/agent-factory-tactical-agents.py",
   "prose": {
    "find": "## 5.",
    "says": [
     "must be **accepted**",
     "agent-factory-tactical-agents.py"
    ],
    "unit": "section"
   },
   "section": "5",
   "sha256": "bc8ceb904a4d8e6b8776e859ae7cb63487b1b5ef043e2192b8ee2c17ae912f1a",
   "verdict": "ACCEPT",
   "what": "Genuinely runs; refusing it is a false refusal."
  },
  {
   "class": "REFERENCE",
   "companion_sha256": {},
   "companions": [],
   "failure_mode": null,
   "id": "reference_solvar_stability_governance_cleanup",
   "path": "specimens/pairs/solvar_stability_governance_cleanup.py",
   "prose": {
    "find": "## 5.",
    "says": [
     "must be **accepted**",
     "solvar_stability_governance_cleanup.py"
    ],
    "unit": "section"
   },
   "section": "5",
   "sha256": "19968ebd42ed1c35f87c7a9cd2fa2b32235bc57c23e857fb4ff9d4fb9e553d8b",
   "verdict": "ACCEPT",
   "what": "Genuinely runs (needs matplotlib); refusing it is a false refusal."
  }
 ]
}
```
<!-- ASSAY-MACHINE-BLOCK:END -->
