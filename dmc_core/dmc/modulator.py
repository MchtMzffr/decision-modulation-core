"""DMC: Apply guards and produce final action (possibly modified/override)."""

from __future__ import annotations

from dmc_core.schema import Action, TradeProposal, FinalAction, MismatchInfo
from dmc_core.dmc.risk_policy import RiskPolicy
from dmc_core.dmc.guards import (
    staleness_guard,
    liquidity_guard,
    spread_guard,
    exposure_guard,
    inventory_guard,
    cancel_rate_guard,
    daily_loss_guard,
    error_rate_guard,
    circuit_breaker_guard,
    adverse_selection_guard,
    adverse_selection_ticks_guard,
    sigma_spike_guard,
    cost_guard,
    ops_health_guard,
)


def modulate(
    proposal: TradeProposal,
    policy: RiskPolicy,
    context: dict,
) -> tuple[FinalAction, MismatchInfo]:
    """
    Apply all guards. On first fail: override to HOLD or FLATTEN/CANCEL_ALL/STOP
    and set mismatch. Otherwise pass through (possibly clamp size).
    
    Supports private policy override via dmc_core._private.policy.override_policy.
    On private hook error: fail-closed (safe defaults).
    """
    # Try private policy override
    policy = _apply_private_policy_override(policy, context)
    
    mismatch_flags: list[str] = []
    reason_codes: list[str] = []

    now_ms = context.get("now_ms", 0)
    last_event_ts_ms = context.get("last_event_ts_ms", now_ms)
    depth = context.get("depth", 0.0)
    spread_bps = context.get("spread_bps", 0.0)
    current_total_exposure_usd = context.get("current_total_exposure_usd", 0.0)
    abs_inventory = context.get("abs_inventory", 0.0)

    # FLATTEN only when there is a position; else HOLD (avoid spurious cancel)
    if proposal.action == Action.FLATTEN and abs_inventory == 0:
        return FinalAction(action=Action.HOLD), MismatchInfo(
            flags=["flatten_no_position"],
            reason_codes=["no_inventory_to_flatten"],
        )
    cancels_in_window = context.get("cancels_in_window", 0)
    daily_realized_pnl_usd = context.get("daily_realized_pnl_usd", 0.0)
    errors_in_window = context.get("errors_in_window", 0)
    steps_in_window = context.get("steps_in_window", 1)
    recent_failures = context.get("recent_failures", 0)
    adverse_selection_avg = context.get("adverse_selection_avg", 0.0)
    sigma_spike_z = context.get("sigma_spike_z", 0.0)
    cost_ticks = context.get("cost_ticks", 0.0)
    tp_ticks = context.get("tp_ticks", 1.0)

    # Ops-health guard (early check - operational safety)
    ops_deny_actions = context.get("ops_deny_actions")
    ops_state = context.get("ops_state")
    ops_cooldown_until_ms = context.get("ops_cooldown_until_ms")
    ok, code = ops_health_guard(ops_deny_actions, ops_state, ops_cooldown_until_ms, now_ms)
    if not ok:
        mismatch_flags.append("ops_health")
        reason_codes.append(code)
        # Ops-health failure → STOP (most severe)
        return FinalAction(action=Action.STOP), MismatchInfo(flags=mismatch_flags, reason_codes=reason_codes)

    # Staleness
    ok, code = staleness_guard(last_event_ts_ms, now_ms, policy.staleness_ms)
    if not ok:
        mismatch_flags.append("staleness")
        reason_codes.append(code)
        return FinalAction(action=Action.HOLD), MismatchInfo(flags=mismatch_flags, reason_codes=reason_codes)

    # Liquidity
    ok, code = liquidity_guard(depth, policy.min_depth)
    if not ok:
        mismatch_flags.append("liquidity")
        reason_codes.append(code)
        return FinalAction(action=Action.HOLD), MismatchInfo(flags=mismatch_flags, reason_codes=reason_codes)

    # Spread
    ok, code = spread_guard(spread_bps, policy.max_spread_bps)
    if not ok:
        mismatch_flags.append("spread")
        reason_codes.append(code)
        return FinalAction(action=Action.HOLD), MismatchInfo(flags=mismatch_flags, reason_codes=reason_codes)

    # Exposure
    ok, code = exposure_guard(current_total_exposure_usd, policy.max_total_exposure_usd)
    if not ok:
        mismatch_flags.append("exposure")
        reason_codes.append(code)
        return FinalAction(action=Action.FLATTEN), MismatchInfo(flags=mismatch_flags, reason_codes=reason_codes)

    # Inventory
    ok, code = inventory_guard(abs_inventory, policy.max_abs_inventory)
    if not ok:
        mismatch_flags.append("inventory")
        reason_codes.append(code)
        return FinalAction(action=Action.FLATTEN), MismatchInfo(flags=mismatch_flags, reason_codes=reason_codes)

    # Cancel rate (throttle: caller should use policy.throttle_refresh_ms for next refresh)
    ok, code = cancel_rate_guard(cancels_in_window, policy.cancel_rate_limit)
    if not ok:
        mismatch_flags.append("cancel_rate")
        reason_codes.append(code)
        return FinalAction(action=Action.HOLD), MismatchInfo(
            flags=mismatch_flags,
            reason_codes=reason_codes,
            throttle_refresh_ms=getattr(policy, "throttle_refresh_ms", 1500),
        )

    # Daily loss
    ok, code = daily_loss_guard(daily_realized_pnl_usd, policy.daily_loss_stop_usd)
    if not ok:
        mismatch_flags.append("daily_loss")
        reason_codes.append(code)
        return FinalAction(action=Action.STOP), MismatchInfo(flags=mismatch_flags, reason_codes=reason_codes)

    # Error rate
    ok, code = error_rate_guard(errors_in_window, steps_in_window, policy.error_rate_max)
    if not ok:
        mismatch_flags.append("error_rate")
        reason_codes.append(code)
        return FinalAction(action=Action.HOLD), MismatchInfo(flags=mismatch_flags, reason_codes=reason_codes)

    # Circuit breaker
    ok, code = circuit_breaker_guard(recent_failures, policy.circuit_breaker_failures)
    if not ok:
        mismatch_flags.append("circuit_breaker")
        reason_codes.append(code)
        return FinalAction(action=Action.STOP), MismatchInfo(flags=mismatch_flags, reason_codes=reason_codes)

    # Adverse selection: ticks-based (15/60s) when available, else legacy
    adv15 = context.get("adverse_15_ticks")
    adv60 = context.get("adverse_60_ticks")
    if adv15 is not None and adv60 is not None:
        max15 = getattr(policy, "adv15_max_ticks", 1.0)
        max60 = getattr(policy, "adv60_max_ticks", 2.0)
        ok, code = adverse_selection_ticks_guard(adv15, adv60, max15, max60)
    else:
        adverse_max = getattr(policy, "adverse_selection_max", 0.005)
        ok, code = adverse_selection_guard(adverse_selection_avg, adverse_max)
    if not ok:
        mismatch_flags.append("adverse_selection")
        reason_codes.append(code)
        return FinalAction(action=Action.HOLD), MismatchInfo(flags=mismatch_flags, reason_codes=reason_codes)

    # Vol spike (short vs long sigma)
    z_max = getattr(policy, "sigma_spike_z_max", 2.5)
    ok, code = sigma_spike_guard(sigma_spike_z, z_max)
    if not ok:
        mismatch_flags.append("sigma_spike")
        reason_codes.append(code)
        return FinalAction(action=Action.HOLD), MismatchInfo(flags=mismatch_flags, reason_codes=reason_codes)

    # Cost gate (tp must exceed cost + min profit)
    policy_cost = getattr(policy, "cost_ticks", 1.0)
    min_profit = getattr(policy, "min_profit_ticks", 1.0)
    ok, code = cost_guard(tp_ticks, policy_cost, min_profit)
    if not ok:
        mismatch_flags.append("cost")
        reason_codes.append(code)
        return FinalAction(action=Action.HOLD), MismatchInfo(flags=mismatch_flags, reason_codes=reason_codes)

    # All passed: pass through (clamp size to policy if QUOTE)
    if proposal.action == Action.QUOTE and proposal.size_usd is not None:
        size_usd = min(proposal.size_usd, policy.max_per_market_usd)
        return (
            FinalAction(
                action=Action.QUOTE,
                bid_quote=proposal.bid_quote,
                ask_quote=proposal.ask_quote,
                size_usd=size_usd,
                post_only=proposal.post_only,
            ),
            MismatchInfo(),
        )
    return (
        FinalAction(
            action=proposal.action,
            bid_quote=proposal.bid_quote,
            ask_quote=proposal.ask_quote,
            size_usd=proposal.size_usd,
            post_only=proposal.post_only,
        ),
        MismatchInfo(),
    )


def _apply_private_policy_override(policy: RiskPolicy, context: dict) -> RiskPolicy:
    """
    Private policy hook: import from dmc_core._private.policy if exists.
    
    On ImportError: silent fallback (expected).
    On runtime exception: fail-closed (return original policy).
    """
    try:
        from dmc_core._private.policy import override_policy
        return override_policy(policy, context)
    except ImportError:
        # Private hook not available - silent fallback (expected)
        return policy
    except Exception as e:
        # Private hook runtime error - fail-closed
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"🔒 Private DMC policy hook error, using public defaults: {type(e).__name__}")
        return policy  # Return original policy (fail-closed)
