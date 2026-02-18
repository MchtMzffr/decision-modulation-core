<!--
Decision Ecosystem — decision-modulation-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Dependency Cleanup — numpy and pydantic Removal

**Date:** 2026-02-17  
**Type:** Dependency Cleanup (F7 Fix)

---

## Summary

Removed unused `numpy` and `pydantic` dependencies from `dmc-core` package.

---

## Changes

### Removed Dependencies

- ❌ `numpy>=1.24` (removed)
- ❌ `pydantic>=2.0` (removed)

### Remaining Dependencies

- ✅ `decision-schema>=0.2,<0.3` (required)

---

## Rationale

### Core Code Analysis

**Verification:** Grep search confirmed:
- Core code (`dmc_core/`) does NOT use `numpy` or `pydantic`
- Only `docs/examples/example_domain_legacy_v0/metrics.py` uses `numpy`
- Example code is NOT included in package (`pyproject.toml` includes only `dmc_core*`)

### Impact

- ✅ **No breaking changes:** Core API unchanged
- ✅ **Reduced footprint:** Smaller install size
- ✅ **Faster installs:** Fewer dependencies to resolve
- ✅ **Tests pass:** All 31 tests pass without numpy/pydantic

---

## Backward Compatibility

✅ **Fully backward-compatible:**
- No API changes
- Core functionality unchanged
- Existing code continues to work

---

## Migration Guide

**No migration needed.** Existing code continues to work.

**Note:** If you were using `numpy` or `pydantic` in your integration code, you can add them directly to your project's dependencies:

```toml
# Your project's pyproject.toml
dependencies = [
    "dmc-core>=0.1,<0.2",
    "numpy>=1.24",  # If you need numpy
    "pydantic>=2.0",  # If you need pydantic
]
```

---

## Testing

- ✅ All existing tests pass (31/31)
- ✅ Core imports work without numpy/pydantic
- ✅ Package installs successfully

---

## References

- **Issue:** F7 from static analysis report
- **Related:** `docs/STATIC_ANALYSIS_FIXES_REPORT.md`

---

**Upgrade Path:** `pip install "dmc-core>=0.1,<0.2"` (no changes needed)
