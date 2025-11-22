from pydantic import BaseModel, Field
from src.core.enums import WorkTypeCategory


class WorkTypeMatch(BaseModel):
    """Сопоставление с типом работ"""
    work_type_id: str = Field(..., description="ID типа работ")
    work_type_name: str = Field(..., description="Название типа работ")
    category: WorkTypeCategory = Field(..., description="Категория")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность (0-1)")
    reasoning: str = Field(..., description="Объяснение почему выбран этот тип")


class WorkTypeSchema(BaseModel):
    """Схема типа работы"""
    id: str
    name: str
    category: WorkTypeCategory
    description: str
    keywords: list[str]
    examples: list[str]
