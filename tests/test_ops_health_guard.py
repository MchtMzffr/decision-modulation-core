"""Tests for ops-health guard."""

from dmc_core.dmc.guards_generic import ops_health_guard
from decision_schema.types import Action, MismatchInfo, Proposal
from dmc_core.dmc.modulator import modulate
from dmc_core.dmc.policy import GuardPolicy


def test_ops_health_guard_deny_actions() -> None:
    """Verify guard fails when ops_deny_actions is True."""
    ok, code = ops_health_guard(ops_deny_actions=True, ops_state=None, ops_cooldown_until_ms=None, now_ms=1000)
    assert ok is False
    assert code == "ops_deny_actions"


def test_ops_health_guard_red_state() -> None:
    """Verify guard fails when ops_state is RED."""
    ok, code = ops_health_guard(ops_deny_actions=None, ops_state="RED", ops_cooldown_until_ms=None, now_ms=1000)
    assert ok is False
    assert code == "ops_health_red"


def test_ops_health_guard_cooldown() -> None:
    """Verify guard fails during cooldown."""
    ok, code = ops_health_guard(
        ops_deny_actions=None, ops_state=None, ops_cooldown_until_ms=2000, now_ms=1000
    )
    assert ok is False
    assert code == "ops_cooldown_active"


def test_ops_health_guard_cooldown_expired() -> None:
    """Verify guard passes after cooldown expires."""
    ok, code = ops_health_guard(
        ops_deny_actions=None, ops_state=None, ops_cooldown_until_ms=1000, now_ms=2000
    )
    assert ok is True
    assert code == ""


def test_ops_health_guard_passes() -> None:
    """Verify guard passes when ops-health is healthy."""
    ok, code = ops_health_guard(
        ops_deny_actions=False, ops_state="GREEN", ops_cooldown_until_ms=None, now_ms=1000
    )
    assert ok is True
    assert code == ""


def test_modulator_with_ops_health_deny() -> None:
    """Verify modulator returns STOP when ops-health denies (GuardPolicy.fail_closed_action=STOP)."""
    proposal = Proposal(action=Action.ACT, confidence=0.8, reasons=["test"])
    policy = GuardPolicy(fail_closed_action=Action.STOP)
    context = {
        "now_ms": 1000,
        "last_event_ts_ms": 950,
        "ops_deny_actions": True,
    }
    final_decision, mismatch = modulate(proposal, policy, context)
    assert final_decision.action == Action.STOP
    assert "ops_health" in mismatch.flags
    assert "ops_deny_actions" in mismatch.reason_codes


def test_modulator_with_ops_health_red() -> None:
    """Verify modulator returns STOP when ops-health is RED."""
    proposal = Proposal(action=Action.ACT, confidence=0.8, reasons=["test"])
    policy = GuardPolicy(fail_closed_action=Action.STOP)
    context = {
        "now_ms": 1000,
        "last_event_ts_ms": 950,
        "ops_state": "RED",
    }
    final_decision, mismatch = modulate(proposal, policy, context)
    assert final_decision.action == Action.STOP
    assert "ops_health" in mismatch.flags
    assert "ops_health_red" in mismatch.reason_codes
