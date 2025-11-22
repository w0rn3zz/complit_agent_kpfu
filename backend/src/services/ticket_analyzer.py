import asyncio
import time
from typing import List, Any
from openai import AsyncOpenAI
import pandas as pd
from io import BytesIO

from src.core.config import settings
from src.core.schemas import AnalysisResult, WorkTypeMatch


class TicketAnalyzerService:
    """Сервис для анализа и классификации заявок"""
    
    def __init__(self):
        self.client = self._init_llm_client()
    
    def _init_llm_client(self):
        """Инициализация LLM клиента"""
        if settings.ai_provider == "openai":
            return AsyncOpenAI(api_key=settings.openai_api_key)
        # TODO: Добавить поддержку GigaChat
        return AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def analyze_ticket(self, ticket_text: str) -> AnalysisResult:
        """Анализ одной заявки"""
        start_time = time.time()
        
        # Проверка релевантности и классификация
        is_relevant, matches = await self._analyze_text(ticket_text)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return AnalysisResult(
            is_relevant=is_relevant,
            matches=matches,
            processing_time_ms=processing_time
        )
    
    async def analyze_excel(self, file_content: bytes) -> List[AnalysisResult]:
        """Парсинг и анализ Excel файла с заявками"""
        try:
            # Читаем Excel файл
            df = pd.read_excel(BytesIO(file_content))
            
            # Проверяем наличие колонки с текстом заявки
            text_column = None
            for col in ['text', 'текст', 'описание', 'заявка', 'description']:
                if col in df.columns.str.lower():
                    text_column = col
                    break
            
            if text_column is None:
                # Используем первую колонку
                text_column = df.columns[0]
            
            # Анализируем каждую строку
            tasks = []
            for _, row in df.iterrows():
                ticket_text = str(row[text_column])
                if ticket_text and ticket_text.strip():
                    tasks.append(self.analyze_ticket(ticket_text))
            
            # Параллельный анализ всех заявок
            results = await asyncio.gather(*tasks)
            return results
            
        except Exception as e:
            print(f"Error parsing Excel: {e}")
            raise ValueError(f"Ошибка при обработке Excel файла: {str(e)}")
    
    async def _analyze_text(self, ticket_text: str) -> tuple[bool, List[WorkTypeMatch]]:
        """Анализ текста заявки через LLM"""
        
        system_prompt = """Ты - система классификации IT-заявок для КФУ.

Твоя задача:
1. Проверить, относится ли заявка к IT-департаменту
2. Определить тип работ и уверенность

К IT относятся: компьютеры, ПО, сеть, почта, доступы, сайты
НЕ относятся: ремонт, сантехника, кадры, финансы

Типы работ:
- Установка ПО (hw_install)
- Настройка оборудования (hw_setup) 
- Ремонт оборудования (hw_repair)
- Настройка сети (net_setup)
- Доступы и учетки (access)
- Разработка/поддержка сайтов (web)

Ответь в JSON:
{
  "is_relevant": true/false,
  "matches": [
    {
      "work_type_id": "hw_install",
      "work_type_name": "Установка ПО",
      "confidence": 0.85,
      "reasoning": "краткое объяснение"
    }
  ]
}

Верни до 3 наиболее подходящих типов работ."""

        user_prompt = f"Заявка: {ticket_text}"
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            is_relevant = result.get("is_relevant", True)
            matches = []
            
            for match_data in result.get("matches", []):
                matches.append(WorkTypeMatch(
                    work_type_id=match_data.get("work_type_id", "unknown"),
                    work_type_name=match_data.get("work_type_name", "Неизвестно"),
                    confidence=match_data.get("confidence", 0.5),
                    reasoning=match_data.get("reasoning", "")
                ))
            
            return is_relevant, matches
            
        except Exception as e:
            print(f"Error in _analyze_text: {e}")
            # Fallback
            return True, [
                WorkTypeMatch(
                    work_type_id="unknown",
                    work_type_name="Требуется ручная обработка",
                    confidence=0.5,
                    reasoning="Ошибка при автоматическом анализе"
                )
            ]
