"""
Сервис для анализа заявок
Использует multi-agent подход для классификации и обработки заявок
"""
import asyncio
import time
from typing import Dict, Any, List
from uuid import uuid4
from openai import AsyncOpenAI

from src.core.config import settings
from src.core.schemas import AnalysisResult, WorkTypeMatch, AgentStep
from src.core.models import get_work_type_by_id, get_all_work_types
from src.dao import WorkTypeDAO


class TicketAnalyzerService:
    """Сервис для анализа и классификации заявок"""
    
    def __init__(self):
        self.work_type_dao = WorkTypeDAO()
        self.client = self._init_llm_client()
    
    def _init_llm_client(self):
        """Инициализация LLM клиента"""
        if settings.ai_provider == "openai":
            return AsyncOpenAI(api_key=settings.openai_api_key)
        # TODO: Добавить поддержку других провайдеров (GigaChat, Yandex)
        return AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def analyze_ticket(self, ticket_text: str, ticket_id: str = None) -> AnalysisResult:
        """
        Основной метод анализа заявки
        
        Этапы:
        1. Проверка релевантности департаменту
        2. Классификация типа работ
        3. Расчет уверенности
        4. Валидация полноты информации
        5. Генерация объяснений
        """
        start_time = time.time()
        
        if ticket_id is None:
            ticket_id = str(uuid4())
        
        agent_steps = []
        
        # Параллельный запуск проверки релевантности и классификации
        relevance_task = self._check_relevance(ticket_text)
        classifier_task = self._classify_work_types(ticket_text)
        
        relevance_result, classifier_result = await asyncio.gather(
            relevance_task,
            classifier_task
        )
        
        agent_steps.extend([relevance_result["step"], classifier_result["step"]])
        
        is_relevant = relevance_result["is_relevant"]
        possible_work_types = classifier_result["possible_work_types"]
        
        # Если заявка нерелевантна, возвращаем результат сразу
        if not is_relevant:
            processing_time = int((time.time() - start_time) * 1000)
            return AnalysisResult(
                ticket_id=ticket_id,
                is_relevant=False,
                matches=[],
                agent_steps=agent_steps,
                processing_time_ms=processing_time,
                metadata={
                    "relevance_reason": relevance_result["reason"],
                    "message": "Данная заявка не относится к компетенции департамента информатизации и связи"
                }
            )
        
        # Расчет уверенности для каждого типа работ
        confidence_result = await self._calculate_confidence(ticket_text, possible_work_types)
        agent_steps.append(confidence_result["step"])
        
        # Генерация объяснений
        explanation_result = await self._generate_explanations(
            ticket_text, 
            confidence_result["confidence_scores"]
        )
        agent_steps.append(explanation_result["step"])
        
        # Формирование списка совпадений
        matches = self._build_matches(
            confidence_result["confidence_scores"],
            explanation_result["explanations"]
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return AnalysisResult(
            ticket_id=ticket_id,
            is_relevant=is_relevant,
            matches=matches,
            agent_steps=agent_steps,
            processing_time_ms=processing_time,
            metadata={
                "classifier_reasoning": classifier_result.get("reasoning", "")
            }
        )
    
    async def _check_relevance(self, ticket_text: str) -> Dict[str, Any]:
        """Проверка релевантности заявки департаменту информатизации"""
        system_prompt = """Ты - агент по проверке релевантности заявок для департамента информатизации и связи КФУ.
        
Твоя задача: определить, относится ли заявка к компетенции IT-департамента.

К IT-департаменту относятся:
- Компьютеры, ноутбуки, принтеры, сканеры
- Программное обеспечение
- Сеть, интернет, WiFi
- Учетные записи, доступы
- Электронная почта
- Сайты, порталы
- Видеосвязь (Zoom, Teams)

НЕ относятся к IT:
- Ремонт помещений
- Сантехника, отопление
- Канцтовары
- Кадровые вопросы
- Расписание занятий
- Финансовые вопросы

Ответь в формате JSON:
{
  "is_relevant": true/false,
  "reason": "краткое объяснение"
}"""
        
        user_prompt = f"Заявка: {ticket_text}"
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            return {
                "is_relevant": result.get("is_relevant", True),
                "reason": result.get("reason", ""),
                "step": AgentStep(
                    agent_name="RelevanceAgent",
                    action="Проверка релевантности департаменту",
                    result=f"Релевантна: {result.get('is_relevant')}"
                )
            }
        except Exception as e:
            print(f"Error in _check_relevance: {e}")
            return {
                "is_relevant": True,
                "reason": "Ошибка при проверке",
                "step": AgentStep(
                    agent_name="RelevanceAgent",
                    action="Проверка релевантности департаменту",
                    result="Ошибка"
                )
            }
    
    async def _classify_work_types(self, ticket_text: str) -> Dict[str, Any]:
        """Классификация типов работ"""
        work_types = self.work_type_dao.get_all()
        
        # Формируем описание всех типов работ для LLM
        work_types_desc = "\n".join([
            f"ID: {wt.id}\nНазвание: {wt.name}\nКатегория: {wt.category.value}\nОписание: {wt.description}\nКлючевые слова: {', '.join(wt.keywords)}\n"
            for wt in work_types
        ])
        
        system_prompt = f"""Ты - агент по классификации заявок в IT-поддержку КФУ.

Доступные типы работ:
{work_types_desc}

Проанализируй заявку и выбери ДО 3 наиболее подходящих типов работ.
Ответь в формате JSON:
{{
  "work_type_ids": ["id1", "id2", "id3"],
  "reasoning": "краткое объяснение выбора"
}}"""
        
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
            
            return {
                "possible_work_types": result.get("work_type_ids", []),
                "reasoning": result.get("reasoning", ""),
                "step": AgentStep(
                    agent_name="ClassifierAgent",
                    action="Классификация типов работ",
                    result=f"Найдено {len(result.get('work_type_ids', []))} типов"
                )
            }
        except Exception as e:
            print(f"Error in _classify_work_types: {e}")
            return {
                "possible_work_types": [],
                "reasoning": "",
                "step": AgentStep(
                    agent_name="ClassifierAgent",
                    action="Классификация типов работ",
                    result="Ошибка"
                )
            }
    
    async def _calculate_confidence(self, ticket_text: str, work_type_ids: List[str]) -> Dict[str, Any]:
        """Расчет уверенности для каждого типа работ"""
        if not work_type_ids:
            return {
                "confidence_scores": {},
                "step": AgentStep(
                    agent_name="ConfidenceAgent",
                    action="Расчет уверенности",
                    result="Нет типов для анализа"
                )
            }
        
        system_prompt = f"""Ты - агент по оценке уверенности соответствия заявки типам работ.

Оцени уверенность (от 0.0 до 1.0) для каждого типа работ.

Ответь в формате JSON:
{{
  "work_type_id": confidence_score,
  ...
}}

Пример: {{"hw_001": 0.85, "sw_001": 0.65}}"""
        
        work_types_info = []
        for wt_id in work_type_ids:
            wt = get_work_type_by_id(wt_id)
            if wt:
                work_types_info.append(f"{wt.id}: {wt.name} - {wt.description}")
        
        user_prompt = f"""Заявка: {ticket_text}

Типы работ:
{chr(10).join(work_types_info)}

Оцени уверенность для каждого типа."""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            scores = json.loads(response.choices[0].message.content)
            
            return {
                "confidence_scores": scores,
                "step": AgentStep(
                    agent_name="ConfidenceAgent",
                    action="Расчет уверенности для типов работ",
                    result=f"Оценено {len(scores)} типов"
                )
            }
        except Exception as e:
            print(f"Error in _calculate_confidence: {e}")
            # Fallback: равномерное распределение
            scores = {wt_id: 1.0 / len(work_type_ids) for wt_id in work_type_ids}
            return {
                "confidence_scores": scores,
                "step": AgentStep(
                    agent_name="ConfidenceAgent",
                    action="Расчет уверенности для типов работ",
                    result="Использованы значения по умолчанию"
                )
            }
    
    async def _generate_explanations(self, ticket_text: str, confidence_scores: Dict[str, float]) -> Dict[str, Any]:
        """Генерация объяснений для каждого варианта"""
        explanations = {}
        
        for work_type_id, score in confidence_scores.items():
            wt = get_work_type_by_id(work_type_id)
            if not wt:
                continue
            
            system_prompt = f"""Ты - агент по генерации объяснений.
            
Объясни кратко (1-2 предложения), почему заявка соответствует данному типу работ.

Тип работ: {wt.name}
Описание: {wt.description}
Уверенность: {score:.0%}"""
            
            user_prompt = f"Заявка: {ticket_text}"
            
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
                
                explanations[work_type_id] = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error generating explanation for {work_type_id}: {e}")
                explanations[work_type_id] = f"Заявка содержит признаки типа работ '{wt.name}'"
        
        return {
            "explanations": explanations,
            "step": AgentStep(
                agent_name="ExplanationAgent",
                action="Генерация объяснений",
                result=f"Создано {len(explanations)} объяснений"
            )
        }
    
    def _build_matches(self, confidence_scores: Dict[str, float], explanations: Dict[str, str]) -> List[WorkTypeMatch]:
        """Формирование списка совпадений с сортировкой по уверенности"""
        matches = []
        
        # Сортируем по уверенности
        sorted_scores = sorted(confidence_scores.items(), key=lambda x: x[1], reverse=True)
        
        for work_type_id, confidence in sorted_scores:
            wt = get_work_type_by_id(work_type_id)
            if wt:
                matches.append(WorkTypeMatch(
                    work_type_id=wt.id,
                    work_type_name=wt.name,
                    category=wt.category,
                    confidence=confidence,
                    reasoning=explanations.get(work_type_id, f"Соответствует типу работ '{wt.name}'")
                ))
        
        return matches
