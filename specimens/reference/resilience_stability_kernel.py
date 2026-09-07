# =============================================================================
# RESILIENCE STABILITY KERNEL - shared weighted-deviation energy primitive
#
# Built 2026-09-03 during the SRE/URE reconciliation pass. Both
# solvar_stability_governance_adapter.py (LyapunovStabilityModule) and the
# flattened sre-system-resilience-evaluator-flattened.py (SystemStabilityValidator)
# independently implement the same function: sum of weight * (current - baseline)^2
# across a metric vector, classified into stable / marginal / unstable against the
# same two threshold constants (1e-4, 1e-2) in both places. That isn't
# coincidence - it's the same design, copy-pasted and reskinned per source repo.
#
# This module is the one tested implementation of that shared piece. It does NOT
# replace either engine's domain-specific front end: SOLVAR's cohort/IVR
# projection stays in solvar_stability_governance_adapter.py, untouched. Only
# sre_system_resilience_evaluator_adapter.py (reconstructed alongside this file)
# is wired to call in here, and its numeric output is unchanged from a literal
# reconstruction of the flattened SRE source - same weights, same field mapping,
# same default thresholds. The formula itself is de-duplicated and its
# thresholds are promoted from hardcoded literals to one configurable dataclass.
#
# ure-universal-resilience-engine-flattened.py's own version of this same idea is
# NOT wired in here: its regime classifier is hardcoded rather than derived from
# its inputs (see governance-stack/archive/README.md), so it isn't a source of
# real logic to share, and nothing in this repo consumes it.
# =============================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass
class StabilityThresholds:
    """Tunable sensitivity for the shared energy-drift stability check.

    Field names and default values match the two constants SOLVAR and SRE
    already hardcoded identically (1e-4 / 1e-2), plus SRE's own DEGRADED /
    CRITICAL cutoffs (0.10 / 0.75) - shaped after
    ure-universal-resilience-engine-flattened.py's SystemResilienceConfig
    dataclass, trimmed to only the fields this kernel and SRE actually use.
    """

    stable_threshold: float = 1e-4
    marginal_threshold: float = 1e-2
    degraded_energy_threshold: float = 0.10
    critical_risk_threshold: float = 0.75


def weighted_deviation_energy(
    baseline: Mapping[str, float],
    current: Mapping[str, float],
    weights: Mapping[str, float],
) -> float:
    """Sum of weight * (current[k] - baseline[k]) ** 2 over every key in weights.

    The shared primitive behind SOLVAR's LyapunovStabilityModule and SRE's
    SystemStabilityValidator.calculate_variance_energy - same formula shape,
    generalized to an arbitrary metric/weight mapping instead of a hardcoded
    field list, so each caller keeps its own field names and weights.
    """
    total = 0.0
    for key, weight in weights.items():
        delta = float(current.get(key, 0.0)) - float(baseline.get(key, 0.0))
        total += weight * (delta ** 2)
    return total


def classify_energy_state(
    energy: float,
    thresholds: StabilityThresholds = StabilityThresholds(),
) -> str:
    """Maps a computed energy scalar to stable / marginal / unstable."""
    if energy <= thresholds.stable_threshold:
        return "stable"
    if energy <= thresholds.marginal_threshold:
        return "marginal"
    return "unstable"


if __name__ == "__main__":
    import random

    print("--- resilience_stability_kernel property checks ---")

    weights = {"a": 5.0, "b": 2.0, "c": 1.0}

    # zero drift -> zero energy, always "stable"
    zero_vec = {"a": 1.0, "b": 2.0, "c": 3.0}
    energy_zero = weighted_deviation_energy(zero_vec, zero_vec, weights)
    assert energy_zero == 0.0, f"expected zero energy for identical vectors, got {energy_zero}"
    assert classify_energy_state(energy_zero) == "stable"

    # non-negativity and baseline/current symmetry (squared deltas), random vectors
    for _ in range(200):
        baseline = {k: random.uniform(-10, 10) for k in weights}
        current = {k: random.uniform(-10, 10) for k in weights}
        forward = weighted_deviation_energy(baseline, current, weights)
        backward = weighted_deviation_energy(current, baseline, weights)
        assert forward >= 0.0, f"energy must be non-negative, got {forward}"
        assert abs(forward - backward) < 1e-9, "energy must be symmetric in baseline/current"

    # monotonicity: scaling the delta must not decrease energy
    baseline = {"a": 0.0, "b": 0.0, "c": 0.0}
    small = {"a": 0.01, "b": 0.01, "c": 0.01}
    large = {"a": 0.5, "b": 0.5, "c": 0.5}
    e_small = weighted_deviation_energy(baseline, small, weights)
    e_large = weighted_deviation_energy(baseline, large, weights)
    assert e_large > e_small, "larger deviation must yield larger energy"

    # threshold boundaries land where documented
    t = StabilityThresholds()
    assert classify_energy_state(t.stable_threshold, t) == "stable"
    assert classify_energy_state(t.stable_threshold + 1e-12, t) == "marginal"
    assert classify_energy_state(t.marginal_threshold, t) == "marginal"
    assert classify_energy_state(t.marginal_threshold + 1e-9, t) == "unstable"

    print(f"zero-drift energy: {energy_zero} -> {classify_energy_state(energy_zero)}")
    print(f"small-drift energy: {e_small:.6f} -> {classify_energy_state(e_small)}")
    print(f"large-drift energy: {e_large:.6f} -> {classify_energy_state(e_large)}")
    print("all property checks passed")
