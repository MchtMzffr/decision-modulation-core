# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Domain-free compatibility aliases. Use decision_schema.types for SSOT."""

from decision_schema.types import FinalDecision, Proposal

ProposalLike = Proposal
DecisionLike = FinalDecision

__all__ = ["ProposalLike", "DecisionLike"]
