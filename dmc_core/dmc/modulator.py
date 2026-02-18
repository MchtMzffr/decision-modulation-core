# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""
DMC: Apply generic guards and produce FinalDecision. Domain-agnostic.

INVARIANT 3: Guard order is fixed (see guards/__init__.py GUARD_ORDER).
INVARIANT 4: On exception → fail-closed (allowed=False, action=policy.fail_closed_action).
"""

from __future__ import annotations

import logging

from decision_schema.types import Action, FinalDecision, MismatchInfo, Proposal

from dmc_core.dmc.policy import GuardPolicy
from dmc_core.dmc.guards_generic import (
    GUARD_ORDER,
    ops_health_guard,
    staleness_guard,
    error_rate_guard,
    rate_limit_guard,
    circuit_breaker_guard,
    cooldown_guard,
)

logger = logging.getLogger(__name__)


def modulate(
    proposal: Proposal,
    policy: GuardPolicy,
    context: dict,
) -> tuple[FinalDecision, MismatchInfo]:
    """
    Apply guards in fixed order. First failure → override to fail_closed_action
    and return (FinalDecision(allowed=False), MismatchInfo). Otherwise pass through.

    Context keys (generic): now_ms, last_event_ts_ms, ops_deny_actions, ops_state,
    ops_cooldown_until_ms, errors_in_window, steps_in_window, rate_limit_events,
    recent_failures, cooldown_until_ms.
    """
    try:
        return _modulate_impl(proposal, policy, context)
    except Exception as e:
        logger.warning("DMC modulate exception, fail-closed: %s", type(e).__name__)
        return _fail_closed(policy), MismatchInfo(
            flags=["modulate_exception"],
            reason_codes=[type(e).__name__],
        )


def _fail_closed(policy: GuardPolicy) -> FinalDecision:
    """INVARIANT 4: allowed=False, action in {HOLD, STOP}."""
    action = policy.fail_closed_action
    if action not in (Action.HOLD, Action.STOP):
        action = Action.HOLD
    return FinalDecision(allowed=False, action=action, reasons=["fail_closed"])


def _modulate_impl(
    proposal: Proposal,
    policy: GuardPolicy,
    context: dict,
) -> tuple[FinalDecision, MismatchInfo]:
    now_ms = context.get("now_ms", 0)
    last_event_ts_ms = context.get("last_event_ts_ms", now_ms)
    mismatch_flags: list[str] = []
    reason_codes: list[str] = []

    # 1. ops_health
    ok, code = ops_health_guard(
        context.get("ops_deny_actions"),
        context.get("ops_state"),
        context.get("ops_cooldown_until_ms"),
        now_ms,
    )
    if not ok:
        mismatch_flags.append("ops_health")
        reason_codes.append(code)
        return _override_decision(proposal, policy, mismatch_flags, reason_codes)

    # 2. staleness
    ok, code = staleness_guard(last_event_ts_ms, now_ms, policy.staleness_ms)
    if not ok:
        mismatch_flags.append("staleness")
        reason_codes.append(code)
        return _override_decision(proposal, policy, mismatch_flags, reason_codes)

    # 3. error_rate
    ok, code = error_rate_guard(
        context.get("errors_in_window", 0),
        context.get("steps_in_window", 1),
        policy.max_error_rate,
    )
    if not ok:
        mismatch_flags.append("error_rate")
        reason_codes.append(code)
        return _override_decision(proposal, policy, mismatch_flags, reason_codes)

    # 4. rate_limit
    ok, code = rate_limit_guard(
        context.get("rate_limit_events", 0),
        policy.rate_limit_events_max,
    )
    if not ok:
        mismatch_flags.append("rate_limit")
        reason_codes.append(code)
        return _override_decision(proposal, policy, mismatch_flags, reason_codes)

    # 5. circuit_breaker
    ok, code = circuit_breaker_guard(
        context.get("recent_failures", 0),
        policy.circuit_breaker_failures,
    )
    if not ok:
        mismatch_flags.append("circuit_breaker")
        reason_codes.append(code)
        return _override_decision(proposal, policy, mismatch_flags, reason_codes)

    # 6. cooldown
    ok, code = cooldown_guard(context.get("cooldown_until_ms"), now_ms)
    if not ok:
        mismatch_flags.append("cooldown")
        reason_codes.append(code)
        return _override_decision(proposal, policy, mismatch_flags, reason_codes)

    # All passed
    return (
        FinalDecision(
            action=proposal.action,
            allowed=True,
            reasons=proposal.reasons or [],
        ),
        MismatchInfo(),
    )


def _override_decision(
    proposal: Proposal,
    policy: GuardPolicy,
    flags: list[str],
    reason_codes: list[str],
) -> tuple[FinalDecision, MismatchInfo]:
    action = policy.fail_closed_action
    if action not in (Action.HOLD, Action.STOP):
        action = Action.HOLD
    mi = MismatchInfo(flags=flags, reason_codes=reason_codes)
    return (
        FinalDecision(action=action, allowed=False, reasons=reason_codes, mismatch=mi),
        mi,
    )
