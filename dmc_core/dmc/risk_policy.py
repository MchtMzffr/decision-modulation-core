"""Risk policy: thresholds, defaults, profiles."""

from dataclasses import dataclass


@dataclass
class RiskPolicy:
    """Thresholds for DMC guards."""

    staleness_ms: int = 1000
    min_depth: float = 1.0
    max_spread_bps: float = 500.0  # 5% in bps
    max_per_market_usd: float = 5.0
    max_total_exposure_usd: float = 10.0
    max_abs_inventory: float = 10.0
    cancel_rate_limit: int = 20  # cancels per window
    cancel_window_ms: int = 10_000  # time window for cancel count (dt_ms-aware)
    cancel_rate_window_sec: float = 10.0
    daily_loss_stop_usd: float = 2.5
    error_rate_max: float = 0.1
    error_window_steps: int = 100
    circuit_breaker_failures: int = 5
    circuit_breaker_window_sec: float = 60.0
    throttle_cooldown_sec: float = 5.0
    # 5m regime filter: trade only when all within bounds
    sigma_5m_max: float = 0.02
    spread_med_5m_max_bps: float = 100.0
    depth_p10_5m_min: float = 50.0
    # Throttle: when cancel_rate hits limit, use this refresh (ms)
    throttle_refresh_ms: int = 1500
    # Adverse selection: max avg adverse move (mid units) after fill (legacy)
    adverse_selection_max: float = 0.005
    # Adverse selection in ticks (15s / 60s horizon) — LIVE kalite metriği
    adv15_max_ticks: float = 1.0
    adv60_max_ticks: float = 2.0
    adverse_cooldown_ms: int = 0  # on adverse trigger: CANCEL_ALL + HOLD for this long (0 = off)
    # Vol spike (5m regime): z > z_max -> HOLD
    sigma_spike_z_max: float = 2.5
    # Cost / TP gate: tp_ticks >= cost_ticks + min_profit_ticks (tp_ticks from strategy config)
    cost_ticks: float = 1.0
    min_profit_ticks: float = 0.0
    tp_ticks: float = 1.0
    # Inventory skew clamp (quote price drift)
    max_inventory_skew_ticks: float = 4.0
    # Loss-streak guard: N consecutive losing closes -> CANCEL_ALL + HOLD (0 = off)
    max_consecutive_losses: int = 0
    streak_cooldown_ms: int = 120_000
    # Equity/drawdown kill-switch (0 = off)
    equity_floor_usd: float = 0.0
    max_drawdown_stop_usd: float = 0.0
    # Market eligibility (min depth for QUOTE; 0 = no extra gate)
    min_depth_p10_market: float = 0.0
    # Max open orders / markets (operational risk; 0 = no limit)
    max_open_orders: int = 0
    max_active_markets: int = 0
    # Min notional (order size floor; below -> HOLD)
    min_order_usd: float = 0.0
    # Ops-health cooldown (429/ws limits; 0 = off)
    ops_cooldown_ms: int = 0
    max_429_per_window: int = 0
    max_ws_reconnects_per_window: int = 0
