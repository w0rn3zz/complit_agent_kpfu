from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from src.core.enums import TicketSource


class TicketRequest(BaseModel):
    """Входящая заявка"""
    text: str = Field(..., description="Текст заявки от пользователя")
    source: TicketSource = Field(default=TicketSource.WEB_UI, description="Источник заявки")
    external_id: Optional[str] = Field(None, description="ID заявки во внешней системе")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Дополнительные данные")


class TicketResponse(BaseModel):
    """Ответ по заявке"""
    ticket_id: str
    status: str
    message: str
