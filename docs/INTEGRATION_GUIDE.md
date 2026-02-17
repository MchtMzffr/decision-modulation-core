# Integration Guide — decision-modulation-core

## Dependency

Pin schema version:
```toml
dependencies = ["decision-schema>=0.1,<0.2"]
```

## Basic Usage

```python
from decision_schema.types import Proposal, Action
from dmc_core.dmc.modulator import modulate
from dmc_core.dmc.risk_policy import RiskPolicy

# Proposal from mdm-engine or other proposal generator
proposal = Proposal(
    action=Action.ACT,
    confidence=0.8,
    reasons=["signal_detected"],
    params={"value": 100},
)

# Context from system/telemetry
context = {
    "now_ms": 1000,
    "last_event_ts_ms": 950,
    "error_count": 2,
    "latency_ms": 50,
    "current_total_exposure": 5.0,
}

# Risk policy (use defaults or configure)
policy = RiskPolicy(
    staleness_ms=1000,
    max_error_rate=0.1,
    max_total_exposure=10.0,
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
final_decision, mismatch = modulate(proposal, RiskPolicy(), context)
```

## Guard Ordering

Guards are applied in deterministic order (fail-fast). First guard failure stops evaluation and returns fail-closed decision.

## Fail-Closed Behavior

On any exception or guard failure:
- `final_decision.action` is set to `Action.HOLD` or `Action.STOP`
- `mismatch.flags` contains failure reason codes
- `PacketV2` includes guard evaluation trace
