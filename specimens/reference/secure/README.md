# SECURE

Archive of a 2-turn Gemini transcript ("SECURE") merging an
application-level capability/sandboxing kernel with a "GSA Universal
Adapter" governance-envelope framework, plus a copy of the recurring
AST-based graph extractor. See `PROVENANCE.md` for the full writeup.

**GSA lineage:** tagged alongside
[CITADEL](https://github.com/wking53214/CITADEL),
[STRIDE](https://github.com/wking53214/STRIDE),
[UZTC](https://github.com/wking53214/UZTC), and
[WRAPPER](https://github.com/wking53214/WRAPPER).

**`artifact_1.py` is a redundant duplicate.** It's byte-for-byte identical
(whitespace-stripped) to the sandbox-kernel section of
[WRAPPER](https://github.com/wking53214/WRAPPER)'s `artifact_3.py` — this
repo's copy just lost its line breaks somewhere in copy/paste or export.
WRAPPER's copy is the canonical, readable one; this file doesn't need
independent preservation.

**`artifact_2.py`'s `ANATHEMA_STATE: PROVENANCE_FAILED` is not a bug.**
Running it produces that status on its own bundled demo input, which
looks alarming for a provenance-focused system but is the code working
exactly as designed. The demo's sample sentence is literally `"I check
the system parameters for paradox logic."` (`artifact_2.py`, `_main()`),
and `SyntacticValidationLayer.scrub_and_verify()` unconditionally rejects
any input containing `"paradox"` or `"recursion"` (its
`forbidden_logic` list) before any real processing happens — the demo
sentence trips its own filter. Feeding it text without those words
processes normally and returns `PIPELINE_ITERATION_EXECUTED`.
