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
    FinalDecision,
    MismatchInfo,
    Proposal,
)

# Domain-free public surface only (INVARIANT 0). Legacy names not in __all__.
__all__ = [
    "Action",
    "Proposal",
    "FinalDecision",
    "MismatchInfo",
    "PacketV2",
]

# Emit deprecation warning when DMC version >= 0.3 (DMC-owned sunset policy)
try:
    from dmc_core.version import __version__ as _dmc_version
except ImportError:
    _dmc_version = "0.1.0"
_parts = _dmc_version.split(".")
if len(_parts) >= 2:
    _minor = int(_parts[1])
    if _minor >= 3:
        warnings.warn(
            "Importing from dmc_core.schema is deprecated. "
            "Import directly from decision_schema instead. "
            "Re-exports will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
