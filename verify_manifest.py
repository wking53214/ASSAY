#!/usr/bin/env python3
"""Check that every specimen still behaves the way MANIFEST.md says it does.

A corpus whose answer key has drifted from its contents is worse than no
corpus: it scores verifiers against claims that are no longer true, and does
it confidently. This script is the guard against that, and it should be run
before anyone trusts a score produced from this repository.

It deliberately asserts the *damage*. A specimen that quietly got fixed --
someone reformatting a flattened file, someone defining the missing method in
UZTC -- destroys the thing that made it a specimen, and this reports it as a
failure rather than an improvement.

    python3 verify_manifest.py        # exits non-zero on drift
"""
from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SPECIMENS = ROOT / "specimens"

results: list[tuple[bool, str]] = []


def check(label: str, condition: bool) -> None:
    results.append((bool(condition), label))


def parses(path: Path) -> bool:
    try:
        ast.parse(path.read_text(errors="replace"))
        return True
    except SyntaxError:
        return False


def load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --- 1. Reconstruction pairs -------------------------------------------------
# Each degraded source must still be degraded, and each reconstruction must
# still be present and parseable. Both halves are required: a pair with a
# missing half is not a pair.

PAIRS = [
    ("pairs/governance_os_security_source.py", "pairs/governance_os_security_adapter.py"),
    ("pairs/quorum_state_governance_source.py", "pairs/quorum_state_governance_adapter.py"),
    # Paired with _cleanup, not _adapter: the adapter is a lossier
    # consolidation of the same source and pairing against it recorded a false
    # "most divergent artifact in the corpus" verdict for a day.
    ("pairs/solvar_stability_governance_source.py", "pairs/solvar_stability_governance_cleanup.py"),
    ("pairs/sre-system-resilience-evaluator-flattened.py", "pairs/sre_system_resilience_evaluator_adapter.py"),
    ("pairs/vanguard-behavioral-simulation-flattened.py", "pairs/vanguard-behavioral-simulation.py"),
]

for source_rel, adapter_rel in PAIRS:
    source, adapter = SPECIMENS / source_rel, SPECIMENS / adapter_rel
    name = source.name
    check(f"pair intact: {name} + {adapter.name}", source.is_file() and adapter.is_file())
    if source.is_file():
        # Flattened: one enormous line. `wc -l` reports 0 because there is no
        # terminating newline on the single line.
        check(f"{name} still flattened (0 newline-terminated lines)",
              source.read_bytes().count(b"\n") == 0)
    if adapter.is_file():
        check(f"{adapter.name} still parses", parses(adapter))


# --- 2. Version progression --------------------------------------------------

UZTC = SPECIMENS / "progressions/uztc"
check("uztc v1.0 still does not parse", not parses(UZTC / "uztc-construct-v1.0-flattened.py"))
check("uztc v1.1 still parses", parses(UZTC / "uztc-construct-v1.1-purged.py"))
check("uztc v1.2 still parses", parses(UZTC / "uztc-construct-v1.2-validated.py"))


# --- 3. Failure modes --------------------------------------------------------

# 3.1 Silent pass: imports cleanly, defines nothing. The whole point is that
# an importability check calls this healthy.
silent = SPECIMENS / "pairs/governance_os_security_source.py"
try:
    module = load(silent)
    defined = [n for n in dir(module) if not n.startswith("__")]
    check("3.1 silent pass: imports without error", True)
    check("3.1 silent pass: defines zero names", len(defined) == 0)
except Exception as exc:  # noqa: BLE001
    check(f"3.1 silent pass: imports without error (got {type(exc).__name__})", False)
    check("3.1 silent pass: defines zero names", False)

# 3.2 Overclaim: v1.2 presents as the refined endpoint and cannot run.
try:
    uztc = load(UZTC / "uztc-construct-v1.2-validated.py")
    construct = uztc.Universal_Zero_Trust_Construct({})
    try:
        construct.validate_synthesis({"x": 1})
        check("3.2 overclaim: v1.2 still raises on its only method", False)
    except AttributeError:
        check("3.2 overclaim: v1.2 still raises AttributeError", True)
except Exception as exc:  # noqa: BLE001
    check(f"3.2 overclaim: v1.2 loadable ({type(exc).__name__})", False)

# 3.3 Flattening duplicate: same content, one flattened, one not.
canonical = SPECIMENS / "reference/wrapper/artifact_3.py"
flattened_copy = SPECIMENS / "reference/secure/artifact_1.py"
check("3.3 flattening duplicate: both halves present",
      canonical.is_file() and flattened_copy.is_file())
if canonical.is_file() and flattened_copy.is_file():
    check("3.3 flattening duplicate: copies still differ textually",
          canonical.read_bytes() != flattened_copy.read_bytes())
    check("3.3 flattening duplicate: secure/ copy still the flattened one",
          flattened_copy.read_bytes().count(b"\n") < canonical.read_bytes().count(b"\n"))


# --- 4. Reference implementations -------------------------------------------
# These must remain runnable. A corpus of only broken material cannot test
# whether a verifier ever correctly says yes.

sandbox = SPECIMENS / "reference/secure/artifact_2.py"
check("reference sandbox present", sandbox.is_file())
if sandbox.is_file():
    import importlib
    import shutil
    import tempfile

    # Imported by module name rather than through spec_from_file_location.
    # The specimen uses @dataclass, and dataclasses resolve string annotations
    # via sys.modules[cls.__module__] -- which is absent for a module built
    # from a spec, producing an AttributeError that looks exactly like a
    # broken specimen and is not one. Worth the extra lines: a harness that
    # reports false drift trains people to ignore it.
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(sandbox, Path(tmp) / "sandbox_specimen.py")
        sys.path.insert(0, tmp)
        try:
            sandbox_module = importlib.import_module("sandbox_specimen")
            try:
                sandbox_module.validate_capabilities({"net.exfiltrate"})
                check("reference sandbox still enforces capabilities", False)
            except Exception:  # the CapabilityError it should raise
                check("reference sandbox still enforces capabilities", True)
        except Exception as exc:  # noqa: BLE001
            check(f"reference sandbox still loads ({type(exc).__name__})", False)
        finally:
            sys.path.remove(tmp)
            sys.modules.pop("sandbox_specimen", None)


# --- 6. Published registry ---------------------------------------------------
# touchstone_production/registry.json is what consumers (Elegant) read. It is
# generated from manifest_registry.py; a stale or hand-edited copy hands them
# an answer key that no longer matches this file.

sys.path.insert(0, str(ROOT))
try:
    from touchstone_production import manifest_registry as _mr

    check("registry: every registered specimen file exists", not _mr.missing_paths(ROOT))
    check("registry: registry.json is published", _mr.REGISTRY_PATH.is_file())
    if _mr.REGISTRY_PATH.is_file():
        check("registry: registry.json matches manifest_registry.py "
              "(regenerate with: python3 -m touchstone_production.manifest_registry --write)",
              _mr.REGISTRY_PATH.read_text(encoding="utf-8") == _mr.render(ROOT))
except Exception as exc:  # noqa: BLE001
    check(f"registry: manifest_registry loads ({type(exc).__name__}: {exc})", False)
finally:
    sys.path.remove(str(ROOT))


# --- report ------------------------------------------------------------------

failures = [label for ok, label in results if not ok]
for ok, label in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")

print()
print(f"{len(results) - len(failures)}/{len(results)} manifest claims hold")
if failures:
    print("\nMANIFEST DRIFT -- the answer key no longer matches the corpus.")
    print("A specimen that was 'fixed' is a specimen destroyed; check whether")
    print("the repair was intended before updating MANIFEST.md to match.")
    sys.exit(1)
print("The corpus matches its answer key.")
