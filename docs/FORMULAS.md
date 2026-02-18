# Formulas — decision-modulation-core (domain-free)

Guard evaluation and composition rules. All formulas use generic context keys only (no domain vocabulary).

## Guard order (deterministic)

Guards run in fixed order; first failure yields fail-closed and stops.

1. **Ops-health**: `context["ops_deny_actions"] == True` → deny, HOLD/STOP
2. **Staleness**: `(now_ms - last_event_ts_ms) > policy.staleness_ms` → HOLD
3. **Error-rate**: `errors_in_window / max(1, steps_in_window) > policy.max_error_rate` → HOLD
4. **Rate-limit**: `rate_limit_events` (or equivalent) exceeds policy threshold → HOLD
5. **Circuit-breaker**: `recent_failures` (or equivalent) exceeds policy threshold → HOLD
6. **Cooldown**: `now_ms < cooldown_until_ms` → HOLD

## Fail-closed

- Any exception in guard evaluation → `FinalDecision(allowed=False, action=policy.fail_closed_action)`
- `fail_closed_action` is typically `Action.HOLD` or `Action.STOP`

## Context keys (SSOT)

See `decision-schema` PARAMETER_INDEX and repo `docs/INTEGRATION_GUIDE.md` for context key registry. Core does not write to PacketV2; the integration layer records guard results into `PacketV2.external` or context.
