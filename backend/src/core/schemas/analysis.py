from pydantic import BaseModel, Field
from typing import List, Optional


class WorkTypeMatch(BaseModel):
    """Сопоставление с типом работ"""
    work_type_id: str = Field(..., description="ID типа работ")
    work_type_name: str = Field(..., description="Название типа работ")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность (0-1)")
    reasoning: str = Field(..., description="Объяснение почему выбран этот тип")


class AnalysisResult(BaseModel):
    """Результат анализа заявки"""
    is_relevant: bool = Field(..., description="Относится ли к компетенции IT департамента")
    matches: List[WorkTypeMatch] = Field(..., description="Варианты типов работ с вероятностями")
    processing_time_ms: int = Field(..., description="Время обработки в мс")


class AgentClassificationResult(BaseModel):
    """Результат классификации через систему агентов"""
    stage: str = Field(..., description="Стадия обработки")
    ticket_class: Optional[str] = Field(None, description="Класс заявки")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Уверенность (0-1)")
    questions: Optional[List[str]] = Field(None, description="Вопросы для уточнения (если требуется)")
    processed_text: Optional[str] = Field(None, description="Обработанный текст заявки")
    reasoning: Optional[str] = Field(None, description="Объяснение результата")
