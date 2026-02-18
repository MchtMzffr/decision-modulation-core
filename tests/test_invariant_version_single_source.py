# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""INV-V1: Version single-source - pyproject version must match package __version__."""

import tomllib
from pathlib import Path

import dmc_core


def test_version_single_source() -> None:
    """pyproject.toml version must equal dmc_core.__version__ (no drift)."""
    repo_root = Path(__file__).resolve().parent.parent
    with (repo_root / "pyproject.toml").open("rb") as f:
        data = tomllib.load(f)
    pyproject_version = data["project"]["version"]
    assert dmc_core.__version__ == pyproject_version, (
        "Version drift: pyproject.toml has %r, dmc_core.__version__ is %r"
        % (pyproject_version, dmc_core.__version__)
    )
