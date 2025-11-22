"""
KFU IT Ticket Classifier
Multi-Agent система для классификации заявок в IT-поддержку КФУ
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from src.core.config import settings
from src.api import api_v1_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting KFU IT Ticket Classifier Multi-Agent System...")
    logging.info("Loading ML models and initializing agents...")
    
    yield
    
    logging.info("Shutting down...")


app = FastAPI(
    title="KFU IT Ticket Classifier - Multi-Agent System",
    description="""
    Интеллектуальная система для автоматической классификации заявок в IT-поддержку КФУ
    
    ## Архитектура
    
    ### Цепочка агентов:
    1. **AbbreviationConvert** (GigaChat) - Исправление аббревиатур
    2. **TicketAnalyzer** (ML) - Классификация на основе RuBERT + Logistic Regression
    3. **DeepTicketAnalyzer** (GigaChat) - Глубокий анализ при низкой уверенности ML
    4. **QuestionGenerator** (GigaChat) - Генерация уточняющих вопросов
    
    ## Возможности
    
    - 🤖 Автоматическая классификация с ML моделью (>90% точность)
    - 🧠 Интеллектуальный анализ с GigaChat
    - 💬 Генерация уточняющих вопросов (до 5 вопросов)
    - 📊 Оценка уверенности классификации
    - ✅ Многоуровневая система принятия решений
    - 📝 Обработка аббревиатур и сокращений
    
    ## Endpoints
    
    - `/api/v1/classify` - Классификация заявки через систему агентов
    - `/api/v1/classify-with-answers` - Финальная классификация с ответами
    - `/api/v1/analyze-text` - Старый endpoint (для совместимости)
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)


@app.get("/")
async def root():
    """Главная страница с информацией о сервисе"""
    return {
        "service": "KFU IT Ticket Classifier - Multi-Agent System",
        "version": "2.0.0",
        "description": "Интеллектуальная система классификации заявок на базе ML + GigaChat",
        "architecture": {
            "agents": [
                "AbbreviationConvert (GigaChat)",
                "TicketAnalyzer (RuBERT + Logistic)",
                "DeepTicketAnalyzer (GigaChat)",
                "QuestionGenerator (GigaChat)"
            ],
            "ml_model": "RuBERT-tiny2 + Logistic Classifier",
            "ai_backend": "GigaChat"
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "classify": "/api/v1/classify",
            "classify_with_answers": "/api/v1/classify-with-answers",
            "analyze_text": "/api/v1/analyze-text (deprecated)"
        }
    }
