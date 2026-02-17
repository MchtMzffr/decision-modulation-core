# Decision Modulation Core (DMC)

**Decision Modulation Core** is a risk-aware decision layer that sits between a Market Decision Model (MDM) and execution. It applies configurable guards and safety policies to proposals, ensuring actions meet operational and risk constraints before execution.

## What DMC Does

DMC takes:
- **Proposal** (from MDM): Proposed action (QUOTE/FLATTEN/HOLD/etc.), confidence, reasons
- **Context**: Market features, telemetry, current state (exposure, inventory, PnL, etc.)
- **Risk Policy**: Configurable thresholds and guard parameters

DMC outputs:
- **Final Decision**: Action (possibly modified/overridden to HOLD/FLATTEN/CANCEL_ALL/STOP)
- **Mismatch Info**: Flags and reason codes when guards trigger

## What DMC Is NOT

- **Not an MDM**: DMC does not generate trading proposals. It only modulates proposals from an external MDM.
- **Not an execution engine**: DMC does not send orders or manage order lifecycle.
- **Not exchange-specific**: DMC is generic and works with any MDM that outputs proposals conforming to the schema.

## Core Concepts

### Guards

Guards are deterministic checks that evaluate proposals against risk policy thresholds:

- **Staleness Guard**: Reject stale market data
- **Liquidity Guard**: Require minimum depth
- **Spread Guard**: Reject wide spreads
- **Exposure Guard**: Limit total USD exposure
- **Inventory Guard**: Limit absolute inventory
- **Cancel Rate Guard**: Throttle when cancel rate exceeds limit
- **Daily Loss Guard**: Stop trading after daily loss threshold
- **Adverse Selection Guard**: Monitor fill quality (15s/60s adverse ticks)
- **Sigma Spike Guard**: Reject volatile regimes
- **Cost Guard**: Ensure profit potential exceeds costs
- **Streak Guard**: Cooldown after consecutive losses
- **Drawdown Guard**: Kill-switch on drawdown threshold
- **Ops-Health Guard**: Cooldown on rate limits / reconnects

See `docs/GUARDS_AND_FORMULAS.md` for detailed formulas.

### Modulator

The `modulate()` function applies guards in deterministic order. On first guard failure, it:
1. Overrides proposal to HOLD (or FLATTEN/CANCEL_ALL/STOP if appropriate)
2. Sets mismatch flags and reason codes
3. Returns immediately (fail-fast)

If all guards pass, the proposal is passed through (possibly with size clamping).

## Quick Start

```python
from dmc_core.schema.types import TradeProposal, Action
from dmc_core.dmc.risk_policy import RiskPolicy
from dmc_core.dmc.modulator import modulate

# MDM outputs a proposal
proposal = TradeProposal(
    action=Action.QUOTE,
    confidence=0.8,
    reasons=["imbalance", "alpha"],
    bid_quote=0.49,
    ask_quote=0.51,
    size_usd=1.0,
)

# Context from market/telemetry
context = {
    "now_ms": 1000,
    "last_event_ts_ms": 950,
    "depth": 100.0,
    "spread_bps": 400.0,
    "current_total_exposure_usd": 5.0,
    "abs_inventory": 2.0,
    # ... more context fields
}

# Risk policy (use defaults or configure)
policy = RiskPolicy(
    max_spread_bps=500.0,
    max_total_exposure_usd=10.0,
    # ... configure thresholds
)

# Modulate
final_action, mismatch = modulate(proposal, policy, context)

if mismatch.flags:
    print(f"Guards triggered: {mismatch.flags}")
    print(f"Reason codes: {mismatch.reason_codes}")
else:
    print(f"Proposal approved: {final_action.action}")
```

## Integration with MDM Engine

DMC is designed to work with MDM Engine (`ami-engine`). Minimal integration:

```python
from ami_engine.mdm.decision_engine import DecisionEngine
from ami_engine.features.feature_builder import build_features
from dmc_core.dmc.modulator import modulate
from dmc_core.dmc.risk_policy import RiskPolicy

# 1. MDM generates proposal
mdm = DecisionEngine()
features = build_features(event, ...)
proposal = mdm.propose(features)

# 2. Build context (from market/telemetry)
context = {
    "now_ms": now_ms,
    "last_event_ts_ms": last_event_ts_ms,
    "depth": features.get("depth", 0.0),
    "spread_bps": features.get("spread_bps", 0.0),
    "current_total_exposure_usd": broker_state.get("total_exposure", 0.0),
    "abs_inventory": abs(broker_state.get("inventory", 0.0)),
}

# 3. DMC modulates
policy = RiskPolicy()
final_action, mismatch = modulate(proposal, policy, context)

# 4. Execute (or HOLD if guards triggered)
if not mismatch.flags:
    execute(final_action)
```

**When DMC returns HOLD/CANCEL_ALL/STOP**: Guards triggered (staleness, exposure, adverse selection, etc.). See `docs/GUARDS_AND_FORMULAS.md` for details.

## Schema Contract

DMC uses `decision-schema` package (SSOT) for type contracts:

- `Proposal` (aliased as `TradeProposal`): MDM output (action, confidence, reasons, params)
- `FinalDecision` (aliased as `FinalAction`): Post-DMC action (possibly modified)
- `MismatchInfo`: Guard failure flags and reason codes
- `Action`: Enum (HOLD, ACT, EXIT, CANCEL, STOP; backward compat: QUOTE, FLATTEN, CANCEL_ALL)

**Note**: Schema is provided by `decision-schema` package. DMC re-exports types from `decision-schema` via `dmc_core.schema` for backward compatibility.

See `decision-schema` repository for full schema definitions.

## Private Policy Hook

DMC supports a private policy override pattern:

1. Create `dmc_core/_private/policy.py` (gitignored)
2. Implement `override_policy(base_policy: RiskPolicy, context: dict) -> RiskPolicy`
3. If the module exists, `modulate()` will use the override; otherwise uses public defaults
4. On private hook runtime error: **fail-closed** (uses public defaults, logs warning)

This allows proprietary risk policies without exposing them in public code.

**Fail-closed behavior**: If `override_policy()` raises an exception, DMC logs a warning and uses the original policy (safe defaults). This ensures the system never breaks due to private hook errors.

## Documentation

- `docs/ARCHITECTURE.md`: System architecture and data flow
- `docs/GUARDS_AND_FORMULAS.md`: Guard formulas and thresholds
- `docs/INTEGRATION_GUIDE.md`: How to integrate MDM with DMC
- `docs/SAFETY_LIMITATIONS.md`: What DMC does NOT guarantee
- `docs/PUBLIC_RELEASE_GUIDE.md`: Public release checklist
- `PARAMETER_INDEX.md`: Complete parameter reference (SSOT)

## Installation

```bash
pip install -e .
```

## Tests

```bash
pytest tests/
```

## License

[Add your license]
