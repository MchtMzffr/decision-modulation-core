# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Generic guard policy: domain-agnostic thresholds for DMC guards."""

from dataclasses import dataclass

from decision_schema.types import Action


@dataclass
class GuardPolicy:
    """
    Policy for generic guards only. No domain vocabulary.
    Context keys are generic (now_ms, last_event_ts_ms, ops_*, errors_in_window, etc.).
    """

    staleness_ms: int = 5000
    max_error_rate: float = 0.1
    rate_limit_events_max: int = 10
    rate_limit_window_ms: int = 60_000
    circuit_breaker_failures: int = 5
    cooldown_ms: int = 30_000
    """Fail-closed action when a guard triggers or on exception."""
    fail_closed_action: Action = Action.HOLD
