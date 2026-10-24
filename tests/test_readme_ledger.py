"""The README's evidence and ledger point at things that exist, and the README keeps the sections it promises.

A claim of "works" in the README names a test, a CI job or a command. This file fails if a named test is gone, if the
ledger cites a version the CHANGELOG does not have, or if marketing words come back.
"""
import re

from conftest import ROOT

README = (ROOT / "README.md").read_text(encoding="utf-8")
CHANGELOG = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")

REQUIRED_HEADINGS = (
    "## What This Is",
    "### What works, and what shows it",
    "### What does not work, or is not proven",
    "### Known defects (open)",
    "## 11. What Broke and How It Was Fixed",
    "## 12. Self-Hosting",
    "## 13. Ceilings Code Cannot Fix",
)
BANNED_WORDS = ("robust", "powerful", "production-ready", "production ready", "seamless", "comprehensive",
                "blazing", "enterprise", "battle-tested", "state-of-the-art")


def section(title_start: str) -> str:
    start = README.index(title_start)
    following = re.search(r"^## ", README[start + 1:], re.M)
    return README[start:start + 1 + following.start()] if following else README[start:]


def test_the_readme_keeps_the_sections_it_promises_in_order():
    positions = [README.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)
    assert all(README.count(heading) == 1 for heading in REQUIRED_HEADINGS)


def test_every_test_the_readme_names_exists():
    named = set(re.findall(r"`(tests/test_\w+\.py)(?:::(\w+))?`", README))
    assert named, "the README names no tests"
    for path, function in named:
        source = (ROOT / path).read_text(encoding="utf-8")
        if function:
            assert re.search(rf"^\s*def {function}\(", source, re.M), f"{path}::{function} is named in the README"


def test_tests_named_by_function_alone_in_the_ledger_exist_in_the_file_just_named():
    tests = {path.name: path.read_text(encoding="utf-8") for path in (ROOT / "tests").glob("test_*.py")}
    everything = "\n".join(tests.values())
    ledger = section("## 11. What Broke and How It Was Fixed")
    for function in re.findall(r"`(test_\w+)`", ledger):
        assert re.search(rf"^\s*def {function}\(", everything, re.M), function


def test_every_version_in_the_ledger_is_a_changelog_heading():
    ledger = section("## 11. What Broke and How It Was Fixed")
    headings = set(re.findall(r"^## \[([^\]]+)\]", CHANGELOG, re.M))
    cited = set(re.findall(r"^\*\*(\d+\.\d+\.\d+)\*\*", ledger, re.M))
    assert cited and cited <= headings, (cited, headings)
    mentioned = set(re.findall(r"\b0\.\d+\.\d+\b", ledger))
    assert mentioned <= headings, mentioned - headings


def test_every_ci_job_the_readme_names_is_in_the_workflow():
    for job in re.findall(r"`(pytest|consumers|baseline|wheel)`", README):
        assert re.search(rf"^  {job}:", WORKFLOW, re.M), job


def test_the_readme_uses_no_marketing_words():
    lowered = README.lower()
    found = [word for word in BANNED_WORDS if word in lowered]
    assert not found, found


def test_the_readme_names_the_pinned_cns_and_its_commit_once_in_the_migration_note():
    assert "from `v1.9.0` to `v2.0.0`" in README
    assert "b13e5d2f9e0e4291725f82794b89117c3d840ac1" in README


# What the self-hosting record says about this repository. Copied from the CNS repository's
# docs/evidence/SELFHOSTING_2026-10-23.md (branch claude/horsemen-production-status-5wsndb until merged), ASSAY row
# and "What each non-ACCEPT means". If the record is replaced by a newer run, change these and the README together.
SELFHOSTING_EVIDENCE = "docs/evidence/SELFHOSTING_2026-10-23.md"
SELFHOSTING_FACTS = (
    "184679c06e0a636a9a08a8403efa410b375c9429",   # commit the run was made at
    "version 0.11.5",
    "its decision is REJECT",
    "34 of the 104 entries",                      # stale baseline entries
    "7 declined checks",
    "12 gaps in all",
    "89 Ghost findings still reported",
)


def test_the_self_hosting_section_states_what_the_record_holds_and_what_it_does_not_mean():
    text = " ".join(section("## 12. Self-Hosting").split())
    assert SELFHOSTING_EVIDENCE in text and "claude/horsemen-production-status-5wsndb" in text
    for fact in SELFHOSTING_FACTS:
        assert fact in text, fact
    for declined in ("mutate", "kernel", "structure", "tests", "project", "secrets", "correlate"):
        assert declined in text, declined
    assert "does not cover 0.11.6" in text
    assert "does not mean there are no secrets or weak tests" in text
    assert "no fresh" not in text.lower() and "not been established" not in text
