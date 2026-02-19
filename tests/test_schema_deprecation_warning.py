# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""DMC schema deprecation warning is driven by DMC version (minor >= 3), not schema version."""

import warnings


def test_schema_no_warning_on_dmc_010() -> None:
    """When DMC is 0.1.0, importing dmc_core.schema must not emit DeprecationWarning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        import dmc_core.schema  # noqa: F401

        deprecations = [x for x in w if issubclass(x.category, DeprecationWarning)]
    assert not deprecations, "DMC 0.1.x should not emit schema deprecation warning"


def test_schema_warning_on_dmc_030() -> None:
    """When DMC version is 0.3.0 (monkeypatch), reload of dmc_core.schema should emit DeprecationWarning."""
    import importlib
    import dmc_core.schema as schema_module
    import dmc_core.version as version_module

    original = version_module.__version__
    try:
        version_module.__version__ = "0.3.0"
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            importlib.reload(schema_module)
        deprecations = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert any("dmc_core.schema" in str(m.message) for m in deprecations), (
            "DMC 0.3.x should emit schema deprecation"
        )
    finally:
        version_module.__version__ = original
        importlib.reload(schema_module)
