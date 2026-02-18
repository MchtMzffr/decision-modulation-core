# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Error-rate guard: fail when errors/steps exceeds threshold."""


def error_rate_guard(
    errors_in_window: int,
    steps_in_window: int,
    error_rate_max: float,
) -> tuple[bool, str]:
    """Pass if steps_in_window <= 0 or errors_in_window/steps_in_window <= error_rate_max."""
    if steps_in_window <= 0:
        return True, ""
    rate = errors_in_window / steps_in_window
    if rate > error_rate_max:
        return False, "error_rate_high"
    return True, ""
