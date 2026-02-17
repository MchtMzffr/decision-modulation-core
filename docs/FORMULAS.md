# Decision Modulation Core Formulas

## Guard Formulas

### Staleness Guard

```
pass = (now_ms - last_event_ts_ms) <= staleness_ms
```

If `now_ms - last_event_ts_ms > staleness_ms` → fail with reason `staleness_exceeded`.

### Liquidity Guard

```
pass = depth >= min_depth
```

If `depth < min_depth` → fail with reason `liquidity_low`.

### Spread Guard

```
pass = spread_bps <= max_spread_bps
```

If `spread_bps > max_spread_bps` → fail with reason `spread_wide`.

### Exposure Guard

```
pass = current_total_exposure_usd <= max_total_exposure_usd
```

If `current_total_exposure_usd > max_total_exposure_usd` → fail with reason `exposure_cap`, override to `FLATTEN`.

### Inventory Guard

```
pass = abs_inventory <= max_abs_inventory
```

If `abs_inventory > max_abs_inventory` → fail with reason `inventory_cap`, override to `FLATTEN`.

### Cancel Rate Guard

```
pass = cancels_in_window < cancel_rate_limit
```

If `cancels_in_window >= cancel_rate_limit` → fail with reason `cancel_rate_throttle`, set `throttle_refresh_ms`.

### Daily Loss Guard

```
pass = daily_realized_pnl_usd > -abs(daily_loss_stop_usd)
```

If `daily_realized_pnl_usd <= -abs(daily_loss_stop_usd)` → fail with reason `daily_loss_stop`, override to `STOP`.

### Error Rate Guard

```
error_rate = errors_in_window / steps_in_window
pass = error_rate <= error_rate_max
```

If `error_rate > error_rate_max` → fail with reason `error_rate_high`.

### Circuit Breaker Guard

```
pass = recent_failures < circuit_breaker_failures
```

If `recent_failures >= circuit_breaker_failures` → fail with reason `circuit_breaker`, override to `STOP`.

### Adverse Selection Guard (Legacy)

```
pass = adverse_selection_avg <= adverse_selection_max
```

If `adverse_selection_avg > adverse_selection_max` → fail with reason `adverse_selection_high`.

### Adverse Selection Ticks Guard

```
pass = (adv15_ticks <= max15_ticks) AND (adv60_ticks <= max60_ticks)
```

If `adv15_ticks > max15_ticks` → fail with reason `adverse_selection_high_15`.  
If `adv60_ticks > max60_ticks` → fail with reason `adverse_selection_high_60`.

### Sigma Spike Guard

```
pass = z <= z_max
```

If `z > z_max` → fail with reason `sigma_spike`.

### Cost Guard

```
required_tp = ceil(cost_ticks + min_profit_ticks)
pass = tp_ticks >= required_tp
```

If `tp_ticks < required_tp` → fail with reason `cost_insufficient`.

### Ops-Health Guard

```
pass = NOT (ops_deny_actions OR ops_state == "RED" OR in_cooldown)
```

If `ops_deny_actions == True` → fail with reason `ops_deny_actions`, override to `STOP`.  
If `ops_state == "RED"` → fail with reason `ops_health_red`, override to `STOP`.  
If `now_ms < ops_cooldown_until_ms` → fail with reason `ops_cooldown_active`, override to `STOP`.

## Modulator Logic

### Guard Execution Order

1. **Ops-health guard** (first - operational safety)
2. Staleness guard
3. Liquidity guard
4. Spread guard
5. Exposure guard
6. Inventory guard
7. Cancel rate guard
8. Daily loss guard
9. Error rate guard
10. Circuit breaker guard
11. Adverse selection guards
12. Sigma spike guard
13. Cost guard (last)

### Action Override Rules

- **HOLD**: Most guards (staleness, liquidity, spread, etc.)
- **FLATTEN**: Exposure/inventory limits (when position exists)
- **STOP**: Daily loss, circuit breaker, ops-health RED

### Size Clamping

If proposal passes all guards and `action == ACT`:

```
size_usd = min(proposal.size_usd, policy.max_per_market_usd)
```

## Generic Metrics (Reference)

### Markout

```
markout = mid_after_fill - fill_price
```

### Adverse Selection (Ticks)

```
adverse_15_ticks = mean(markout_ticks) for fills within 15s window
adverse_60_ticks = mean(markout_ticks) for fills within 60s window
```

These are generic definitions; actual computation is domain-specific.
