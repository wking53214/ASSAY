"""ref.agent_factory.runs asserts the specimen's documented behaviour, not just an exit code.

An auditor replaced agent-factory-tactical-agents.py with ``raise SystemExit(0)`` and re-recording accepted it,
because the old claim only needed the file to run and exit 0. These tests replace the specimen with trivial or
subtly wrong versions and require both the verifier and the deliberate re-record command to refuse.
"""
import json
import re

import pytest

from assay_production.sandbox import run_in_sandbox
from conftest import ROOT, edit, run_verify, run_write

REL = "specimens/reference/agent-factory-tactical-agents.py"
CLAIM = "ref.agent_factory.runs"
SUMMARY = re.compile(r"^ASSAY-SUMMARY: (\{.*\})$", re.M)


def failing_claims(proc) -> dict:
    found = SUMMARY.search(proc.stdout)
    assert found is not None, proc.stdout[-400:]
    return {f["claim"]: f for f in json.loads(found.group(1))["failures"]}


def mutate_to_trivial(path):
    path.write_text("raise SystemExit(0)\n", encoding="utf-8")


def mutate_to_empty(path):
    path.write_text("", encoding="utf-8")


def mutate_to_print_only(path):
    path.write_text("print('ALL AGENT CHECKS PASSED')\n", encoding="utf-8")


def mutate_output(path):
    edit(path, "DESTROYER: Entropy incinerated.", "DESTROYER: Entropy preserved.")


def mutate_unregister(path):
    edit(path, '@AgentFactory.register("DESTROYER")\n', "")


def mutate_base_class(path):
    edit(path, 'raise NotImplementedError("Agent vector must implement tactical logic.")', "return None")


def mutate_hardcode_priority(path):
    """The output the probe's first config expects, written as a fixed string: it ignores the config it was given."""
    edit(path, 'return f"CITADEL: Layer {self.config.priority} secured."', 'return "CITADEL: Layer 7 secured."')


MUTANTS = [mutate_to_trivial, mutate_to_empty, mutate_to_print_only, mutate_output, mutate_unregister,
           mutate_base_class, mutate_hardcode_priority]


def test_the_untouched_specimen_satisfies_the_claim(corpus):
    proc = run_verify(corpus)
    assert proc.returncode == 0, proc.stdout[-500:]
    assert "loads and its factory spawns the registered agents" in proc.stdout


def test_the_old_check_would_have_accepted_the_trivial_replacement(corpus):
    """Documents why the claim changed: a bare SystemExit(0) is a clean run that exits 0."""
    target = corpus / REL
    mutate_to_trivial(target)
    res = run_in_sandbox("script", target)
    assert res.exit_code == 0 and res.completed and res.clean and not res.error


@pytest.mark.parametrize("mutant", MUTANTS, ids=lambda f: f.__name__)
def test_a_replaced_specimen_fails_the_claim(corpus, mutant):
    mutant(corpus / REL)
    proc = run_verify(corpus)
    assert proc.returncode == 1, proc.stdout[-500:]
    failures = failing_claims(proc)
    assert CLAIM in failures, sorted(failures)
    assert failures[CLAIM]["reason"] in ("behaviour_changed", "specimen_error")


@pytest.mark.parametrize("mutant", MUTANTS, ids=lambda f: f.__name__)
def test_re_recording_refuses_a_replaced_specimen(corpus, mutant):
    registry = corpus / "assay_production" / "registry.json"
    before = registry.read_bytes()
    mutant(corpus / REL)
    proc = run_write(corpus)
    assert proc.returncode != 0 and "refusing to write" in proc.stdout, proc.stdout[-500:]
    assert "agent-factory-tactical-agents.py" in proc.stdout
    assert registry.read_bytes() == before, "a refused re-record must not change registry.json"


def test_the_asserted_facts_are_what_the_specimen_source_says():
    from assay_production.verification import AGENT_FACTORY_FACTS

    source = (ROOT / REL).read_text(encoding="utf-8")
    assert AGENT_FACTORY_FACTS["destroyer_says"] in source
    assert AGENT_FACTORY_FACTS["citadel_says"].replace("7", "{self.config.priority}") in source
    assert AGENT_FACTORY_FACTS["citadel_other_says"].replace("3", "{self.config.priority}") in source
    assert AGENT_FACTORY_FACTS["citadel_says"] != AGENT_FACTORY_FACTS["citadel_other_says"]
    for name in AGENT_FACTORY_FACTS["registry"]:
        assert f'@AgentFactory.register("{name}")' in source
