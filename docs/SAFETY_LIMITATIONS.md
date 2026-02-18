<!--
Decision Ecosystem — decision-modulation-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Safety Limitations

## What DMC Does NOT Guarantee

DMC is a **risk-aware decision layer**, not a complete risk management system. Important limitations:

### 1. No Guarantee of Positive Outcomes

DMC does not guarantee positive outcomes. It only ensures proposals meet operational and risk constraints. A proposal that passes all guards may still result in negative outcomes depending on the domain.

### 2. No Regime Detection

DMC guards check individual proposal/context pairs. It does not detect broader system regime changes (e.g., sudden state changes, external disruptions). Downstream systems should implement regime detection if needed.

### 3. No Execution Guarantee

DMC does not guarantee successful execution. Even if an `ACT` proposal passes all guards, execution may fail due to:
- State changes before action reaches executor
- Executor rejections
- Network latency
- Partial execution

### 4. No Quality Prevention

DMC monitors execution quality metrics but cannot prevent poor execution quality. It can only trigger cooldowns after poor execution is detected. Execution quality depends on:
- Execution latency
- System state
- Action placement strategy

### 5. No Domain-Specific Guarantees

DMC is generic and does not account for:
- Domain-specific action types
- Domain-specific risk limits
- Domain-specific cost structures
- Domain-specific rate limits (beyond generic ops-health guard)

### 6. Context Completeness Assumption

DMC assumes context is complete and accurate. If context is missing or stale:
- Guards may pass incorrectly
- Guards may fail incorrectly
- Mismatch flags may be misleading

### 7. No State Management

DMC does not manage system state. It only modulates proposals. Downstream systems must:
- Track state
- Handle partial execution
- Manage state lifecycle
- Handle position reconciliation

### 8. No Action Lifecycle Management

DMC does not manage action lifecycle. Downstream systems must:
- Execute actions
- Track action status
- Handle cancellations
- Handle replacements
- Handle execution results

### 9. Policy Configuration Responsibility

DMC thresholds are configurable but not validated. Users must:
- Set appropriate thresholds for their use case
- Understand guard formulas
- Test guard boundaries
- Monitor guard triggers

### 10. No Simulation Guarantee

DMC guards are designed for live execution. Simulation/testing may not accurately reflect guard behavior if:
- Context is simulated (may not match live)
- Data is historical (may not reflect live conditions)
- Execution is simulated (may not reflect live latency)

## What DMC DOES Provide

- **Deterministic guard evaluation**: Same proposal + context + policy → same result
- **Explainable overrides**: Mismatch flags and reason codes explain every override
- **Configurable thresholds**: All thresholds in RiskPolicy
- **Fail-fast behavior**: First guard failure stops evaluation
- **Generic design**: Works with any MDM that outputs proposals conforming to schema

## Recommendations

1. **Use DMC as one layer** in a multi-layer risk system
2. **Implement downstream risk layers** (domain-specific, state management, etc.)
3. **Monitor guard triggers** to tune thresholds
4. **Test guard boundaries** before live execution
5. **Validate context completeness** before calling modulate()
6. **Implement execution quality monitoring** separately from DMC
7. **Use private policy hook** for proprietary risk policies (keep public code generic)

## When NOT to Use DMC

- If you need domain-specific risk management (use domain-specific APIs)
- If you need state management (use a state manager)
- If you need action lifecycle management (use an execution engine)
- If you need regime detection (use a regime detector)
- If you need simulation guarantees (use a simulation framework)

DMC is designed to be **one component** in a larger system, not a complete solution.
