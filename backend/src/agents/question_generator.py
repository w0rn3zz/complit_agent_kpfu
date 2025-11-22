"""Агент для генерации уточняющих вопросов"""
import logging
from typing import List, Optional, Dict
import json

from src.core.clients.gigachat_client import GigaChatClient

logger = logging.getLogger(__name__)


class QuestionGeneratorAgent:
    """
    Агент для генерации уточняющих вопросов.
    Используется когда deep_ticket_analyzer не смог определить класс с высокой уверенностью.
    """
    
    MAX_QUESTIONS = 5
    
    def __init__(self):
        self.gigachat_client = GigaChatClient()
        self.system_prompt = """Ты - эксперт техподдержки университета КФУ.

Твоя задача - сгенерировать уточняющие вопросы для сотрудника техподдержки, которые он может задать пользователю по телефону, чтобы точно определить класс заявки.

Правила:
1. Генерируй от 3 до 5 вопросов
2. Вопросы должны быть конкретными и помогать определить класс заявки
3. Вопросы должны быть понятны обычному пользователю
4. Не используй технический жаргон без объяснений
5. Каждый вопрос должен помочь сузить круг возможных классов

Верни ответ СТРОГО в формате JSON:
{
    "questions": [
        "Вопрос 1?",
        "Вопрос 2?",
        "Вопрос 3?"
    ]
}"""
    
    async def generate_questions(self, ticket_text: str, ml_class: Optional[str] = None) -> List[str]:
        """
        Генерация уточняющих вопросов
        
        Args:
            ticket_text: Исходный текст заявки
            ml_class: Класс, предложенный ML моделью (если есть)
            
        Returns:
            Список вопросов (макс. 5)
        """
        try:
            logger.info(f"Генерация вопросов для заявки: {ticket_text[:100]}...")
            
            # Формируем промпт
            user_prompt = f"""Текст заявки от пользователя:
{ticket_text}
"""
            if ml_class:
                user_prompt += f"\nМодель предположила класс: {ml_class} (но с низкой уверенностью)\n"
            
            user_prompt += f"\nСгенерируй {self.MAX_QUESTIONS} уточняющих вопросов, которые помогут точно определить класс заявки."
            
            # Отправляем запрос
            response = await self.gigachat_client.generate_response(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,  # Средняя температура для разнообразия вопросов
                max_tokens=512
            )
            
            # Парсим ответ
            questions = self._parse_questions(response)
            
            # Ограничиваем количество вопросов
            if len(questions) > self.MAX_QUESTIONS:
                questions = questions[:self.MAX_QUESTIONS]
            
            logger.info(f"Сгенерировано {len(questions)} вопросов")
            return questions
            
        except Exception as e:
            logger.error(f"Ошибка при генерации вопросов: {e}")
            # Возвращаем базовые вопросы
            return [
                "Опишите подробнее, что именно не работает?",
                "Когда началась проблема?",
                "Эта проблема связана с компьютером, программой или доступом к системе?"
            ]
    
    async def analyze_with_answers(
        self, 
        ticket_text: str, 
        questions: List[str], 
        answers: List[str]
    ) -> tuple[str, float]:
        """
        Анализ заявки с учетом ответов на вопросы
        
        Args:
            ticket_text: Исходный текст заявки
            questions: Заданные вопросы
            answers: Ответы пользователя
            
        Returns:
            Tuple[class_name, confidence]
        """
        try:
            logger.info("Анализ с учетом ответов на вопросы")
            
            # Загружаем промпт классификации
            from pathlib import Path
            prompt_path = Path(__file__).parent.parent.parent / "data" / "prompts" / "prompt.txt"
            with open(prompt_path, 'r', encoding='utf-8') as f:
                classification_prompt = f.read()
            
            # Формируем контекст с вопросами и ответами
            qa_context = "\n\nДополнительная информация от пользователя:\n"
            for q, a in zip(questions, answers):
                qa_context += f"Вопрос: {q}\nОтвет: {a}\n\n"
            
            user_prompt = f"""Исходная заявка:
{ticket_text}
{qa_context}

На основе всей информации определи класс заявки.

Верни ответ СТРОГО в формате JSON:
{{
    "class": "название класса из списка",
    "confidence": 0.95,
    "reasoning": "объяснение"
}}"""
            
            # Отправляем запрос
            response = await self.gigachat_client.generate_response(
                system_prompt=classification_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=512
            )
            
            # Парсим результат
            result = self._parse_classification(response)
            
            if result:
                class_name = result.get("class", "нет классов")
                confidence = result.get("confidence", 0.0)
                reasoning = result.get("reasoning", "")
                
                logger.info(f"Финальная классификация: {class_name}, уверенность: {confidence:.2%}")
                logger.info(f"Обоснование: {reasoning}")
                
                return class_name, confidence
            else:
                logger.warning("Не удалось распарсить результат классификации")
                return "нет классов", 0.0
                
        except Exception as e:
            logger.error(f"Ошибка при анализе с ответами: {e}")
            return "нет классов", 0.0
    
    def _parse_questions(self, response: str) -> List[str]:
        """Парсинг списка вопросов из ответа"""
        try:
            # Убираем markdown маркеры
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Парсим JSON
            result = json.loads(response)
            questions = result.get("questions", [])
            
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            
            # Пытаемся извлечь вопросы построчно
            questions = []
            for line in response.split('\n'):
                line = line.strip()
                if line and '?' in line:
                    # Убираем нумерацию
                    line = line.lstrip('0123456789.-) ')
                    if line:
                        questions.append(line)
            
            return questions[:self.MAX_QUESTIONS]
    
    def _parse_classification(self, response: str) -> Optional[Dict]:
        """Парсинг результата классификации"""
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            result = json.loads(response)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return None
