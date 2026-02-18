<!--
Decision Ecosystem — decision-modulation-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Formulas — decision-modulation-core

Let P be a Proposal, and G = [g1, g2, ..., gn] be an ordered guard list.

Each guard outputs a verdict vi:
```
vi ∈ {ALLOW, CLAMP, REJECT, ESCALATE}
```

## Composition rule (severity max)

```
Final verdict v* = max_severity(v1..vn)
```

## Guard formulas

### Staleness Guard
```
pass = (now_ms - last_event_ts_ms) <= staleness_ms
```

### Rate Limit Guard
```
pass = rate_limit_events_in_window < max_rate_limit_events
```

### Error Budget Guard
```
error_rate = errors_in_window / steps_in_window
pass = error_rate <= max_error_rate
```

### Exposure Guard
```
pass = current_total_exposure <= max_total_exposure
```

### Cooldown Guard
```
pass = (now_ms >= cooldown_until_ms) AND (streak_count < streak_cooldown_steps)
```

### Latency Guard
```
pass = latency_ms <= max_latency_ms
```

### Daily Loss Guard
```
pass = daily_realized_pnl > -abs(daily_loss_stop)
```

### Drawdown Guard
```
pass = current_drawdown <= max_drawdown_stop
```

### Ops-Health Guard
```
pass = NOT (ops_deny_actions OR ops_state == "RED" OR in_cooldown)
```

## Invariants

- **Determinism**: same (P, context, G) => same v*
- **Fail-closed**: exceptions => v* = ESCALATE (or HOLD)
- **Trace completeness**: PacketV2 includes each guard evaluation in order
