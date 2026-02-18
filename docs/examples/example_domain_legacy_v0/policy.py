# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""
Legacy RiskPolicy — example domain policy only. Not part of core.
Core uses GuardPolicy (dmc_core.dmc.policy).
"""

from dataclasses import dataclass


@dataclass
class RiskPolicy:
    """Legacy thresholds for domain guards (example only)."""

    staleness_ms: int = 1000
    min_depth: float = 1.0
    max_spread_bps: float = 500.0
    max_per_market_usd: float = 5.0
    max_total_exposure_usd: float = 10.0
    max_abs_inventory: float = 10.0
    cancel_rate_limit: int = 20
    cancel_window_ms: int = 10_000
    cancel_rate_window_sec: float = 10.0
    daily_loss_stop_usd: float = 2.5
    error_rate_max: float = 0.1
    error_window_steps: int = 100
    circuit_breaker_failures: int = 5
    circuit_breaker_window_sec: float = 60.0
    throttle_cooldown_sec: float = 5.0
    sigma_5m_max: float = 0.02
    spread_med_5m_max_bps: float = 100.0
    depth_p10_5m_min: float = 50.0
    throttle_refresh_ms: int = 1500
    adverse_selection_max: float = 0.005
    adv15_max_ticks: float = 1.0
    adv60_max_ticks: float = 2.0
    adverse_cooldown_ms: int = 0
    sigma_spike_z_max: float = 2.5
    cost_ticks: float = 1.0
    min_profit_ticks: float = 0.0
    tp_ticks: float = 1.0
    max_inventory_skew_ticks: float = 4.0
    max_consecutive_losses: int = 0
    streak_cooldown_ms: int = 120_000
    equity_floor_usd: float = 0.0
    max_drawdown_stop_usd: float = 0.0
    min_depth_p10_market: float = 0.0
    max_open_orders: int = 0
    max_active_markets: int = 0
    min_order_usd: float = 0.0
    ops_cooldown_ms: int = 0
    max_429_per_window: int = 0
    max_ws_reconnects_per_window: int = 0
