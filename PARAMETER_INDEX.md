<!--
Decision Ecosystem — decision-modulation-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Parameter Index (SSOT)

Complete reference for all DMC configuration parameters.

## RiskPolicy Parameters

All parameters are in `dmc_core.dmc.risk_policy.RiskPolicy`.

### Staleness Guard

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `staleness_ms` | int | 1000 | Max staleness (ms) before HOLD | `guards.staleness_guard()` |

**Formula**: `if (now_ms - last_event_ts_ms) > staleness_ms: HOLD`

---

### Liquidity Guard

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `min_depth` | float | 1.0 | Min market depth | `guards.liquidity_guard()` |
| `min_depth_p10_market` | float | 0.0 | Min depth percentile (0 = off) | `guards.liquidity_guard()` |

**Formula**: `if depth < min_depth: HOLD`

---

### Spread Guard

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `max_spread_bps` | float | 500.0 | Max spread in basis points (5%) | `guards.spread_guard()` |
| `spread_med_5m_max_bps` | float | 100.0 | Max 5m median spread (bps) | `guards.spread_guard()` |

**Formula**: `if spread_bps > max_spread_bps: HOLD`

---

### Exposure Guard

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `max_total_exposure_usd` | float | 10.0 | Max total USD exposure | `guards.exposure_guard()` |
| `max_per_market_usd` | float | 5.0 | Max USD per market | `guards.exposure_guard()` |

**Formula**: `if current_total_exposure_usd >= max_total_exposure_usd: HOLD`  
**Size Clamping**: `size_usd = min(size_usd, max_total_exposure_usd - current_total_exposure_usd)`

---

### Inventory Guard

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `max_abs_inventory` | float | 10.0 | Max absolute inventory | `guards.inventory_guard()` |
| `max_inventory_skew_ticks` | float | 4.0 | Max inventory skew (ticks) | Quote price clamping |

**Formula**: `if abs_inventory >= max_abs_inventory: HOLD`

---

### Cancel Rate Guard

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `cancel_rate_limit` | int | 20 | Max cancels per window | `guards.cancel_rate_guard()` |
| `cancel_window_ms` | int | 10000 | Time window for cancel count (ms) | `guards.cancel_rate_guard()` |
| `cancel_rate_window_sec` | float | 10.0 | Window size in seconds | `guards.cancel_rate_guard()` |
| `throttle_refresh_ms` | int | 1500 | Throttle hint (ms) | Set in `MismatchInfo` |

**Formula**: `if (cancels_in_window / (cancel_window_ms / 1000.0)) > cancel_rate_limit: HOLD`

---

### Daily Loss Guard

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `daily_loss_stop_usd` | float | 2.5 | Daily loss threshold (USD) | `guards.daily_loss_guard()` |

**Formula**: `if daily_realized_pnl_usd <= -daily_loss_stop_usd: STOP`

---

### Error Rate / Circuit Breaker Guard

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `error_rate_max` | float | 0.1 | Max error rate (10%) | `guards.error_rate_guard()` |
| `error_window_steps` | int | 100 | Window size (steps) | `guards.error_rate_guard()` |
| `circuit_breaker_failures` | int | 5 | Max failures before STOP | `guards.circuit_breaker_guard()` |
| `circuit_breaker_window_sec` | float | 60.0 | Circuit breaker window (sec) | `guards.circuit_breaker_guard()` |

**Formula**: `if (errors_in_window / steps_in_window) > error_rate_max: STOP`

---

### Adverse Selection Guard

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `adv15_max_ticks` | float | 1.0 | Max 15s adverse ticks | `guards.adverse_selection_ticks_guard()` |
| `adv60_max_ticks` | float | 2.0 | Max 60s adverse ticks | `guards.adverse_selection_ticks_guard()` |
| `adverse_cooldown_ms` | int | 0 | Cooldown on adverse (0 = off) | Triggers CANCEL_ALL + HOLD |
| `adverse_selection_max` | float | 0.005 | Legacy adverse threshold | `guards.adverse_selection_guard()` |

**Formula**: `if adverse_15_ticks > adv15_max_ticks: CANCEL_ALL + HOLD (if adverse_cooldown_ms > 0)`

---

### Sigma Spike Guard

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `sigma_spike_z_max` | float | 2.5 | Max volatility z-score | `guards.sigma_spike_guard()` |
| `sigma_5m_max` | float | 0.02 | Max 5m sigma | `guards.sigma_spike_guard()` |

**Formula**: `if sigma_spike_z > sigma_spike_z_max: HOLD`

---

### Cost / Profit Gate

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `cost_ticks` | float | 1.0 | Cost in ticks | `guards.cost_guard()` |
| `min_profit_ticks` | float | 0.0 | Min profit in ticks | `guards.cost_guard()` |
| `tp_ticks` | float | 1.0 | Take-profit ticks (from context) | `guards.cost_guard()` |

**Formula**: `if tp_ticks < (cost_ticks + min_profit_ticks): HOLD`

---

### Streak Cooldown Guard

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `max_consecutive_losses` | int | 0 | Max consecutive losses (0 = off) | `guards.streak_guard()` |
| `streak_cooldown_ms` | int | 120000 | Cooldown duration (ms) | Triggers CANCEL_ALL + HOLD |

**Formula**: `if consecutive_losses >= max_consecutive_losses and max_consecutive_losses > 0: CANCEL_ALL + HOLD`

---

### Drawdown Guard

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `max_drawdown_stop_usd` | float | 0.0 | Max drawdown threshold (0 = off) | `guards.drawdown_guard()` |
| `equity_floor_usd` | float | 0.0 | Equity floor (0 = off) | `guards.drawdown_guard()` |

**Formula**: `if max_drawdown >= max_drawdown_stop_usd and max_drawdown_stop_usd > 0: STOP`

---

### Ops Health Guard

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `ops_cooldown_ms` | int | 0 | Ops cooldown duration (0 = off) | `guards.ops_health_guard()` |
| `max_429_per_window` | int | 0 | Max 429 errors per window (0 = off) | `guards.ops_health_guard()` |
| `max_ws_reconnects_per_window` | int | 0 | Max WS reconnects per window (0 = off) | `guards.ops_health_guard()` |

**Formula**: `if 429_count >= max_429_per_window and max_429_per_window > 0: HOLD`

---

### Operational Limits

| Parameter | Type | Default | Purpose | Consumed By |
|-----------|------|---------|---------|-------------|
| `max_open_orders` | int | 0 | Max open orders (0 = no limit) | `modulator.py` |
| `max_active_markets` | int | 0 | Max active markets (0 = no limit) | `modulator.py` |
| `min_order_usd` | float | 0.0 | Min order size (USD) | `modulator.py` |

**Formula**: `if open_orders_count >= max_open_orders and max_open_orders > 0: HOLD`

---

## Public vs Private Parameters

### Public Parameters

All parameters listed above are **public** and documented. They have safe defaults and can be configured by users.

### Private Parameters

Users may implement proprietary risk policies via the private hook (`dmc_core/_private/policy.py`). Private parameters are not documented here (they are gitignored and user-specific).

To use private parameters:
1. Create `dmc_core/_private/policy.py`
2. Implement `override_policy(base_policy: RiskPolicy, context: dict) -> RiskPolicy`
3. Return modified policy with proprietary thresholds

Public tests must pass without `_private/` present.

---

## Safe Defaults

All parameters have safe defaults that:
- Are conservative (favor HOLD over action)
- Can be tuned for specific use cases
- Are documented in `docs/GUARDS_AND_FORMULAS.md`

Users should:
1. Start with defaults
2. Monitor guard triggers
3. Tune thresholds based on observed behavior
4. Test guard boundaries before live trading

---

## Parameter Validation

DMC does not validate parameter ranges. Users must ensure:
- Positive values where required
- Reasonable ranges (e.g., `max_spread_bps` should be < 10000 for most markets)
- Consistent units (ms for time, USD for exposure, ticks for price moves)

See `docs/SAFETY_LIMITATIONS.md` for limitations.
