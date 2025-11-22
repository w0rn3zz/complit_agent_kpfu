from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class KFUTicketWebhook(BaseModel):
    """Webhook от системы КФУ"""
    ticket_id: str
    title: str
    description: str
    author_email: Optional[str] = None
    department: Optional[str] = None
    priority: Optional[str] = "normal"
    created_at: datetime
    callback_url: Optional[str] = None


class KFUCallbackResponse(BaseModel):
    """Ответ для отправки обратно в КФУ"""
    ticket_id: str
    suggested_work_types: List["WorkTypeMatch"]
    is_relevant_to_it_dept: bool
    processing_timestamp: datetime
    confidence_score: float


from src.core.schemas.work_type import WorkTypeMatch
KFUCallbackResponse.model_rebuild()
