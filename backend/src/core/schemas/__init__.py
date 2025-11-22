"""Schemas для приложения"""

from .ticket import TicketRequest, TicketResponse
from .work_type import WorkTypeMatch, WorkTypeSchema
from .analysis import AnalysisResult, AgentStep
from .kfu import KFUTicketWebhook, KFUCallbackResponse

__all__ = [
    "TicketRequest",
    "TicketResponse",
    "WorkTypeMatch",
    "WorkTypeSchema",
    "AnalysisResult",
    "AgentStep",
    "KFUTicketWebhook",
    "KFUCallbackResponse",
]
