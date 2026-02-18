# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Circuit-breaker guard: fail when recent failures >= threshold."""


def circuit_breaker_guard(
    recent_failures: int,
    circuit_breaker_failures: int,
) -> tuple[bool, str]:
    """Pass if recent_failures < circuit_breaker_failures."""
    if recent_failures >= circuit_breaker_failures:
        return False, "circuit_breaker"
    return True, ""
