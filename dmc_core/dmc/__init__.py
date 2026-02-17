"""DMC: Risk modulation (generic guards + modulator)."""

from dmc_core.dmc.policy import GuardPolicy
from dmc_core.dmc.modulator import modulate

# Legacy (domain-specific) still available from dmc_core.dmc.guards (old) and risk_policy
from dmc_core.dmc.risk_policy import RiskPolicy

__all__ = [
    "GuardPolicy",
    "modulate",
    "RiskPolicy",
]
