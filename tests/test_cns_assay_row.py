"""The connector reads the verifier's summary through CNS's shared ``cns.assay`` row where there is one.

The pinned CNS (v2.3.0) has such a row; a CNS without one (v1.8.0 and earlier) makes the connector rely on its own
reading alone. The first group uses a stand-in row so it runs against any installed CNS; the second uses the real
row when the installed CNS has it.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import types

import pytest

gate = pytest.importorskip("cns.gate")

from assay_production import cns_connector as cc  # noqa: E402
from assay_production.cns_connector import AssayKeyGate, assay_row_available  # noqa: E402
from assay_production.verification import SUMMARY_PREFIX  # noqa: E402
from test_cns_connector import proven_record, runner_returning, said  # noqa: E402

REAL_ROW_INSTALLED = importlib.util.find_spec("cns.assay") is not None


def stand_in_row(refuse: str = "") -> types.ModuleType:
    """A ``cns.assay`` look-alike that records what it is given and refuses with ``refuse`` if that is set."""
    row = types.ModuleType("cns.assay")
    seen: list = []

    class AssaySummary:
        @staticmethod
        def from_dict(data):
            seen.append(data)
            if refuse:
                raise ValueError(refuse)
            return data

    setattr(row, "AssaySummary", AssaySummary)  # noqa: B010 - building a module look-alike
    setattr(row, "seen", seen)  # noqa: B010
    return row


def summary_line(record: dict) -> str:
    return "60/60 manifest claims hold\n" + SUMMARY_PREFIX + json.dumps(record)


# ------------------------------------------------------------ with a stand-in row

def test_the_summary_is_handed_to_the_row_and_a_row_that_accepts_changes_nothing(monkeypatch, corpus):
    row = stand_in_row()
    monkeypatch.setitem(sys.modules, "cns.assay", row)
    result = AssayKeyGate(runner=runner_returning(said(proven_record()))).check(corpus)
    assert result.outcome is gate.GateOutcome.PASS, result.reason
    assert row.seen == [proven_record()]


def test_a_row_that_refuses_a_summary_the_connector_accepted_is_a_breach(monkeypatch, corpus):
    monkeypatch.setitem(sys.modules, "cns.assay", stand_in_row("status is empty"))
    result = AssayKeyGate(runner=runner_returning(said(proven_record()))).check(corpus)
    assert result.outcome is gate.GateOutcome.TERMINAL_BREACH
    assert "shared cns.assay row" in result.reason and "status is empty" in result.reason


def test_a_refusing_row_is_not_asked_when_the_connector_has_already_refused(monkeypatch):
    row = stand_in_row("never reached")
    monkeypatch.setitem(sys.modules, "cns.assay", row)
    with pytest.raises(ValueError, match="documented fields"):
        cc._read_summary(summary_line({"schema": proven_record()["schema"]}))
    assert row.seen == []


def test_the_row_is_asked_at_read_time_not_at_import(monkeypatch):
    monkeypatch.setitem(sys.modules, "cns.assay", stand_in_row())
    assert assay_row_available() is True


def test_where_cns_has_no_row_the_connector_still_reads_the_summary(monkeypatch, corpus):
    monkeypatch.setitem(sys.modules, "cns.assay", None)  # makes any import of it fail
    assert assay_row_available() is False
    result = AssayKeyGate(runner=runner_returning(said(proven_record()))).check(corpus)
    assert result.outcome is gate.GateOutcome.PASS, result.reason


def test_without_a_row_the_connectors_own_refusals_still_hold(monkeypatch, corpus):
    monkeypatch.setitem(sys.modules, "cns.assay", None)
    result = AssayKeyGate(runner=runner_returning(said(proven_record(schema="assay-summary/2")))).check(corpus)
    assert result.outcome is gate.GateOutcome.TERMINAL_BREACH


# ------------------------------------------------------------ with the installed CNS

def test_the_installed_cns_row_and_the_connector_agree_on_a_real_summary(corpus):
    assert assay_row_available() is REAL_ROW_INSTALLED
    result = AssayKeyGate(runner=runner_returning(said(proven_record()))).check(corpus)
    assert result.outcome is gate.GateOutcome.PASS, result.reason
    if REAL_ROW_INSTALLED:
        from cns.assay import AssaySummary
        row = AssaySummary.from_dict(proven_record())
        assert row.all_claims_hold is True and row.schema == proven_record()["schema"]


def test_the_installed_row_refuses_what_the_connector_alone_would_let_through():
    """A blank status passes the connector's own field checks; the shared row says it cannot be read."""
    blank = proven_record(status="  ")
    if REAL_ROW_INSTALLED:
        with pytest.raises(ValueError, match="shared cns.assay row"):
            cc._read_summary(summary_line(blank))
    else:
        read = cc._read_summary(summary_line(blank))
        assert read is not None and read["status"] == "  "
