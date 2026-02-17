# DMC Architecture

## Overview

Decision Modulation Core (DMC) is a **risk-aware decision layer** that sits between a Market Decision Model (MDM) and execution. It applies configurable guards to proposals, ensuring actions meet operational and risk constraints.

## Data Flow

```
MDM → Proposal → DMC Modulator → Final Action
                    ↓
              Risk Policy
                    ↓
              Context (features/telemetry)
                    ↓
              Guards (deterministic checks)
                    ↓
         Final Action + Mismatch Info
```

## Components

### 1. Schema (`dmc_core/schema/`)

**Contract types** that define the interface between MDM and DMC:

- `TradeProposal`: MDM output
  - `action`: Proposed action (QUOTE/FLATTEN/HOLD/etc.)
  - `confidence`: [0, 1] confidence score
  - `reasons`: List of reason strings
  - `bid_quote`, `ask_quote`, `size_usd`: Action parameters

- `FinalAction`: Post-DMC action
  - May be modified/overridden by guards
  - Same structure as proposal but represents final decision

- `MismatchInfo`: Guard failure metadata
  - `flags`: List of guard names that triggered
  - `reason_codes`: Detailed reason codes
  - `throttle_refresh_ms`: Optional throttle hint

- `Action`: Enum of possible actions
  - QUOTE, FLATTEN, HOLD, CANCEL_ALL, STOP

### 2. Risk Policy (`dmc_core/dmc/risk_policy.py`)

**Configurable thresholds** for all guards:

- Staleness: `staleness_ms`
- Liquidity: `min_depth`, `min_depth_p10_market`
- Spread: `max_spread_bps`, `spread_med_5m_max_bps`
- Exposure: `max_per_market_usd`, `max_total_exposure_usd`
- Inventory: `max_abs_inventory`, `max_inventory_skew_ticks`
- Cancel rate: `cancel_rate_limit`, `cancel_window_ms`
- Loss limits: `daily_loss_stop_usd`, `max_drawdown_stop_usd`
- Adverse selection: `adv15_max_ticks`, `adv60_max_ticks`
- Volatility: `sigma_5m_max`, `sigma_spike_z_max`
- Ops health: `max_429_per_window`, `max_ws_reconnects_per_window`
- And more...

See `PARAMETER_INDEX.md` for complete reference.

### 3. Guards (`dmc_core/dmc/guards.py`)

**Deterministic check functions** that evaluate proposals:

Each guard:
- Takes context values and policy thresholds
- Returns `(ok: bool, reason_code: str)`
- If `ok == False`, the guard has triggered

Guards are applied in **deterministic order** (fail-fast):
1. Staleness
2. Liquidity
3. Spread
4. Exposure
5. Inventory
6. Cancel rate
7. Daily loss
8. Error rate / circuit breaker
9. Adverse selection
10. Sigma spike
11. Cost / profit gate
12. Streak cooldown
13. Drawdown
14. Ops health

See `docs/GUARDS_AND_FORMULAS.md` for formulas.

### 4. Modulator (`dmc_core/dmc/modulator.py`)

**Main entry point**: `modulate(proposal, policy, context) -> (FinalAction, MismatchInfo)`

Algorithm:
1. Extract context values (now_ms, depth, spread_bps, exposure, etc.)
2. Apply guards in order (fail-fast)
3. On first guard failure:
   - Override action to HOLD (or FLATTEN/CANCEL_ALL/STOP if appropriate)
   - Set mismatch flags and reason codes
   - Return immediately
4. If all guards pass:
   - Pass proposal through (possibly clamp size)
   - Return FinalAction with original proposal action

### 5. Private Hook (`dmc_core/_private/`)

**Optional private policy override** (gitignored):

If `dmc_core._private.policy.override_policy()` exists, modulator uses it to override policy before applying guards. This allows proprietary risk policies without exposing them.

Public tests must pass without `_private/` present.

## Integration Points

### MDM → DMC

MDM must output `TradeProposal` conforming to schema:
- `action`: One of Action enum values
- `confidence`: [0, 1] float
- `reasons`: List[str]
- Action-specific fields (quotes, size) if action == QUOTE

### DMC → Execution

Execution layer receives:
- `FinalAction`: What to actually do
- `MismatchInfo`: Why proposal was modified (if any)

Execution should:
- Respect `FinalAction.action`
- Use `FinalAction.bid_quote`, `ask_quote`, `size_usd` if action == QUOTE
- Log mismatch flags/reason codes for debugging

## Context Requirements

DMC requires context dict with these keys (see `modulator.py` for full list):

**Required:**
- `now_ms`: Current timestamp (ms)
- `last_event_ts_ms`: Last market event timestamp (ms)
- `depth`: Current market depth
- `spread_bps`: Current spread in basis points
- `current_total_exposure_usd`: Total USD exposure across all markets
- `abs_inventory`: Absolute inventory for current market

**Optional (guards may skip if missing):**
- `daily_realized_pnl_usd`: Daily PnL
- `adverse_15_ticks`, `adverse_60_ticks`: Adverse selection metrics
- `sigma_spike_z`: Volatility spike z-score
- `cancels_in_window`: Cancel count in time window
- `errors_in_window`: Error count
- And more...

See `modulator.py` for complete context key list.

## Design Principles

1. **Fail-fast**: First guard failure stops evaluation
2. **Deterministic**: Same proposal + context + policy → same result
3. **Generic**: No exchange-specific or trading-specific logic
4. **Explainable**: Mismatch flags and reason codes explain every override
5. **Configurable**: All thresholds in RiskPolicy (no hardcoded magic numbers)
