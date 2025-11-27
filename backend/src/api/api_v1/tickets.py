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

# Инициализация сервисов
analyzer_service = TicketAnalyzerService()
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


@router.post("/analyze-text", response_model=AnalysisResult)
async def analyze_text(request: TicketRequest) -> AnalysisResult:
    """
    Анализ текстовой заявки (старый endpoint для совместимости)
    
    Принимает текст заявки и возвращает:
    - Релевантность IT департаменту
    - Список подходящих типов работ с уверенностью
    - Объяснения для каждого варианта
    """
    try:
        result = await analyzer_service.analyze_ticket(ticket_text=request.text)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при анализе заявки: {str(e)}"
        )


@router.post("/analyze-excel", response_model=List[AnalysisResult])
async def analyze_excel(file: UploadFile = File(...)) -> List[AnalysisResult]:
    """
    Анализ заявок из Excel файла
    
    Принимает Excel файл с заявками и возвращает результаты анализа для каждой.
    Ожидаемый формат: колонка с текстом заявок.
    """
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="Поддерживаются только Excel файлы (.xlsx, .xls)"
            )
        
        results = await analyzer_service.analyze_excel(file)
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке Excel файла: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {
        "status": "healthy",
        "service": "KFU IT Ticket Classifier"
    }
