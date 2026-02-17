# Decision Modulation Core Formulas

## Guard Formulas

### Staleness Guard

```
pass = (now_ms - last_event_ts_ms) <= staleness_ms
```

If `now_ms - last_event_ts_ms > staleness_ms` → fail with reason `staleness_exceeded`.

### Rate Limit Guard

```
pass = rate_limit_events_in_window < max_rate_limit_events
```

If `rate_limit_events_in_window >= max_rate_limit_events` → fail with reason `rate_limit_exceeded`.

### Error Budget Guard

```
error_rate = errors_in_window / steps_in_window
pass = error_rate <= max_error_rate
```

If `error_rate > max_error_rate` → fail with reason `error_rate_high`.

### Exposure Guard

```
pass = current_total_exposure <= max_total_exposure
```

If `current_total_exposure > max_total_exposure` → fail with reason `exposure_cap`, override to `EXIT`.

### Cooldown Guard

```
pass = (now_ms >= cooldown_until_ms) AND (streak_count < streak_cooldown_steps)
```

If in cooldown or streak exceeded → fail with reason `cooldown_active` or `streak_cooldown`, override to `HOLD`.

### Latency Guard

```
pass = latency_ms <= max_latency_ms
```

If `latency_ms > max_latency_ms` → fail with reason `latency_high`.

### Daily Loss Guard

```
pass = daily_realized_pnl > -abs(daily_loss_stop)
```

If `daily_realized_pnl <= -abs(daily_loss_stop)` → fail with reason `daily_loss_stop`, override to `STOP`.

### Drawdown Guard

```
pass = current_drawdown <= max_drawdown_stop
```

If `current_drawdown > max_drawdown_stop` → fail with reason `drawdown_stop`, override to `STOP`.

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
3. Rate limit guard
4. Error budget guard
5. Exposure guard
6. Cooldown guard
7. Latency guard
8. Daily loss guard
9. Drawdown guard
10. (Additional domain-specific guards)

### Action Override Rules

- **HOLD**: Most guards (staleness, rate limits, error budgets, cooldowns)
- **EXIT**: Exposure/resource limits (when resource is allocated)
- **STOP**: Daily loss, drawdown, ops-health RED

### Parameter Clamping

If proposal passes all guards and `action == ACT`:

```
clamped_value = min(proposal.params.get("value", 0), policy.max_value)
```

## Generic Metrics (Reference)

These are generic definitions; actual computation is domain-specific.

### Error Rate

```
error_rate = errors_in_window / steps_in_window
```

### Latency Percentiles

```
p50_latency = percentile(latency_samples, 50)
p95_latency = percentile(latency_samples, 95)
p99_latency = percentile(latency_samples, 99)
```

### Health Score (from ops-health-core)

```
score = 1 - (w1*p_err + w2*p_rate_limit + w3*p_reconnect + w4*p_latency)
```

Where `p_*` are normalized penalty factors [0, 1].
