"""
DMC schema: backward-compatible re-exports from decision-schema.

**DEPRECATED**: This module provides backward compatibility re-exports.
New code should import directly from `decision_schema`:

    from decision_schema.types import Proposal, FinalDecision, Action
    from decision_schema.packet_v2 import PacketV2

**Sunset plan**:
- v0.1.x: Re-exports available, no warnings
- v0.3.x: Re-exports available with DeprecationWarning
- v1.0.0: Re-exports removed (use decision_schema directly)

See INTEGRATION_GUIDE.md for migration instructions.
"""

import warnings

# Re-export from decision-schema for backward compatibility
from decision_schema.packet_v2 import PacketV2
from decision_schema.types import (
    Action,
    FinalAction,  # Alias for FinalDecision
    FinalDecision,
    MismatchInfo,
    Proposal,
    TradeProposal,  # Alias for Proposal
)

__all__ = [
    "Action",
    "Proposal",
    "TradeProposal",  # Backward compat alias
    "FinalDecision",
    "FinalAction",  # Backward compat alias
    "MismatchInfo",
    "PacketV2",
]

# Emit deprecation warning in v0.3+
from decision_schema.version import __version__
version_parts = __version__.split(".")
if len(version_parts) >= 2:
    minor = int(version_parts[1])
    if minor >= 3:
        warnings.warn(
            "Importing from dmc_core.schema is deprecated. "
            "Import directly from decision_schema instead. "
            "Re-exports will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
