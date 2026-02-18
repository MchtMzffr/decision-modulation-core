<!--
Decision Ecosystem — decision-modulation-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Guards and Formulas

This document describes each guard's formula, threshold, and triggered action.

## Guard Application Order

Guards are applied in this order (fail-fast):

1. Staleness Guard
2. Liquidity Guard
3. Spread Guard
4. Exposure Guard
5. Inventory Guard
6. Cancel Rate Guard
7. Daily Loss Guard
8. Error Rate / Circuit Breaker Guard
9. Adverse Selection Guard
10. Sigma Spike Guard
11. Cost / Profit Gate
12. Streak Cooldown Guard
13. Drawdown Guard
14. Ops Health Guard

## Guard Details

### 1. Staleness Guard

**Purpose**: Reject proposals based on stale market data.

**Formula**:
```
staleness_ms = now_ms - last_event_ts_ms
if staleness_ms > policy.staleness_ms:
    FAIL → HOLD
```

**Policy Parameter**: `staleness_ms` (default: 1000 ms)

**Reason Code**: `"staleness_exceeded"`

---

### 2. Liquidity Guard

**Purpose**: Require minimum market depth.

**Formula**:
```
if depth < policy.min_depth:
    FAIL → HOLD
```

**Policy Parameters**:
- `min_depth` (default: 1.0)
- `min_depth_p10_market` (optional, default: 0.0) - additional gate for QUOTE

**Reason Code**: `"insufficient_depth"`

---

### 3. Spread Guard

**Purpose**: Reject wide spreads.

**Formula**:
```
if spread_bps > policy.max_spread_bps:
    FAIL → HOLD
```

**Policy Parameters**:
- `max_spread_bps` (default: 500.0 = 5%)
- `spread_med_5m_max_bps` (optional, default: 100.0) - 5-minute regime filter

**Reason Code**: `"spread_too_wide"`

---

### 4. Exposure Guard

**Purpose**: Limit total USD exposure.

**Formula**:
```
if current_total_exposure_usd >= policy.max_total_exposure_usd:
    FAIL → HOLD

if proposal.size_usd and (current_total_exposure_usd + proposal.size_usd) > policy.max_total_exposure_usd:
    CLAMP size_usd to (max_total_exposure_usd - current_total_exposure_usd)
```

**Policy Parameters**:
- `max_total_exposure_usd` (default: 10.0)
- `max_per_market_usd` (default: 5.0)

**Reason Code**: `"exposure_limit"` (if clamping), `"total_exposure_exceeded"` (if rejecting)

---

### 5. Inventory Guard

**Purpose**: Limit absolute inventory.

**Formula**:
```
if abs_inventory >= policy.max_abs_inventory:
    FAIL → HOLD
```

**Policy Parameter**: `max_abs_inventory` (default: 10.0)

**Reason Code**: `"inventory_limit"`

---

### 6. Cancel Rate Guard

**Purpose**: Throttle when cancel rate exceeds limit.

**Formula**:
```
cancel_rate = cancels_in_window / (cancel_window_ms / 1000.0)
if cancel_rate > policy.cancel_rate_limit:
    FAIL → HOLD
    Set mismatch.throttle_refresh_ms = policy.throttle_refresh_ms
```

**Policy Parameters**:
- `cancel_rate_limit` (default: 20 cancels per window)
- `cancel_window_ms` (default: 10000 ms)
- `throttle_refresh_ms` (default: 1500 ms) - hint for execution layer

**Reason Code**: `"cancel_rate_exceeded"`

---

### 7. Daily Loss Guard

**Purpose**: Stop trading after daily loss threshold.

**Formula**:
```
if daily_realized_pnl_usd <= -policy.daily_loss_stop_usd:
    FAIL → STOP (or HOLD if STOP not supported)
```

**Policy Parameter**: `daily_loss_stop_usd` (default: 2.5)

**Reason Code**: `"daily_loss_stop"`

---

### 8. Error Rate / Circuit Breaker Guard

**Purpose**: Stop trading on high error rate.

**Formula**:
```
error_rate = errors_in_window / steps_in_window
if error_rate > policy.error_rate_max:
    FAIL → STOP

if recent_failures >= policy.circuit_breaker_failures:
    FAIL → STOP
```

**Policy Parameters**:
- `error_rate_max` (default: 0.1 = 10%)
- `error_window_steps` (default: 100)
- `circuit_breaker_failures` (default: 5)
- `circuit_breaker_window_sec` (default: 60.0)

**Reason Code**: `"error_rate_exceeded"` or `"circuit_breaker"`

---

### 9. Adverse Selection Guard

**Purpose**: Monitor fill quality and trigger cooldown on poor fills.

**Formula**:
```
if adverse_15_ticks > policy.adv15_max_ticks:
    FAIL → CANCEL_ALL + HOLD (if adverse_cooldown_ms > 0)

if adverse_60_ticks > policy.adv60_max_ticks:
    FAIL → CANCEL_ALL + HOLD (if adverse_cooldown_ms > 0)
```

**Policy Parameters**:
- `adv15_max_ticks` (default: 1.0)
- `adv60_max_ticks` (default: 2.0)
- `adverse_cooldown_ms` (default: 0 = off)

**Reason Code**: `"adverse_selection_15"` or `"adverse_selection_60"`

**Action**: If `adverse_cooldown_ms > 0`, triggers CANCEL_ALL + cooldown.

---

### 10. Sigma Spike Guard

**Purpose**: Reject volatile regimes.

**Formula**:
```
if sigma_spike_z > policy.sigma_spike_z_max:
    FAIL → HOLD
```

**Policy Parameters**:
- `sigma_spike_z_max` (default: 2.5)
- `sigma_5m_max` (optional, default: 0.02) - 5-minute regime filter

**Reason Code**: `"sigma_spike"`

---

### 11. Cost / Profit Gate

**Purpose**: Ensure profit potential exceeds costs.

**Formula**:
```
if proposal.action == QUOTE:
    if tp_ticks < (cost_ticks + min_profit_ticks):
        FAIL → HOLD
```

**Policy Parameters**:
- `cost_ticks` (default: 1.0)
- `min_profit_ticks` (default: 0.0)
- `tp_ticks` (from context, typically from strategy config)

**Reason Code**: `"insufficient_profit_potential"`

---

### 12. Streak Cooldown Guard

**Purpose**: Cooldown after consecutive losses.

**Formula**:
```
if consecutive_losses >= policy.max_consecutive_losses and max_consecutive_losses > 0:
    FAIL → CANCEL_ALL + HOLD (cooldown for streak_cooldown_ms)
```

**Policy Parameters**:
- `max_consecutive_losses` (default: 0 = off)
- `streak_cooldown_ms` (default: 120000 ms = 2 min)

**Reason Code**: `"loss_streak"`

**Action**: Triggers CANCEL_ALL + cooldown.

---

### 13. Drawdown Guard

**Purpose**: Kill-switch on drawdown threshold.

**Formula**:
```
if max_drawdown >= policy.max_drawdown_stop_usd and max_drawdown_stop_usd > 0:
    FAIL → STOP

if equity <= policy.equity_floor_usd and equity_floor_usd > 0:
    FAIL → STOP
```

**Policy Parameters**:
- `max_drawdown_stop_usd` (default: 0.0 = off)
- `equity_floor_usd` (default: 0.0 = off)

**Reason Code**: `"drawdown_stop"` or `"equity_floor"`

---

### 14. Ops Health Guard

**Purpose**: Cooldown on rate limits / reconnects.

**Formula**:
```
if 429_count >= policy.max_429_per_window and max_429_per_window > 0:
    FAIL → HOLD (cooldown for ops_cooldown_ms)

if ws_reconnects >= policy.max_ws_reconnects_per_window and max_ws_reconnects_per_window > 0:
    FAIL → HOLD (cooldown for ops_cooldown_ms)
```

**Policy Parameters**:
- `max_429_per_window` (default: 0 = off)
- `max_ws_reconnects_per_window` (default: 0 = off)
- `ops_cooldown_ms` (default: 0 = off)

**Reason Code**: `"rate_limit_429"` or `"ws_reconnect_limit"`

---

## Guard Interaction

- **Fail-fast**: First guard failure stops evaluation
- **Order matters**: Guards are applied in deterministic order
- **Action override**: Different guards may trigger different actions:
  - Most guards → HOLD
  - Adverse/Streak → CANCEL_ALL + HOLD (if cooldown enabled)
  - Daily loss/Drawdown/Error → STOP

## Testing Guards

Each guard should be tested at boundary conditions:
- Just below threshold → PASS
- At threshold → FAIL
- Just above threshold → FAIL

See `tests/test_guards.py` for examples.
