"""Schemas для приложения"""

from .ticket import TicketRequest, TicketWithAnswersRequest
from .analysis import AnalysisResult, WorkTypeMatch, AgentClassificationResult

__all__ = [
    "TicketRequest",
    "TicketWithAnswersRequest",
    "AnalysisResult",
    "WorkTypeMatch",
    "AgentClassificationResult",
]
