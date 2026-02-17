# Architecture — decision-modulation-core

## Role in the ecosystem

decision-modulation-core is the **guard and modulation** layer that sits between proposal generation and execution. It is **domain-agnostic** and depends only on `decision-schema`.

## Data flow

```
Proposal -> modulate(Proposal, GuardPolicy, context) -> (FinalDecision, MismatchInfo)
```

## Guard pipeline (generic)

Guards are applied in **deterministic order** (fail-fast). See `dmc_core.dmc.guards_generic.GUARD_ORDER`:

1. Ops-health guard (operational safety)
2. Staleness guard
3. Error-rate guard
4. Rate-limit guard
5. Circuit-breaker guard
6. Cooldown guard

## Contracts

- Input: `decision_schema.types.Proposal`
- Output: `decision_schema.types.FinalDecision`, `MismatchInfo`
- Context: Generic dictionary (`now_ms`, `last_event_ts_ms`, `ops_*`, `errors_in_window`, `steps_in_window`, etc.)
- Policy: `GuardPolicy` (domain-agnostic thresholds)

## Safety invariants

- **Fail-closed**: Any exception → safe default (`Action.HOLD` or `Action.STOP` per policy)
- **Deterministic**: Same inputs → same outputs (INVARIANT 3)
- **No cross-core imports**: Core imports only `decision_schema` (INVARIANT 2)

## Components

### 1. Modulator (`dmc_core/dmc/modulator.py`)

**Function**: `modulate(proposal: Proposal, policy: GuardPolicy, context: dict) -> tuple[FinalDecision, MismatchInfo]`

- Applies generic guards in fixed order
- Returns `FinalDecision` and `MismatchInfo`

### 2. Guards (`dmc_core/dmc/guards_generic/`)

Generic guard set: ops_health, staleness, error_rate, rate_limit, circuit_breaker, cooldown. No domain vocabulary.

### 3. Policy (`dmc_core/dmc/policy.py`)

**Class**: `GuardPolicy`

- Generic thresholds only (staleness_ms, max_error_rate, rate_limit_events_max, circuit_breaker_failures, cooldown_ms, fail_closed_action)
- Domain-specific policies are in `docs/examples/` only.
