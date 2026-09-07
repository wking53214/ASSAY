# WRAPPER

Archive of a 5-turn Gemini transcript ("Wrapper") combining a GSA
Universal Cryptographic Interlock Wrapper Engine with an application-level
sandboxing/capability kernel (`Event`, `CapabilityError`,
`validate_capabilities`, circuit-breaker logic), plus a copy of the
recurring AST-based graph extractor. See `PROVENANCE.md` for the full
turn-by-turn writeup.

**GSA lineage:** tagged alongside
[CITADEL](https://github.com/wking53214/CITADEL),
[STRIDE](https://github.com/wking53214/STRIDE),
[SECURE](https://github.com/wking53214/SECURE), and
[UZTC](https://github.com/wking53214/UZTC).

**Canonical copy of the sandbox kernel:** `artifact_3.py`'s sandbox-kernel
section is byte-for-byte identical (whitespace-stripped) to the entirety
of [SECURE](https://github.com/wking53214/SECURE)'s `artifact_1.py` —
confirmed by direct comparison (13,539 characters, exact match either
way). This is the origin point: the content was generated in this
WRAPPER session with real line breaks intact, then pasted into a fresh
SECURE session later where whitespace got lost in copy/paste or export.
`artifact_3.py` here is the canonical, readable copy; SECURE's
`artifact_1.py` is a redundant, badly-flattened duplicate.
