# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Staleness guard: fail when last event is too old."""


def staleness_guard(
    last_event_ts_ms: int,
    now_ms: int,
    staleness_ms: int,
) -> tuple[bool, str]:
    """Pass if (now_ms - last_event_ts_ms) <= staleness_ms."""
    if now_ms - last_event_ts_ms > staleness_ms:
        return False, "staleness_exceeded"
    return True, ""
