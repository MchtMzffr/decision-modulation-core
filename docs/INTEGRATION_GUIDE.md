# Integration Guide

## Importing Schema Types

**✅ Correct way** (recommended):

```python
from decision_schema.types import Proposal, FinalDecision, Action, MismatchInfo
from decision_schema.packet_v2 import PacketV2
```

**❌ Deprecated way** (will be removed in v1.0.0):

```python
from dmc_core.schema import Proposal, FinalDecision  # Re-exports, deprecated
```

## Using Proposal

**✅ Domain-agnostic** (recommended):

```python
from decision_schema.types import Proposal, Action

proposal = Proposal(
    action=Action.ACT,
    confidence=0.8,
    reasons=["signal"],
    params={
        "bid": 0.49,      # Generic key
        "ask": 0.51,      # Generic key
        "size": 1.0,      # Generic key
        "post_only": True,
    },
)
```

**❌ Legacy fields** (deprecated, will be removed in v1.0.0):

```python
proposal = Proposal(
    action=Action.QUOTE,  # Deprecated alias
    bid_quote=0.49,       # Deprecated field
    ask_quote=0.51,       # Deprecated field
    size_usd=1.0,         # Deprecated field
)
```

## Ops-Health Integration

DMC includes an **ops-health guard** that checks operational safety signals.

### Basic Usage

```python
from ops_health_core.kill_switch import update_kill_switch
from ops_health_core.model import OpsPolicy, OpsState
from dmc_core.dmc.modulator import modulate
from dmc_core.dmc.risk_policy import RiskPolicy

# Update ops-health signal
state = OpsState()
# ... record events (errors, rate limits, reconnects) ...
signal = update_kill_switch(state, OpsPolicy(), now_ms)

# Add to DMC context
context = {
    "now_ms": now_ms,
    "error_count": 5,
    "latency_ms": 100,
    # ... other context ...
}
context.update(signal.to_context())  # Adds ops_deny_actions, ops_state, etc.

# DMC will check ops-health guard
final_action, mismatch = modulate(proposal, RiskPolicy(), context)

# If ops-health denies, final_action.action == Action.STOP
if mismatch.flags and "ops_health" in mismatch.flags:
    # Operational safety triggered
    print(f"Ops-health denied: {mismatch.reason_codes}")
```

### Ops-Health Guard Behavior

The ops-health guard checks:
- `ops_deny_actions`: If `True`, returns `STOP` with reason `ops_deny_actions`
- `ops_state`: If `"RED"`, returns `STOP` with reason `ops_health_red`
- `ops_cooldown_until_ms`: If in cooldown, returns `STOP` with reason `ops_cooldown_active`

**Guard order**: Ops-health guard runs **first** (before staleness, liquidity, etc.) to ensure operational safety.

## Migration Checklist

- [ ] Replace `Action.QUOTE` → `Action.ACT`
- [ ] Replace `Action.FLATTEN` → `Action.EXIT`
- [ ] Replace `Action.CANCEL_ALL` → `Action.CANCEL`
- [ ] Replace direct fields (`bid_quote`, etc.) → `params` dict
- [ ] Replace imports from `dmc_core.schema` → `decision_schema`
- [ ] Update tests to use generic Action values and params dict
- [ ] Integrate ops-health-core signals into DMC context
- [ ] Replace "Market Decision Model" → "proposal generator" in documentation

See `decision-schema/docs/DEPRECATION_PLAN.md` for detailed migration guide.
