"""
KFU IT Ticket Classifier
Multi-Agent система для классификации заявок в IT-поддержку КФУ
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.config import settings
from src.api import api_v1_router
from src.core.clients import get_kfu_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle менеджер приложения"""
    print("🚀 Starting KFU IT Ticket Classifier")
    print(f"📊 AI Provider: {settings.ai_provider}")
    print(f"🔗 KFU API: {settings.kfu_api_url}")
    print(f"🐛 Debug Mode: {settings.debug}")
    
    yield
    
    print("👋 Shutting down...")
    kfu_client = get_kfu_client()
    await kfu_client.close()


app = FastAPI(
    title="KFU IT Ticket Classifier",
    description="""
    Multi-Agent система для автоматической классификации заявок в IT-поддержку КФУ
    
    ## Возможности
    
    - 🤖 Автоматическая классификация типов работ по смысловой нагрузке текста
    - 📊 Предложение нескольких вариантов с процентами вероятности
    - ✅ Определение релевантности департаменту информатизации и связи
    - 💡 Генерация объяснений для каждого варианта
    - 🔌 Интеграция с системой приема заявок КФУ через webhook
    - ⚡ Real-time обновления через WebSocket
    
    ## Архитектура
    
    Система использует multi-agent подход:
    - **RelevanceAgent** - проверка релевантности департаменту
    - **ClassifierAgent** - классификация типов работ
    - **ConfidenceAgent** - расчет уверенности для каждого варианта
    - **ExplanationAgent** - генерация объяснений решений
    
    ## Интеграция с КФУ
    
    Для быстрой интеграции с реальным API КФУ:
    1. Настройте переменные окружения (KFU_API_URL, KFU_API_KEY)
    2. Раскомментируйте код в `src/core/clients/kfu.py`
    3. Настройте webhook endpoint в системе КФУ на `/api/v1/webhook/kfu`
    
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(api_v1_router)


@app.get("/")
async def root():
    """Главная страница с информацией о сервисе"""
    return {
        "service": "KFU IT Ticket Classifier",
        "version": "1.0.0",
        "description": "Multi-Agent система для автоматической классификации заявок",
        "features": [
            "Классификация типов работ по смысловой нагрузке текста",
            "Определение релевантности департаменту информатизации",
            "Расчет процентов уверенности для каждого варианта",
            "Генерация объяснений решений",
            "Интеграция с системой КФУ через webhook",
            "Real-time обновления через WebSocket"
        ],
        "integrations": {
            "kfu_api": {
                "status": "ready",
                "mode": "development",
                "note": "Для интеграции с реальным API КФУ настройте переменные окружения и раскомментируйте код в kfu_client.py"
            }
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/v1/health",
            "analyze": "/api/v1/analyze",
            "webhook": "/api/v1/webhook/kfu",
            "work_types": "/api/v1/work-types",
            "websocket": "/ws/updates"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
