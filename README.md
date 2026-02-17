# Decision Modulation Core (DMC)

**Decision Modulation Core** is a risk-aware decision layer that sits between a proposal generator and execution. It applies configurable guards and safety policies to proposals, ensuring actions meet operational and risk constraints before execution.

## Domain-Agnostic Guarantee

DMC is designed to work across **any domain** that requires risk-aware decision modulation:

- ✅ **No domain-specific logic**: Guards are generic (staleness, rate limits, cooldowns)
- ✅ **Generic action types**: `ACT`, `EXIT`, `HOLD`, `CANCEL`, `STOP` work for any domain
- ✅ **Flexible context**: Context keys are generic (`now_ms`, `error_count`, `latency_ms`)
- ✅ **Configurable thresholds**: All limits are policy-driven, not hardcoded
- ✅ **Fail-closed design**: Guard failures result in safe actions (`HOLD`/`STOP`)
- ✅ **Contract-first**: Uses `decision-schema` for type contracts (domain-agnostic)

## What DMC Does

DMC takes:
- **Proposal** (from proposal generator): Proposed action (`ACT`/`EXIT`/`HOLD`), confidence, reasons
- **Context**: System state, telemetry, operational metrics (timestamps, error counts, latency, etc.)
- **Risk Policy**: Configurable thresholds and guard parameters

DMC outputs:
- **Final Decision**: Action (possibly modified/overridden to `HOLD`/`EXIT`/`CANCEL`/`STOP`)
- **Mismatch Info**: Flags and reason codes when guards trigger

## What DMC Is NOT

- **Not a proposal generator**: DMC does not generate proposals. It only modulates proposals from an external generator.
- **Not an execution engine**: DMC does not execute actions or manage lifecycle.
- **Not domain-specific**: DMC is generic and works with any proposal generator that outputs proposals conforming to `decision-schema`.

## Use Cases

DMC enables risk-aware decision modulation in various domains:

### 1. Content Moderation Pipeline
- **Proposal**: Moderate/flag content based on ML model
- **Guards**: Rate limits (moderation per minute), cooldowns (after false positives), error budgets
- **FinalDecision**: Apply moderation or hold for human review

### 2. Robotics Control System
- **Proposal**: Move/stop robot based on sensor inputs
- **Guards**: Battery limits, collision avoidance, error rate (sensor failures), latency (command delay)
- **FinalDecision**: Execute movement or emergency stop

### 3. API Rate Limiting & Quota Management
- **Proposal**: Allow/deny API requests based on usage patterns
- **Guards**: Rate limits (requests per window), quota limits (daily/monthly), error budgets (429 responses)
- **FinalDecision**: Allow request or throttle/deny

### 4. Resource Allocation System
- **Proposal**: Allocate compute/storage based on demand
- **Guards**: Capacity limits, cooldowns (after over-allocation), error budgets (allocation failures)
- **FinalDecision**: Allocate resources or hold/wait

### 5. Trading/Financial Markets (Optional)
- **Proposal**: Execute trades based on market signals
- **Guards**: Exposure limits, drawdown limits, adverse selection, rate limits
- **FinalDecision**: Execute trade or hold/flatten/stop

## Example Domain: Market Microstructure (Optional Reference)

For reference, here's how DMC applies to market microstructure scenarios:

- **Proposal**: Execute trades (`ACT`) with bid/ask quotes
- **Guards**: Spread limits, depth requirements, exposure caps, adverse selection thresholds
- **FinalDecision**: Execute trade (`ACT`) or hold/flatten (`EXIT`)/stop (`STOP`)

**Note**: This is just one example domain. DMC is generic and works for any domain that requires risk-aware decision modulation.

## Core Concepts

### Guards

Guards are deterministic checks that evaluate proposals against risk policy thresholds:

- **Staleness Guard**: Reject stale data/events
- **Rate Limit Guard**: Throttle when rate exceeds limit
- **Error Budget Guard**: Stop when error rate exceeds threshold
- **Exposure Guard**: Limit total exposure/resource usage
- **Cooldown Guard**: Enforce cooldown periods after failures
- **Latency Guard**: Reject when latency exceeds threshold
- **Ops-Health Guard**: Stop when operational health is RED

See `docs/FORMULAS.md` for detailed formulas.

### Modulator

The `modulate()` function applies guards in deterministic order. On first guard failure, it:
1. Overrides proposal to `HOLD` (or `EXIT`/`CANCEL`/`STOP` if appropriate)
2. Sets mismatch flags and reason codes
3. Returns immediately (fail-fast)

If all guards pass, the proposal is passed through (possibly with parameter clamping).

## Quick Start

```python
from decision_schema.types import Proposal, Action
from dmc_core.dmc.risk_policy import RiskPolicy
from dmc_core.dmc.modulator import modulate

# Proposal generator outputs a proposal
proposal = Proposal(
    action=Action.ACT,
    confidence=0.8,
    reasons=["signal_detected", "threshold_met"],
    params={"value": 100, "threshold": 0.5},
)

# Context from system/telemetry
context = {
    "now_ms": 1000,
    "last_event_ts_ms": 950,
    "error_count": 2,
    "latency_ms": 50,
    "current_total_exposure": 5.0,
    # ... more context fields
}

# Risk policy (use defaults or configure)
policy = RiskPolicy(
    staleness_ms=1000,
    max_error_rate=0.1,
    max_total_exposure=10.0,
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

## Integration with Proposal Generator

DMC is designed to work with any proposal generator that outputs `Proposal` (from `decision-schema`). Minimal integration:

```python
from decision_schema.types import Proposal, Action
from dmc_core.dmc.modulator import modulate
from dmc_core.dmc.risk_policy import RiskPolicy

# 1. Proposal generator produces proposal
proposal = your_proposal_generator.generate(context)

# 2. Build context (from system state/telemetry)
context = {
    "now_ms": now_ms,
    "last_event_ts_ms": last_event_ts_ms,
    "error_count": error_count,
    "latency_ms": latency_ms,
    # ... system-specific context
}

# 3. DMC modulates
policy = RiskPolicy()
final_action, mismatch = modulate(proposal, policy, context)

# 4. Execute (or HOLD if guards triggered)
if not mismatch.flags:
    execute(final_action)
```

**When DMC returns `HOLD`/`EXIT`/`CANCEL`/`STOP`**: Guards triggered (staleness, rate limits, error budgets, etc.). See `docs/FORMULAS.md` for details.

## Schema Contract

DMC uses `decision-schema` package (SSOT) for type contracts:

- `Proposal`: Proposal generator output (action, confidence, reasons, params)
- `FinalDecision`: Post-DMC action (possibly modified)
- `MismatchInfo`: Guard failure flags and reason codes
- `Action`: Enum (`HOLD`, `ACT`, `EXIT`, `CANCEL`, `STOP`; backward compat: `QUOTE`, `FLATTEN`, `CANCEL_ALL`)

**Note**: Schema is provided by `decision-schema` package. DMC re-exports types from `decision-schema` via `dmc_core.schema` for backward compatibility (deprecated in v0.3+).

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
- `docs/FORMULAS.md`: Guard formulas and thresholds
- `docs/INTEGRATION_GUIDE.md`: How to integrate proposal generators with DMC
- `docs/SAFETY_LIMITATIONS.md`: What DMC does NOT guarantee
- `docs/PUBLIC_RELEASE_GUIDE.md`: Public release checklist
- `PARAMETER_INDEX.md`: Complete parameter reference (SSOT)

## Installation

```bash
pip install -e .
```

Or from git:
```bash
pip install git+https://github.com/MeetlyTR/decision-modulation-core.git
```

## Tests

```bash
pytest tests/
```

## License

[Add your license]
