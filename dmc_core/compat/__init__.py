"""Domain-free compatibility aliases. Use decision_schema.types for SSOT."""

from decision_schema.types import FinalDecision, Proposal

ProposalLike = Proposal
DecisionLike = FinalDecision

__all__ = ["ProposalLike", "DecisionLike"]
