"""Endpoints для работы с заявками"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from datetime import datetime

from src.core.schemas import (
    TicketRequest,
    AnalysisResult,
    KFUTicketWebhook,
    KFUCallbackResponse,
    WorkTypeSchema
)
from src.services import TicketAnalyzerService
from src.core.clients import get_kfu_client
from src.dao import WorkTypeDAO

router = APIRouter(tags=["tickets"])

# Инициализация сервисов
analyzer_service = TicketAnalyzerService()
work_type_dao = WorkTypeDAO()


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_ticket(request: TicketRequest) -> AnalysisResult:
    """
    Анализ заявки и определение типов работ
    
    Эндпоинт для анализа произвольного текста заявки.
    Возвращает:
    - Релевантность департаменту
    - Список подходящих типов работ с процентами уверенности
    - Объяснения для каждого варианта
    - Информацию о шагах выполнения агентов
    """
    try:
        result = await analyzer_service.analyze_ticket(
            ticket_text=request.text,
            ticket_id=request.external_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при анализе заявки: {str(e)}"
        )


@router.post("/webhook/kfu", status_code=202)
async def kfu_webhook(webhook: KFUTicketWebhook, background_tasks: BackgroundTasks):
    """
    Webhook для приема заявок из системы КФУ
    
    При интеграции с реальным API КФУ:
    - Этот эндпоинт будет принимать заявки от КФУ
    - Обрабатывать их в фоновом режиме
    - Отправлять результаты обратно через callback_url
    
    Пока работает с тестовыми данными в режиме разработки.
    """
    background_tasks.add_task(process_kfu_ticket, webhook)
    
    return {
        "status": "accepted",
        "ticket_id": webhook.ticket_id,
        "message": "Заявка принята в обработку"
    }


async def process_kfu_ticket(webhook: KFUTicketWebhook):
    """
    Фоновая обработка заявки от КФУ
    
    TODO: При интеграции с КФУ
    - Добавить обработку ошибок и retry логику
    - Настроить правильный callback_url
    - Добавить логирование в БД
    """
    try:
        # Формируем полный текст заявки
        ticket_text = f"{webhook.title}\n\n{webhook.description}"
        if webhook.department:
            ticket_text += f"\n\nПодразделение: {webhook.department}"
        
        # Анализируем заявку
        result = await analyzer_service.analyze_ticket(
            ticket_text=ticket_text,
            ticket_id=webhook.ticket_id
        )
        
        # Формируем ответ для КФУ
        callback_response = KFUCallbackResponse(
            ticket_id=webhook.ticket_id,
            suggested_work_types=result.matches,
            is_relevant_to_it_dept=result.is_relevant,
            processing_timestamp=datetime.now(),
            confidence_score=result.matches[0].confidence if result.matches else 0.0
        )
        
        # Отправляем результат обратно в КФУ (если указан callback_url)
        if webhook.callback_url:
            kfu_client = get_kfu_client()
            await kfu_client.send_classification_result(
                webhook.callback_url,
                callback_response
            )
        
    except Exception as e:
        print(f"Ошибка при обработке заявки КФУ {webhook.ticket_id}: {e}")


@router.get("/work-types", response_model=List[WorkTypeSchema])
async def get_work_types() -> List[WorkTypeSchema]:
    """
    Получить список всех доступных типов работ
    
    Возвращает каталог типов работ департамента информатизации и связи КФУ.
    Используется для справочной информации и отладки.
    """
    work_types = work_type_dao.get_all()
    return [
        WorkTypeSchema(
            id=wt.id,
            name=wt.name,
            category=wt.category,
            description=wt.description,
            keywords=wt.keywords,
            examples=wt.examples
        )
        for wt in work_types
    ]


@router.get("/health")
async def health_check():
    """
    Проверка работоспособности сервиса
    
    Используется для мониторинга и health checks в production.
    """
    return {
        "status": "healthy",
        "service": "KFU IT Ticket Classifier",
        "timestamp": datetime.now().isoformat(),
        "work_types_count": len(work_type_dao.get_all())
    }
