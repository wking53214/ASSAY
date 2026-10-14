# Failure modes

The named specimens do not live in this directory. Each one is a *property of
a file* that also belongs to a pair, a progression or the reference set, and
moving it here would break the pairing that gives it meaning — a silent-pass
source is only interesting beside the reconstruction that recovered it.

They are catalogued in [`../../MANIFEST.md`](../../MANIFEST.md) §3, with the
correct verdict for each:

| # | Failure mode | Lives in |
|---|---|---|
| 3.1 | **Silent pass** — imports cleanly, defines zero names | `pairs/governance_os_security_source.py` |
| 3.2 | **Overclaim** — documentation describes a system the code cannot be | `progressions/uztc/` |
| 3.3 | **Flattening duplicate** — identical content, unrecognisable textually | `reference/wrapper/artifact_3.py` vs `reference/secure/artifact_1.py` |
| 3.4 | **Unreachable branch** — a verdict no input can produce | `pairs/sre_system_resilience_evaluator_adapter.py` |
| 3.5 | **Reskinned duplicate** — same formula, same thresholds, different names, different repos | `pairs/solvar_stability_governance_adapter.py` vs `pairs/sre_system_resilience_evaluator_adapter.py` |
| 3.6 | **Test that cannot fail** — four green tests, none of which could have been red | `failure-modes/cannot_fail/test_governance_boots.py` |
| 3.7 | **Unbacked status claim** — "production-ready", "RL Ready", "100% coverage", beside no code and no test | `failure-modes/status_claims/README.md` |

Two specimens do live here, 3.6 and 3.7. They are constructed, and each says
so in its own text: they reproduce failures recorded in the ecosystem's own
history (tests whose assertions never ran; a README claiming readiness for
things that had not shipped) in the smallest shape that keeps every property.
Everything else here exists to be looked in and to redirect, because someone
scanning the tree will look here first.
