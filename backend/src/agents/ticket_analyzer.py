"""Агент для классификации заявок с использованием ML модели"""
import logging
import os
from pathlib import Path
from typing import Tuple, Optional
import joblib
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel

logger = logging.getLogger(__name__)


class TicketAnalyzerAgent:
    """
    Агент для классификации заявок с использованием обученной ML модели.
    Если уверенность > 90%, возвращает результат.
    Иначе передает управление следующему агенту.
    """
    
    CONFIDENCE_THRESHOLD = 0.90
    
    def __init__(self):
        self.tokenizer: Optional[AutoTokenizer] = None
        self.model: Optional[AutoModel] = None
        self.classifier = None
        self._load_models()
    
    def _load_models(self):
        """Загрузка моделей"""
        try:
            # Путь к моделям
            models_dir = Path(__file__).parent.parent.parent / "data" / "models"
            
            # Загрузка токенизатора
            tokenizer_path = models_dir / "tokenizer_new_dataset.pkl"
            if tokenizer_path.exists():
                logger.info(f"Загрузка токенизатора из {tokenizer_path}")
                self.tokenizer = joblib.load(str(tokenizer_path))
            else:
                logger.warning(f"Токенизатор не найден: {tokenizer_path}")
            
            # Загрузка BERT модели
            bert_model_path = models_dir / "rubert-tiny2-local"
            if bert_model_path.exists():
                logger.info(f"Загрузка BERT модели из {bert_model_path}")
                self.model = AutoModel.from_pretrained(str(bert_model_path))
                self.model.eval()  # Режим inference
            else:
                logger.warning(f"BERT модель не найдена: {bert_model_path}")
            
            # Загрузка классификатора
            classifier_path = models_dir / "logistic_classifier_new_dataset.pkl"
            if classifier_path.exists():
                logger.info(f"Загрузка классификатора из {classifier_path}")
                self.classifier = joblib.load(str(classifier_path))
            else:
                logger.warning(f"Классификатор не найден: {classifier_path}")
            
            # Проверка что все модели загружены
            if self.tokenizer and self.model and self.classifier:
                logger.info("Все модели успешно загружены")
            else:
                logger.error("Не все модели загружены!")
                
        except Exception as e:
            logger.error(f"Ошибка при загрузке моделей: {e}")
            raise
    
    async def analyze(self, text: str) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Анализ текста заявки
        
        Args:
            text: Текст заявки (уже обработанный abbreviation_convert)
            
        Returns:
            Tuple[should_continue, class_name, confidence]
            - should_continue: True если нужно передать следующему агенту
            - class_name: Название класса заявки (если определен)
            - confidence: Уверенность классификации (0-1)
        """
        try:
            if not all([self.tokenizer, self.model, self.classifier]):
                logger.error("Модели не загружены")
                return True, None, None
            
            # Получаем предсказание
            predicted_class, confidence = self._predict(text)
            
            logger.info(f"Предсказанный класс: {predicted_class}, уверенность: {confidence:.2%}")
            
            # Проверяем порог уверенности
            if confidence >= self.CONFIDENCE_THRESHOLD:
                logger.info(f"Уверенность {confidence:.2%} >= {self.CONFIDENCE_THRESHOLD:.0%}, возвращаем результат")
                return False, predicted_class, confidence
            else:
                logger.info(f"Уверенность {confidence:.2%} < {self.CONFIDENCE_THRESHOLD:.0%}, передаем следующему агенту")
                return True, predicted_class, confidence
                
        except Exception as e:
            logger.error(f"Ошибка при анализе: {e}")
            # При ошибке передаем следующему агенту
            return True, None, None
    
    def _predict(self, text: str) -> Tuple[str, float]:
        """
        Предсказание класса заявки
        
        Args:
            text: Текст заявки
            
        Returns:
            Tuple[class_name, confidence]
        """
        # Токенизация
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            padding=True, 
            max_length=256
        )
        
        # Получение эмбеддингов
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Берем [CLS] token embedding
            embeddings = outputs.last_hidden_state[:, 0, :].numpy()
        
        # Предсказание класса
        predicted_class = self.classifier.predict(embeddings)[0]
        
        # Получение вероятностей
        probabilities = self.classifier.predict_proba(embeddings)[0]
        confidence = np.max(probabilities)
        
        return predicted_class, confidence
