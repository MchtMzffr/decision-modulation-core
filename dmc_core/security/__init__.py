"""DMC security: live gating, fail-closed checks, kill switch."""

from dmc_core.security.policy import (
    live_execution_allowed,
    live_trading_allowed,  # Deprecated alias
    LiveGatingResult,
)

__all__ = ["live_execution_allowed", "live_trading_allowed", "LiveGatingResult"]
