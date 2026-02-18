# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Ops-health guard: deny when ops layer denies or is in cooldown."""


def ops_health_guard(
    ops_deny_actions: bool | None,
    ops_state: str | None,
    ops_cooldown_until_ms: int | None,
    now_ms: int,
) -> tuple[bool, str]:
    """
    Pass if ops-health allows actions.
    Context keys: ops_deny_actions, ops_state, ops_cooldown_until_ms, now_ms.
    """
    if ops_deny_actions is True:
        return False, "ops_deny_actions"
    if ops_state == "RED":
        return False, "ops_health_red"
    if ops_cooldown_until_ms is not None and now_ms < ops_cooldown_until_ms:
        return False, "ops_cooldown_active"
    return True, ""
