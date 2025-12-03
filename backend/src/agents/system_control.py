"""Системный контроллер для управления цепочкой агентов"""
import logging
from typing import Optional, List, Dict
from enum import Enum

from .abbreviation_convert import AbbreviationConvertAgent
from .ticket_analyzer import TicketAnalyzerAgent
from .deep_ticket_analyzer import DeepTicketAnalyzerAgent
from .question_generator import QuestionGeneratorAgent

logger = logging.getLogger(__name__)


class ProcessingStage(str, Enum):
    """Стадии обработки заявки"""
    ABBREVIATION_CONVERT = "abbreviation_convert"
    ML_CLASSIFICATION = "ml_classification"
    DEEP_ANALYSIS = "deep_analysis"
    QUESTION_GENERATION = "question_generation"
    FINAL_ANALYSIS = "final_analysis"
    COMPLETED = "completed"


class ClassificationResult:
    """Результат классификации заявки"""
    
    def __init__(
        self,
        stage: ProcessingStage,
        ticket_class: Optional[str] = None,
        confidence: Optional[float] = None,
        questions: Optional[List[str]] = None,
        processed_text: Optional[str] = None,
        reasoning: Optional[str] = None
    ):
        self.stage = stage
        self.ticket_class = ticket_class
        self.confidence = confidence
        self.questions = questions
        self.processed_text = processed_text
        self.reasoning = reasoning
    
    def to_dict(self) -> Dict:
        """Конвертация в словарь для API"""
        return {
            "stage": self.stage,
            "ticket_class": self.ticket_class,
            "confidence": self.confidence,
            "questions": self.questions,
            "processed_text": self.processed_text,
            "reasoning": self.reasoning
        }


class SystemControlAgent:
    """
    Главный контроллер системы агентов.
    Управляет цепочкой обработки заявки.
    """
    
    def __init__(self):
        self.abbreviation_agent = AbbreviationConvertAgent()
        self.ml_agent = TicketAnalyzerAgent()
        self.deep_agent = DeepTicketAnalyzerAgent()
        self.question_agent = QuestionGeneratorAgent()
    
    async def process_ticket(self, ticket_text: str) -> ClassificationResult:
        """
        Основной метод обработки заявки
        
        Цепочка:
        1. AbbreviationConvert - исправление аббревиатур
        2. TicketAnalyzer (ML) - классификация
           - Если confidence >= 90% -> возврат результата
           - Иначе -> переход к 3
        3. DeepTicketAnalyzer (GigaChat) - глубокий анализ
           - Если удалось классифицировать -> возврат результата
           - Иначе -> переход к 4
        4. QuestionGenerator - генерация вопросов
        
        Args:
            ticket_text: Исходный текст заявки
            
        Returns:
            ClassificationResult с результатом или вопросами
        """
        try:
            logger.info("Начало обработки заявки")
            
            processed_text = await self.abbreviation_agent.process(ticket_text)
            should_continue, ml_class, ml_confidence = await self.ml_agent.analyze(processed_text)
            
            if not should_continue and ml_class:
                logger.info(f"ML: {ml_class} ({ml_confidence:.2%})")
                return ClassificationResult(
                    stage=ProcessingStage.ML_CLASSIFICATION,
                    ticket_class=ml_class,
                    confidence=ml_confidence,
                    processed_text=processed_text,
                    reasoning="Классифицировано ML моделью с высокой уверенностью"
                )
            
            should_continue, deep_class, deep_confidence = await self.deep_agent.analyze(processed_text)
            
            if not should_continue and deep_class:
                logger.info(f"Deep: {deep_class} ({deep_confidence:.2%})")
                return ClassificationResult(
                    stage=ProcessingStage.DEEP_ANALYSIS,
                    ticket_class=deep_class,
                    confidence=deep_confidence,
                    processed_text=processed_text,
                    reasoning="Классифицировано GigaChat с высокой уверенностью"
                )
            
            questions = await self.question_agent.generate_questions(
                ticket_text=processed_text,
                ml_class=ml_class or deep_class
            )
            
            return ClassificationResult(
                stage=ProcessingStage.QUESTION_GENERATION,
                questions=questions,
                processed_text=processed_text,
                ticket_class=ml_class or deep_class,  # Предварительный класс
                confidence=ml_confidence or deep_confidence,
                reasoning="Требуется дополнительная информация от пользователя"
            )
            
        except Exception as e:
            logger.error(f"Ошибка в процессе обработки: {e}", exc_info=True)
            raise
    
    async def process_with_answers(
        self,
        ticket_text: str,
        questions: List[str],
        answers: List[str]
    ) -> ClassificationResult:
        """
        Финальная обработка заявки с ответами на вопросы
        
        Args:
            ticket_text: Исходный текст заявки (уже обработанный)
            questions: Вопросы, которые были заданы
            answers: Ответы пользователя
            
        Returns:
            ClassificationResult с финальным результатом
        """
        try:
            logger.info("Финальный анализ с ответами")
            
            # Используем QuestionGenerator для анализа с учетом ответов
            final_class, final_confidence = await self.question_agent.analyze_with_answers(
                ticket_text=ticket_text,
                questions=questions,
                answers=answers
            )
            
            logger.info(f"Финальная классификация: {final_class} ({final_confidence:.2%})")
            
            return ClassificationResult(
                stage=ProcessingStage.COMPLETED,
                ticket_class=final_class,
                confidence=final_confidence,
                processed_text=ticket_text,
                reasoning="Классифицировано на основе дополнительных ответов пользователя"
            )
            
        except Exception as e:
            logger.error(f"Ошибка в финальной обработке: {e}", exc_info=True)
            raise
