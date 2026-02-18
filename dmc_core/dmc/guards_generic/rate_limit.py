# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Rate-limit guard: fail when events in window exceed limit."""


def rate_limit_guard(
    events_in_window: int,
    events_max: int,
) -> tuple[bool, str]:
    """Pass if events_in_window <= events_max."""
    if events_in_window > events_max:
        return False, "rate_limit_exceeded"
    return True, ""
