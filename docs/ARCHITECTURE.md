# DMC Architecture

## Overview

Decision Modulation Core (DMC) is a **risk-aware decision layer** that sits between a proposal generator and execution. It applies configurable guards to proposals, ensuring actions meet operational and risk constraints.

## Data Flow

```
Proposal Generator → Proposal → DMC Modulator → Final Action
                                    ↓
                              Risk Policy
                                    ↓
                              Context (system state/telemetry)
                                    ↓
                              Guards (deterministic checks)
                                    ↓
                         Final Action + Mismatch Info
```

## Components

### 1. Schema (`dmc_core/schema/`)

**Contract types** that define the interface (from `decision-schema` package):

- `Proposal`: Proposal generator output
  - `action`: Proposed action (`ACT`/`EXIT`/`HOLD`/`CANCEL`/`STOP`)
  - `confidence`: [0, 1] confidence score
  - `reasons`: List of reason strings
  - `params`: Generic dict for domain-specific parameters

- `FinalDecision`: Post-DMC action
  - May be modified/overridden by guards
  - Same structure as proposal but represents final decision

- `MismatchInfo`: Guard failure metadata
  - `flags`: List of guard names that triggered
  - `reason_codes`: Detailed reason codes
  - `throttle_refresh_ms`: Optional throttle hint

- `Action`: Enum of possible actions
  - `ACT`, `EXIT`, `HOLD`, `CANCEL`, `STOP` (primary)
  - `QUOTE`, `FLATTEN`, `CANCEL_ALL` (deprecated aliases)

### 2. Risk Policy (`dmc_core/dmc/risk_policy.py`)

**Configurable thresholds** for all guards:

- Staleness: `staleness_ms`
- Rate limits: `max_error_rate`, `max_rate_limit_events`
- Exposure: `max_total_exposure`
- Cooldowns: `cooldown_ms`, `streak_cooldown_steps`
- Latency: `max_latency_ms`
- Loss limits: `daily_loss_stop`, `max_drawdown_stop`
- Ops health: `max_errors_per_window`, `max_reconnects_per_window`
- And more...

See `PARAMETER_INDEX.md` for complete reference.

### 3. Guards (`dmc_core/dmc/guards.py`)

**Deterministic check functions** that evaluate proposals:

Each guard:
- Takes context values and policy thresholds
- Returns `(ok: bool, reason_code: str)`
- If `ok == False`, the guard has triggered

Guards are applied in **deterministic order** (fail-fast):
1. Ops-health (first - operational safety)
2. Staleness
3. Rate limits
4. Error budgets
5. Exposure/resource limits
6. Cooldowns
7. Latency
8. Loss limits
9. Drawdown
10. And more...

See `docs/FORMULAS.md` for formulas.

### 4. Modulator (`dmc_core/dmc/modulator.py`)

**Main entry point**: `modulate(proposal, policy, context) -> (FinalDecision, MismatchInfo)`

Algorithm:
1. Extract context values (`now_ms`, `error_count`, `latency_ms`, `exposure`, etc.)
2. Apply guards in order (fail-fast)
3. On first guard failure:
   - Override action to `HOLD` (or `EXIT`/`CANCEL`/`STOP` if appropriate)
   - Set mismatch flags and reason codes
   - Return immediately
4. If all guards pass:
   - Pass proposal through (possibly clamp parameters)
   - Return `FinalDecision` with original proposal action

### 5. Private Hook (`dmc_core/_private/`)

**Optional private policy override** (gitignored):

If `dmc_core._private.policy.override_policy()` exists, modulator uses it to override policy before applying guards. This allows proprietary risk policies without exposing them.

Public tests must pass without `_private/` present.

## Integration Points

### Proposal Generator → DMC

Proposal generator must output `Proposal` conforming to `decision-schema`:
- `action`: One of `Action` enum values
- `confidence`: [0, 1] float
- `reasons`: List[str]
- `params`: Domain-specific parameters dict

### DMC → Execution

Execution layer receives:
- `FinalDecision`: What to actually do
- `MismatchInfo`: Why proposal was modified (if any)

Execution should:
- Respect `FinalDecision.action`
- Use `FinalDecision.params` for action-specific parameters
- Log mismatch flags/reason codes for debugging

## Context Requirements

DMC requires context dict with these keys (see `modulator.py` for full list):

**Required:**
- `now_ms`: Current timestamp (ms)
- `last_event_ts_ms`: Last event timestamp (ms)

**Optional (guards may skip if missing):**
- `error_count`: Error count in window
- `latency_ms`: Current latency
- `current_total_exposure`: Total resource exposure
- `daily_realized_pnl`: Daily profit/loss
- `ops_deny_actions`: Ops-health deny flag
- `ops_state`: Ops-health state (`GREEN`/`YELLOW`/`RED`)
- `ops_cooldown_until_ms`: Ops-health cooldown timestamp
- And more...

See `modulator.py` for complete context key list.

## Design Principles

1. **Fail-fast**: First guard failure stops evaluation
2. **Deterministic**: Same proposal + context + policy → same result
3. **Generic**: No domain-specific logic (trading/exchange/etc.)
4. **Explainable**: Mismatch flags and reason codes explain every override
5. **Configurable**: All thresholds in `RiskPolicy` (no hardcoded magic numbers)
6. **Fail-closed**: Guard failures result in safe actions (`HOLD`/`STOP`)
