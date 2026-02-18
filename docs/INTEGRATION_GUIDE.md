# Integration Guide — decision-modulation-core

## Dependency

Pin schema version:
```toml
dependencies = ["decision-schema>=0.2,<0.3"]
```

## Basic Usage

Core API is **domain-agnostic**. Use `GuardPolicy` and generic context keys.

```python
from decision_schema.types import Proposal, Action
from dmc_core.dmc.modulator import modulate
from dmc_core.dmc.policy import GuardPolicy

# Proposal from mdm-engine or other proposal generator
proposal = Proposal(
    action=Action.ACT,
    confidence=0.8,
    reasons=["signal_detected"],
    params={"value": 100},
)

# Context (generic keys): now_ms, last_event_ts_ms, ops_*, errors_in_window, steps_in_window, etc.
context = {
    "now_ms": 1000,
    "last_event_ts_ms": 950,
    "errors_in_window": 0,
    "steps_in_window": 100,
    "rate_limit_events": 0,
    "recent_failures": 0,
}

# Guard policy (generic thresholds)
policy = GuardPolicy(
    staleness_ms=5000,
    max_error_rate=0.1,
    fail_closed_action=Action.HOLD,
)

# Modulate
final_decision, mismatch = modulate(proposal, policy, context)

if mismatch.flags:
    print(f"Guards triggered: {mismatch.flags}")
    print(f"Reason codes: {mismatch.reason_codes}")
    # Fail-closed: do not execute
else:
    print(f"Proposal approved: {final_decision.action}")
    # Execute final_decision
```

## Integration with ops-health-core

```python
from ops_health_core.kill_switch import update_kill_switch
from ops_health_core.model import OpsPolicy, OpsState

# Update ops-health signal
state = OpsState()
# ... record events (errors, rate limits, reconnects) ...
signal = update_kill_switch(state, OpsPolicy(), now_ms)

# Add to DMC context
context.update(signal.to_context())

# DMC will check ops-health guard automatically
final_decision, mismatch = modulate(proposal, GuardPolicy(), context)
```

## Guard Ordering

Guards are applied in deterministic order (fail-fast). First guard failure stops evaluation and returns fail-closed decision.

## Fail-Closed Behavior

On any exception or guard failure:
- `final_decision.action` is set to `Action.HOLD` or `Action.STOP`
- `mismatch.flags` contains failure reason codes
- The integration layer should record guard evaluation results into `PacketV2.external` or context passed to the trace

## Trace and PacketV2

DMC core does **not** write to `PacketV2` itself. The integration layer (e.g. harness) records guard outcomes and context into `PacketV2.external` and/or context for downstream reporting.
