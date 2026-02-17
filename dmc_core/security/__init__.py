"""DMC security: live gating, fail-closed checks, kill switch."""

from dmc_core.security.policy import (
    live_trading_allowed,
    LiveGatingResult,
)

__all__ = ["live_trading_allowed", "LiveGatingResult"]
