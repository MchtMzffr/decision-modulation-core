# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""
Legacy domain guards — example only. Not part of core.
Import from decision_schema.types (domain-agnostic contract).
"""

from __future__ import annotations

import math
from decision_schema.types import Action, Proposal


def staleness_guard(
    last_event_ts_ms: int,
    now_ms: int,
    staleness_ms: int,
) -> tuple[bool, str]:
    if now_ms - last_event_ts_ms > staleness_ms:
        return False, "staleness_exceeded"
    return True, ""


def liquidity_guard(depth: float, min_depth: float) -> tuple[bool, str]:
    if depth < min_depth:
        return False, "liquidity_low"
    return True, ""


def spread_guard(spread_bps: float, max_spread_bps: float) -> tuple[bool, str]:
    if spread_bps > max_spread_bps:
        return False, "spread_wide"
    return True, ""


def exposure_guard(
    current_total_exposure_usd: float,
    max_total_exposure_usd: float,
) -> tuple[bool, str]:
    if current_total_exposure_usd > max_total_exposure_usd:
        return False, "exposure_cap"
    return True, ""


def inventory_guard(
    abs_inventory: float,
    max_abs_inventory: float,
) -> tuple[bool, str]:
    if abs_inventory > max_abs_inventory:
        return False, "inventory_cap"
    return True, ""


def cancel_rate_guard(
    cancels_in_window: int,
    cancel_rate_limit: int,
) -> tuple[bool, str]:
    if cancels_in_window >= cancel_rate_limit:
        return False, "cancel_rate_throttle"
    return True, ""


def daily_loss_guard(
    daily_realized_pnl_usd: float,
    daily_loss_stop_usd: float,
) -> tuple[bool, str]:
    if daily_realized_pnl_usd <= -abs(daily_loss_stop_usd):
        return False, "daily_loss_stop"
    return True, ""


def error_rate_guard(
    errors_in_window: int,
    steps_in_window: int,
    error_rate_max: float,
) -> tuple[bool, str]:
    if steps_in_window <= 0:
        return True, ""
    rate = errors_in_window / steps_in_window
    if rate > error_rate_max:
        return False, "error_rate_high"
    return True, ""


def circuit_breaker_guard(
    recent_failures: int,
    circuit_breaker_failures: int,
) -> tuple[bool, str]:
    if recent_failures >= circuit_breaker_failures:
        return False, "circuit_breaker"
    return True, ""


def adverse_selection_guard(
    adverse_selection_avg: float,
    adverse_selection_max: float,
) -> tuple[bool, str]:
    if adverse_selection_avg > adverse_selection_max:
        return False, "adverse_selection_high"
    return True, ""


def adverse_selection_ticks_guard(
    adv15_ticks: float,
    adv60_ticks: float,
    max15_ticks: float,
    max60_ticks: float,
) -> tuple[bool, str]:
    if adv15_ticks > max15_ticks:
        return False, "adverse_selection_high_15"
    if adv60_ticks > max60_ticks:
        return False, "adverse_selection_high_60"
    return True, ""


def sigma_spike_guard(z: float, z_max: float) -> tuple[bool, str]:
    if z > z_max:
        return False, "sigma_spike"
    return True, ""


def cost_guard(tp_ticks: float, cost_ticks: float, min_profit_ticks: float = 1.0) -> tuple[bool, str]:
    required_tp = math.ceil(cost_ticks + min_profit_ticks)
    if tp_ticks < required_tp:
        return False, "cost_insufficient"
    return True, ""


def ops_health_guard(
    ops_deny_actions: bool | None,
    ops_state: str | None,
    ops_cooldown_until_ms: int | None,
    now_ms: int,
) -> tuple[bool, str]:
    if ops_deny_actions is True:
        return False, "ops_deny_actions"
    if ops_state == "RED":
        return False, "ops_health_red"
    if ops_cooldown_until_ms is not None and now_ms < ops_cooldown_until_ms:
        return False, "ops_cooldown_active"
    return True, ""
