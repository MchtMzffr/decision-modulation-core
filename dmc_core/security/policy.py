# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Live execution gating: require mode=live + enable flag + env vars; fail closed."""

from dataclasses import dataclass


@dataclass
class LiveGatingResult:
    """Result of live execution permission check."""

    allowed: bool
    reason: str  # why allowed or denied


def live_execution_allowed(
    mode: str,
    enable_live_flag: bool,
    required_env_vars_present: bool,
    kill_switch_active: bool = False,
) -> LiveGatingResult:
    """
    Live execution requires: mode==live AND enable_live_flag AND required_env_vars AND not kill_switch.
    Otherwise fail closed.
    
    Note: This function was previously named `live_trading_allowed`. The name has been changed
    to be domain-agnostic. `live_trading_allowed` is deprecated and will be removed in a future version.
    """
    if kill_switch_active:
        return LiveGatingResult(allowed=False, reason="kill_switch_active")
    if mode != "live":
        return LiveGatingResult(allowed=False, reason="mode_not_live")
    if not enable_live_flag:
        return LiveGatingResult(allowed=False, reason="live_not_enabled")
    if not required_env_vars_present:
        return LiveGatingResult(allowed=False, reason="missing_env_vars")
    return LiveGatingResult(allowed=True, reason="ok")


# Backward compatibility alias (deprecated)
def live_trading_allowed(
    mode: str,
    enable_live_flag: bool,
    required_env_vars_present: bool,
    kill_switch_active: bool = False,
) -> LiveGatingResult:
    """
    Deprecated: Use `live_execution_allowed` instead.
    
    This function is kept for backward compatibility and will be removed in a future version.
    """
    import warnings
    warnings.warn(
        "live_trading_allowed is deprecated. Use live_execution_allowed instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return live_execution_allowed(mode, enable_live_flag, required_env_vars_present, kill_switch_active)
