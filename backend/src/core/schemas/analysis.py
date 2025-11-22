from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime


class AgentStep(BaseModel):
    """Шаг выполнения агента"""
    agent_name: str = Field(..., description="Имя агента")
    action: str = Field(..., description="Выполненное действие")
    result: str = Field(..., description="Результат")
    timestamp: datetime = Field(default_factory=datetime.now)


class AnalysisResult(BaseModel):
    """Результат анализа заявки"""
    ticket_id: str = Field(..., description="ID обработанной заявки")
    is_relevant: bool = Field(..., description="Относится ли к компетенции департамента")
    matches: List["WorkTypeMatch"] = Field(..., description="Варианты типов работ с вероятностями")
    agent_steps: List[AgentStep] = Field(default_factory=list, description="Шаги выполнения агентов")
    processing_time_ms: int = Field(..., description="Время обработки в мс")
    metadata: Dict[str, Any] = Field(default_factory=dict)


from src.core.schemas.work_type import WorkTypeMatch
AnalysisResult.model_rebuild()
