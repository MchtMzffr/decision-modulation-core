# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""
INVARIANT 2: No cross-core imports.

dmc_core/** must not import mdm_engine, ops_health_core, eval_calibration_core.
Only decision_schema is allowed as external core.
"""

import ast
import importlib.util
from pathlib import Path


def test_invariant_2_no_cross_core_imports() -> None:
    """AST scan: no import of mdm_engine, ops_health_core, eval_calibration_core in dmc_core."""
    root = Path(__file__).resolve().parent.parent
    dmc_root = root / "dmc_core"
    if not dmc_root.is_dir():
        return

    forbidden = {"mdm_engine", "ops_health_core", "eval_calibration_core"}
    violations: list[tuple[str, int, str]] = []

    for py_path in dmc_root.rglob("*.py"):
        if "__pycache__" in str(py_path) or py_path.name.startswith("_"):
            continue
        try:
            text = py_path.read_text(encoding="utf-8")
        except Exception:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        rel = py_path.relative_to(root)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top in forbidden:
                        violations.append((str(rel), node.lineno or 0, alias.name))
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                top = node.module.split(".")[0]
                if top in forbidden:
                    violations.append((str(rel), node.lineno or 0, node.module))

    assert not violations, (
        "INVARIANT 2 violated: cross-core imports in dmc_core: " + str(violations)
    )
