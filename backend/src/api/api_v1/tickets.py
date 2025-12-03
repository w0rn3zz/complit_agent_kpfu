"""Endpoints для работы с заявками"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List

from src.core.schemas import (
    TicketRequest, 
    TicketWithAnswersRequest,
    AnalysisResult,
    AgentClassificationResult
)
from src.services import TicketAnalyzerService
from src.agents import SystemControlAgent

router = APIRouter(tags=["tickets"])

agent_system = SystemControlAgent()


@router.post("/classify", response_model=AgentClassificationResult)
async def classify_ticket(request: TicketRequest) -> AgentClassificationResult:
    """
    Классификация заявки через систему агентов
    
    Цепочка обработки:
    1. AbbreviationConvert - исправление аббревиатур
    2. TicketAnalyzer (ML) - классификация с ML моделью
       - Если уверенность >= 90% -> возврат результата
    3. DeepTicketAnalyzer (GigaChat) - глубокий анализ
       - Если удалось классифицировать -> возврат результата
    4. QuestionGenerator - генерация вопросов для уточнения
    
    Returns:
        Результат классификации или список вопросов для уточнения
    """
    try:
        result = await agent_system.process_ticket(request.text)
        return AgentClassificationResult(**result.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при классификации заявки: {str(e)}"
        )


@router.post("/classify-with-answers", response_model=AgentClassificationResult)
async def classify_with_answers(request: TicketWithAnswersRequest) -> AgentClassificationResult:
    """
    Финальная классификация заявки с ответами на вопросы
    
    Используется когда система сгенерировала вопросы и получила на них ответы.
    
    Args:
        request: Заявка с вопросами и ответами
        
    Returns:
        Финальный результат классификации
    """
    try:
        result = await agent_system.process_with_answers(
            ticket_text=request.text,
            questions=request.questions,
            answers=request.answers
        )
        return AgentClassificationResult(**result.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при финальной классификации: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {
        "status": "healthy",
        "service": "KFU IT Ticket Classifier"
    }
