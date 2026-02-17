# Safety Limitations

## What DMC Does NOT Guarantee

DMC is a **risk-aware decision layer**, not a complete risk management system. Important limitations:

### 1. No Guarantee of Profitability

DMC does not guarantee profitable trading. It only ensures proposals meet operational and risk constraints. A proposal that passes all guards may still result in losses.

### 2. No Market Regime Detection

DMC guards check individual proposal/context pairs. It does not detect broader market regime changes (e.g., flash crashes, market manipulation). Downstream systems should implement regime detection.

### 3. No Fill Guarantee

DMC does not guarantee fills. Even if a QUOTE proposal passes all guards, execution may fail due to:
- Market moves before order reaches exchange
- Exchange rejections
- Network latency
- Partial fills

### 4. No Adverse Selection Prevention

DMC monitors adverse selection (`adv15_max_ticks`, `adv60_max_ticks`) but cannot prevent it. It can only trigger cooldowns after poor fills are detected. Fill quality depends on:
- Execution latency
- Market microstructure
- Order placement strategy

### 5. No Exchange-Specific Guarantees

DMC is generic and does not account for:
- Exchange-specific order types
- Exchange-specific risk limits
- Exchange-specific fee structures
- Exchange-specific rate limits (beyond generic ops-health guard)

### 6. Context Completeness Assumption

DMC assumes context is complete and accurate. If context is missing or stale:
- Guards may pass incorrectly
- Guards may fail incorrectly
- Mismatch flags may be misleading

### 7. No Position Management

DMC does not manage positions. It only modulates proposals. Downstream systems must:
- Track positions
- Handle partial fills
- Manage position lifecycle
- Handle position reconciliation

### 8. No Order Lifecycle Management

DMC does not manage order lifecycle. Downstream systems must:
- Send orders
- Track order status
- Handle cancellations
- Handle replacements
- Handle fills

### 9. Policy Configuration Responsibility

DMC thresholds are configurable but not validated. Users must:
- Set appropriate thresholds for their use case
- Understand guard formulas
- Test guard boundaries
- Monitor guard triggers

### 10. No Backtesting Guarantee

DMC guards are designed for live trading. Backtesting may not accurately reflect guard behavior if:
- Context is simulated (may not match live)
- Market data is historical (may not reflect live microstructure)
- Execution is simulated (may not reflect live latency)

## What DMC DOES Provide

- **Deterministic guard evaluation**: Same proposal + context + policy → same result
- **Explainable overrides**: Mismatch flags and reason codes explain every override
- **Configurable thresholds**: All thresholds in RiskPolicy
- **Fail-fast behavior**: First guard failure stops evaluation
- **Generic design**: Works with any MDM that outputs proposals conforming to schema

## Recommendations

1. **Use DMC as one layer** in a multi-layer risk system
2. **Implement downstream risk layers** (exchange-specific, position management, etc.)
3. **Monitor guard triggers** to tune thresholds
4. **Test guard boundaries** before live trading
5. **Validate context completeness** before calling modulate()
6. **Implement fill quality monitoring** separately from DMC
7. **Use private policy hook** for proprietary risk policies (keep public code generic)

## When NOT to Use DMC

- If you need exchange-specific risk management (use exchange APIs)
- If you need position management (use a position manager)
- If you need order lifecycle management (use an execution engine)
- If you need market regime detection (use a regime detector)
- If you need backtesting guarantees (use a backtesting framework)

DMC is designed to be **one component** in a larger system, not a complete solution.
