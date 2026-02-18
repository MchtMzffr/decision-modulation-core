# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""
INVARIANT 4: Fail-closed.

On exception in modulate -> FinalDecision.allowed=False and action in {HOLD, STOP}.
"""

from decision_schema.types import Action, Proposal

from dmc_core.dmc.modulator import modulate
from dmc_core.dmc.policy import GuardPolicy


def test_fail_closed_on_bad_context() -> None:
    """Guard failure yields allowed=False and action HOLD or STOP."""
    proposal = Proposal(action=Action.ACT, confidence=0.8)
    policy = GuardPolicy(fail_closed_action=Action.HOLD)
    context = {
        "now_ms": 1000,
        "last_event_ts_ms": 0,
        "ops_deny_actions": True,  # ops_health will fail
    }
    final, mismatch = modulate(proposal, policy, context)
    assert final.allowed is False
    assert final.action in (Action.HOLD, Action.STOP)
    assert "ops_health" in mismatch.flags


def test_fail_closed_action_respected() -> None:
    """policy.fail_closed_action=STOP yields action STOP on guard fail."""
    proposal = Proposal(action=Action.ACT, confidence=0.8)
    policy = GuardPolicy(fail_closed_action=Action.STOP)
    context = {
        "now_ms": 1000,
        "last_event_ts_ms": 0,
        "ops_deny_actions": True,
    }
    final, _ = modulate(proposal, policy, context)
    assert final.allowed is False
    assert final.action == Action.STOP


def test_all_pass_allowed_true() -> None:
    """When all guards pass, allowed=True and proposal action preserved."""
    proposal = Proposal(action=Action.ACT, confidence=0.7)
    policy = GuardPolicy(staleness_ms=60_000)
    context = {
        "now_ms": 5000,
        "last_event_ts_ms": 4000,
        "errors_in_window": 0,
        "steps_in_window": 10,
        "rate_limit_events": 0,
        "recent_failures": 0,
    }
    final, mismatch = modulate(proposal, policy, context)
    assert final.allowed is True
    assert final.action == Action.ACT
    assert not mismatch.flags


def test_exception_fail_closed() -> None:
    """INVARIANT 4: Exception inside modulate -> allowed=False, action HOLD or STOP."""
    proposal = Proposal(action=Action.ACT, confidence=0.8)
    policy = GuardPolicy(fail_closed_action=Action.HOLD)
    # Pass invalid type to trigger exception in a guard (e.g. staleness expects int)
    context = {
        "now_ms": 1000,
        "last_event_ts_ms": "not_an_int",  # type error in staleness_guard
    }
    final, mismatch = modulate(proposal, policy, context)
    assert final.allowed is False
    assert final.action in (Action.HOLD, Action.STOP)
    assert "modulate_exception" in mismatch.flags or mismatch.reason_codes
