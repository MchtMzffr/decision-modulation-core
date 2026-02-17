"""Generic DMC guards: pass/fail + reason code. Domain-agnostic."""

from dmc_core.dmc.guards_generic.ops_health import ops_health_guard
from dmc_core.dmc.guards_generic.staleness import staleness_guard
from dmc_core.dmc.guards_generic.error_rate import error_rate_guard
from dmc_core.dmc.guards_generic.rate_limit import rate_limit_guard
from dmc_core.dmc.guards_generic.circuit_breaker import circuit_breaker_guard
from dmc_core.dmc.guards_generic.cooldown import cooldown_guard

__all__ = [
    "ops_health_guard",
    "staleness_guard",
    "error_rate_guard",
    "rate_limit_guard",
    "circuit_breaker_guard",
    "cooldown_guard",
]

# Fixed order for INVARIANT 3 (determinism). Do not reorder.
GUARD_ORDER: tuple[str, ...] = (
    "ops_health",
    "staleness",
    "error_rate",
    "rate_limit",
    "circuit_breaker",
    "cooldown",
)
