"""Tests for ops-health guard."""

from dmc_core.dmc.guards import ops_health_guard
from dmc_core.schema import Action, FinalAction, MismatchInfo, TradeProposal
from dmc_core.dmc.modulator import modulate
from dmc_core.dmc.risk_policy import RiskPolicy


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
    """Verify modulator returns STOP when ops-health denies."""
    proposal = TradeProposal(action=Action.ACT, confidence=0.8, reasons=["test"])
    policy = RiskPolicy()
    context = {
        "now_ms": 1000,
        "last_event_ts_ms": 950,
        "depth": 100.0,
        "spread_bps": 400.0,
        "current_total_exposure_usd": 5.0,
        "abs_inventory": 2.0,
        "ops_deny_actions": True,  # Ops-health denies
    }

    final_action, mismatch = modulate(proposal, policy, context)
    assert final_action.action == Action.STOP
    assert "ops_health" in mismatch.flags
    assert "ops_deny_actions" in mismatch.reason_codes


def test_modulator_with_ops_health_red() -> None:
    """Verify modulator returns STOP when ops-health is RED."""
    proposal = TradeProposal(action=Action.ACT, confidence=0.8, reasons=["test"])
    policy = RiskPolicy()
    context = {
        "now_ms": 1000,
        "last_event_ts_ms": 950,
        "depth": 100.0,
        "spread_bps": 400.0,
        "current_total_exposure_usd": 5.0,
        "abs_inventory": 2.0,
        "ops_state": "RED",  # Ops-health RED
    }

    final_action, mismatch = modulate(proposal, policy, context)
    assert final_action.action == Action.STOP
    assert "ops_health" in mismatch.flags
    assert "ops_health_red" in mismatch.reason_codes
