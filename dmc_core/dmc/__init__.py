# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""DMC: Risk modulation (generic guards + modulator)."""

from dmc_core.dmc.policy import GuardPolicy
from dmc_core.dmc.modulator import modulate

__all__ = [
    "GuardPolicy",
    "modulate",
]
