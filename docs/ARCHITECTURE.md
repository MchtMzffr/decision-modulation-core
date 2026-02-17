# Architecture — decision-modulation-core

## Role in the ecosystem

decision-modulation-core is the **guard and modulation** layer that sits between proposal generation and execution.

## Data flow

```
Proposal -> modulate() -> FinalDecision
```

## Guard pipeline

Guards are applied in **deterministic order** (fail-fast):

1. Ops-health guard (operational safety)
2. Staleness guard
3. Rate limit guard
4. Error budget guard
5. Exposure guard
6. Cooldown guard
7. Latency guard
8. Daily loss guard
9. Drawdown guard

## Contracts

- Input: `decision_schema.types.Proposal`
- Output: `decision_schema.types.FinalDecision`
- Context: Generic dictionary (no domain-specific keys in core)

## Safety invariants

- **Fail-closed**: Any exception → safe default (`Action.HOLD` or `Action.STOP`)
- **Deterministic**: Same inputs → same outputs
- **Trace completeness**: All guard evaluations recorded in `PacketV2`

## Components

### 1. Modulator (`dmc_core/dmc/modulator.py`)

**Function**: `modulate(proposal: Proposal, policy: RiskPolicy, context: dict) -> tuple[FinalDecision, MismatchInfo]`

- Applies guards in deterministic order
- Returns `FinalDecision` and `MismatchInfo`

### 2. Guards (`dmc_core/dmc/guards.py`)

Guard types:
- Staleness guard
- Rate limit guard
- Error budget guard
- Exposure guard
- Cooldown guard
- Latency guard
- Daily loss guard
- Drawdown guard
- Ops-health guard

### 3. Risk Policy (`dmc_core/dmc/risk_policy.py`)

**Class**: `RiskPolicy`

- Configurable thresholds for all guards
- Domain-agnostic parameters
