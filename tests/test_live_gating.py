# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Live gating: fail closed when requirements not met (domain-agnostic: live_execution_allowed)."""

from dmc_core.security.policy import live_execution_allowed


def test_live_not_allowed_without_mode():
    r = live_execution_allowed(
        mode="sim", enable_live_flag=True, required_env_vars_present=True
    )
    assert r.allowed is False
    assert "live" in r.reason.lower() or "mode" in r.reason.lower()


def test_live_not_allowed_without_flag():
    r = live_execution_allowed(
        mode="live", enable_live_flag=False, required_env_vars_present=True
    )
    assert r.allowed is False


def test_live_not_allowed_with_kill_switch():
    r = live_execution_allowed(
        mode="live",
        enable_live_flag=True,
        required_env_vars_present=True,
        kill_switch_active=True,
    )
    assert r.allowed is False
    assert "kill" in r.reason.lower()
