"""Live gating: require mode=live + enable flag + env vars; fail closed."""

from dataclasses import dataclass


@dataclass
class LiveGatingResult:
    """Result of live trading permission check."""

    allowed: bool
    reason: str  # why allowed or denied


def live_trading_allowed(
    mode: str,
    enable_live_flag: bool,
    required_env_vars_present: bool,
    kill_switch_active: bool = False,
) -> LiveGatingResult:
    """
    Live trading requires: mode==live AND enable_live_flag AND required_env_vars AND not kill_switch.
    Otherwise fail closed.
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
