"""Агент для глубокого анализа заявок с использованием GigaChat"""
import logging
from pathlib import Path
from typing import Tuple, Optional
import json

from src.core.clients.gigachat_client import GigaChatClient

logger = logging.getLogger(__name__)


class DeepTicketAnalyzerAgent:
    """
    Агент для глубокого анализа заявок с использованием GigaChat.
    Используется когда ML модель не уверена в классификации.
    """
    
    CONFIDENCE_THRESHOLD = 0.90
    
    def __init__(self):
        self.gigachat_client = GigaChatClient()
        self.system_prompt = self._load_prompt()
    
    def _load_prompt(self) -> str:
        """Загрузка промпта из файла"""
        try:
            prompt_path = Path(__file__).parent.parent.parent / "data" / "prompts" / "prompt.txt"
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt = f.read()
            logger.info(f"Промпт загружен из {prompt_path}")
            return prompt
        except Exception as e:
            logger.error(f"Ошибка при загрузке промпта: {e}")
            # Возвращаем базовый промпт
            return "Ты - эксперт по классификации заявок университета КФУ."
    
    async def analyze(self, text: str) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Глубокий анализ заявки с использованием GigaChat
        
        Args:
            text: Текст заявки
            
        Returns:
            Tuple[should_continue, class_name, confidence]
            - should_continue: True если нужно передать следующему агенту (генератору вопросов)
            - class_name: Название класса заявки (если определен)
            - confidence: Уверенность классификации (0-1)
        """
        try:
            logger.info(f"Глубокий анализ заявки: {text[:100]}...")
            
            # Формируем промпт для GigaChat
            user_prompt = f"""Проанализируй заявку и определи её класс.

Текст заявки:
{text}

Верни ответ СТРОГО в формате JSON:
{{
    "class": "название класса из списка или 'нет классов'",
    "confidence": 0.95,
    "reasoning": "краткое объяснение выбора"
}}"""
            
            # Отправляем запрос
            response = await self.gigachat_client.generate_response(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,  # Низкая температура для точности
                max_tokens=512
            )
            
            # Парсим ответ
            result = self._parse_response(response)
            
            if result:
                class_name = result.get("class")
                confidence = result.get("confidence", 0.0)
                
                if class_name and class_name != "нет классов" and confidence >= self.CONFIDENCE_THRESHOLD:
                    return False, class_name, confidence
                else:
                    return True, class_name, confidence
            else:
                logger.warning("Не удалось распарсить ответ GigaChat")
                return True, None, None
                
        except Exception as e:
            logger.error(f"Ошибка при глубоком анализе: {e}")
            return True, None, None
    
    def _parse_response(self, response: str) -> Optional[dict]:
        """
        Парсинг ответа от GigaChat
        
        Args:
            response: Ответ от GigaChat
            
        Returns:
            Словарь с результатами или None
        """
        try:
            # Пытаемся найти JSON в ответе
            response = response.strip()
            
            # Если ответ начинается с ```json, убираем маркеры
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            response = response.strip()
            
            # Парсим JSON
            result = json.loads(response)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            logger.error(f"Ответ: {response}")
            
            # Пытаемся извлечь информацию вручную
            try:
                # Простой парсинг если JSON невалидный
                if "нет классов" in response.lower():
                    return {"class": "нет классов", "confidence": 0.0, "reasoning": "Класс не определен"}
                return None
            except:
                return None
