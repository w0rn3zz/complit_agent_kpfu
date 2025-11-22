from pydantic import BaseModel, Field
from typing import List, Optional


class TicketRequest(BaseModel):
    """Входящая заявка для анализа"""
    text: str = Field(..., description="Текст заявки от пользователя")


class TicketWithAnswersRequest(BaseModel):
    """Заявка с ответами на вопросы"""
    text: str = Field(..., description="Исходный текст заявки (обработанный)")
    questions: List[str] = Field(..., description="Вопросы, которые были заданы")
    answers: List[str] = Field(..., description="Ответы пользователя на вопросы")
