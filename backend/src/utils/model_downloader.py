"""
Автоматическая загрузка ML моделей из Hugging Face
"""
import logging
from pathlib import Path
from transformers import AutoTokenizer, AutoModel

logger = logging.getLogger(__name__)

HUGGINGFACE_MODEL = "cointegrated/rubert-tiny2"


def download_models(models_dir: Path) -> bool:
    """
    Загружает модели из Hugging Face если они отсутствуют
    
    Args:
        models_dir: Директория для сохранения моделей
        
    Returns:
        bool: True если модели загружены успешно
    """
    try:
        models_dir.mkdir(parents=True, exist_ok=True)
        bert_model_path = models_dir / "rubert-tiny2-local"
        
        model_file = bert_model_path / "model.safetensors"
        if bert_model_path.exists() and model_file.exists():
            logger.info(f"Модель уже загружена: {bert_model_path}")
            return True
        
        logger.info(f"Загрузка {HUGGINGFACE_MODEL} из Hugging Face (это может занять несколько минут)...")
        print(f"[MODEL] Downloading {HUGGINGFACE_MODEL} from Hugging Face...", flush=True)
        
        tokenizer = AutoTokenizer.from_pretrained(HUGGINGFACE_MODEL)
        tokenizer.save_pretrained(str(bert_model_path))
        
        model = AutoModel.from_pretrained(HUGGINGFACE_MODEL)
        model.save_pretrained(str(bert_model_path))
        
        logger.info(f"Модель успешно загружена в {bert_model_path}")
        print(f"[MODEL] Successfully downloaded to {bert_model_path}", flush=True)
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке моделей: {e}")
        print(f"[MODEL] Download failed: {e}", flush=True)
        return False


def ensure_models_available(models_dir: Path) -> bool:
    """
    Проверяет наличие моделей и загружает при необходимости
    
    Args:
        models_dir: Директория с моделями
        
    Returns:
        bool: True если модели доступны
    """
    bert_model_path = models_dir / "rubert-tiny2-local"
    classifier_path = models_dir / "logistic_classifier_new_dataset.pkl"
    tokenizer_path = models_dir / "tokenizer_new_dataset.pkl"
    model_file = bert_model_path / "model.safetensors"
    
    if not (bert_model_path.exists() and model_file.exists()):
        logger.info("BERT модель не найдена, начинается загрузка...")
        if not download_models(models_dir):
            return False
    
    missing = []
    if not classifier_path.exists():
        missing.append("logistic_classifier_new_dataset.pkl")
    if not tokenizer_path.exists():
        missing.append("tokenizer_new_dataset.pkl")
    
    if missing:
        logger.warning(f"Отсутствуют файлы: {', '.join(missing)}")
        return False
    
    return True
