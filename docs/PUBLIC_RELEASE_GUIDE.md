<!--
Decision Ecosystem — decision-modulation-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Public Release Guide

Checklist for making DMC public-safe.

## Pre-Release Checklist

### Code Cleanup

- [ ] Remove all MDM modules (`dmc_core/mdm/` deleted)
- [ ] Remove all exchange-specific code (external adapters, exchange integrations)
- [ ] Remove all trading/bot artifacts (dashboards, scripts, configs)
- [ ] Remove external integration tests and references
- [ ] Verify `git grep -i exchange` returns only generic terms
- [ ] Verify no external service names appear in code
- [ ] Verify `git grep -i mdm` returns nothing (except docs where MDM is referenced conceptually)

### Secrets and Security

- [ ] Verify `.gitignore` includes: `.env*`, `*.local`, `*.secrets*`, `runs/`, `traces/`, `*.log`
- [ ] Verify `dmc_core/_private/` is gitignored
- [ ] Check git history for secrets (see `SECURITY.md`)
- [ ] Add `SECURITY.md` with warnings if history contains secrets
- [ ] Verify no API keys, private keys, or credentials in code
- [ ] Verify redaction utilities work (if present)

### Documentation

- [ ] `README.md` explains what DMC is and is NOT
- [ ] `SECURITY.md` documents security policy
- [ ] `docs/ARCHITECTURE.md` describes system architecture
- [ ] `docs/GUARDS_AND_FORMULAS.md` documents all guards
- [ ] `docs/INTEGRATION_GUIDE.md` shows integration examples
- [ ] `docs/SAFETY_LIMITATIONS.md` documents limitations
- [ ] `PARAMETER_INDEX.md` documents all parameters (SSOT)

### Tests

- [ ] All tests pass: `pytest tests/`
- [ ] No network tests (all unit tests)
- [ ] Tests cover guard boundaries
- [ ] Tests cover private hook optional behavior
- [ ] Tests cover redaction (if present)
- [ ] Tests pass without `_private/` present

### Schema and Types

- [ ] `dmc_core/schema/types.py` defines clean contract
- [ ] `TradeProposal` is generic (not trading-specific)
- [ ] `Action` enum is generic (HOLD/ACT/EXIT/CANCEL, not QUOTE/FLATTEN)
- [ ] Wait, check: Action enum should be generic but current has QUOTE/FLATTEN which are trading-specific. Need to make generic or document as reference implementation.

### Private Hook

- [ ] `dmc_core/_private/` directory exists (gitignored)
- [ ] Modulator tries to import `dmc_core._private.policy.override_policy`
- [ ] Falls back to public defaults if not found
- [ ] Public tests pass without `_private/` present

### Package Structure

- [ ] `pyproject.toml` has correct name and description
- [ ] Package structure matches target:
  ```
  dmc_core/
    schema/
      packet_v2.py
      types.py
    dmc/
      risk_policy.py
      guards.py
      modulator.py
    metrics/
      pnl_metrics.py (generic only)
    security/
      policy.py (if present)
  ```

## Post-Release

- [ ] Monitor issues for secret leaks
- [ ] Monitor issues for missing documentation
- [ ] Update `CHANGELOG.md` (if present) with release notes

## Notes

- DMC is designed to be **generic** and work with any MDM
- Keep public code **explainable** (no proprietary thresholds)
- Private hook allows **proprietary policies** without exposing them
- All guards should be **deterministic** and **testable**
