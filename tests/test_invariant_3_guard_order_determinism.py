# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""
INVARIANT 3: Deterministic guard ordering.

Same (proposal, context, policy) must yield same (final_decision, mismatch).
Guard list order is fixed (GUARD_ORDER); no reorder.
"""

from decision_schema.types import Action, Proposal

from dmc_core.dmc.guards_generic import GUARD_ORDER
from dmc_core.dmc.modulator import modulate
from dmc_core.dmc.policy import GuardPolicy


def test_guard_order_is_fixed() -> None:
    """GUARD_ORDER is defined and non-empty."""
    assert len(GUARD_ORDER) >= 1
    assert "ops_health" in GUARD_ORDER
    assert "staleness" in GUARD_ORDER


def test_same_input_same_output() -> None:
    """Same (proposal, context, policy) -> same (FinalDecision, MismatchInfo)."""
    proposal = Proposal(action=Action.ACT, confidence=0.8, reasons=["test"])
    policy = GuardPolicy(staleness_ms=10_000, fail_closed_action=Action.HOLD)
    context = {
        "now_ms": 5000,
        "last_event_ts_ms": 4000,
        "errors_in_window": 0,
        "steps_in_window": 100,
        "rate_limit_events": 0,
        "recent_failures": 0,
    }

    out1 = modulate(proposal, policy, context)
    out2 = modulate(proposal, policy, context)

    assert out1[0].action == out2[0].action
    assert out1[0].allowed == out2[0].allowed
    assert out1[1].flags == out2[1].flags
    assert out1[1].reason_codes == out2[1].reason_codes


def test_staleness_fail_deterministic() -> None:
    """Staleness fail always yields same override."""
    proposal = Proposal(action=Action.ACT, confidence=0.9)
    policy = GuardPolicy(staleness_ms=100, fail_closed_action=Action.HOLD)
    context = {
        "now_ms": 10_000,
        "last_event_ts_ms": 1,  # very stale
        "errors_in_window": 0,
        "steps_in_window": 1,
        "rate_limit_events": 0,
        "recent_failures": 0,
    }

    final, mismatch = modulate(proposal, policy, context)
    assert final.allowed is False
    assert final.action == Action.HOLD
    assert "staleness" in mismatch.flags
