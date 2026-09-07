# TOUCHSTONE

**A specimen corpus. Not a system.**

A touchstone does nothing by itself. You streak gold across it and read the
mark to judge purity. Its entire value is that other things are tested against
it — and that is exactly what this repository is for.

See [`MANIFEST.md`](./MANIFEST.md) for every specimen, what it proves, and
**what the correct answer is**.

---

## Why this exists

Every verification claim in this ecosystem is currently calibrated against
material its own author invented. The Conservation Kernel's `build_ground_truth()`
is entirely synthetic — hand-constructed propositions named `p-human-fact`,
`ev-conflict-a`, built to be verified by the verifier that verifies them. That
is circular, and it is the deepest weakness in the platform: not that the
verifiers are wrong, but that **nothing can show whether they are right**.

TOUCHSTONE is the ecosystem's only non-synthetic ground truth. Real code,
really damaged, with independently-known correct answers — because the damage
happened first and was catalogued afterwards, not designed to be caught.

The corpus answers one question the platform could not previously ask:

> Does this verifier reach the right verdict on material it did not author?

## What is here

| | |
|---|---|
| **`specimens/pairs/`** | Five matched pairs — a flattened original beside its verified reconstruction. Both halves exist; the relationship is known. |
| **`specimens/progressions/`** | One construct across three versions, with the intent of each step recorded — and an endpoint that presents as most refined while being least functional. |
| **`specimens/failure-modes/`** | Named in the manifest, located among the pairs and references: silent pass, overclaim, flattening duplicate, unreachable branch, reskinned duplicate. |
| **`specimens/superseded/`** | Approaches tried and replaced, kept beside what replaced them, with the reason recorded. |
| **`specimens/reference/`** | Material that genuinely runs. A corpus of only broken things cannot test whether a verifier ever says yes. |

## The specimen worth knowing about

`specimens/pairs/governance_os_security_source.py` is a flattened file like
the others — except its single line begins with `#`. Python treats the entire
11,700-byte file as one comment. It **imports cleanly, raises nothing, and
defines zero names**.

Every other flattened source in this corpus fails loudly with a `SyntaxError`.
This one fails silently, and an importability check reports it as healthy.

It is the canonical physical specimen of a failure class this ecosystem has now
met five separate times — something that satisfies its check without doing its
job. The others are catalogued in the manifest.

## How to use it

The corpus is inert by design. A verifier is run across it and scored on four
numbers, kept separate:

1. faithful pairs **accepted**
2. failure modes **caught**
3. reference implementations **accepted** — the false-refusal check
4. specimens where it **returned no opinion**

That fourth number matters. A verifier that abstains on everything has not
passed; it has declined to sit the exam.

## History

This repository was `GSA-GATEWAY`, a consolidation point for GSA-lineage
content scattered across several separately-archived repos with no unified
home — `SECURE`, `UZTC`, `WRAPPER`, plus governance-stack material from DGK,
VANGUARD and EDDP. That work is intact and is what makes the corpus possible;
the forensic detail from those passes has moved into `MANIFEST.md`, where it
now serves as the answer key rather than as a changelog.

The rename reflects what the contents turned out to be good for, which is not
what they were gathered for. As a system this material was always going to be
marginal — parallel implementations of patterns the governance chain already
has properly wired. As evidence it is the only thing of its kind here.

### Preserved overclaim

The prior README described `uztc/` as *"the Universal Zero-Trust Construct, a
7-layer registry including a named Provenance layer."* It is 20 lines. The
named Provenance layer is a dict containing one string, and its only method
calls a function that is never defined — it raises `AttributeError` when
called.

That sentence is quoted here rather than deleted, because the gap between it
and the code is itself specimen 3.2. Correcting it away would destroy the
evidence.

### Source repositories

`SECURE`, `UZTC` and `WRAPPER` still exist on GitHub, now empty of code, left
in place for review rather than auto-deleted. `VANGUARD` was folded in and
archived 2026-09-03.

---

*Apache-2.0. Nothing here is a running system, and nothing here should be
imported by one.*
