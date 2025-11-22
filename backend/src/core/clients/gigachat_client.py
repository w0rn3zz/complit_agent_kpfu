import logging

from gigachat import GigaChat
from src.core.config import settings


logger = logging.getLogger(__name__)


class GigaChatClient:
    
    def __init__(self):
        self.api_key = settings.gigachat_credentials
        self._client = None
    
    def _get_client(self) -> GigaChat:
        if self._client is None:
            self._client = GigaChat(
                credentials=self.api_key,
                verify_ssl_certs=False,
                scope="GIGACHAT_API_PERS"
            )
        return self._client
    
    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Генерация ответа от GigaChat
        
        Args:
            system_prompt: Системный промпт
            user_prompt: Запрос пользователя
            temperature: Температура генерации (0.0-1.0) - игнорируется
            max_tokens: Максимальное количество токенов - игнорируется
            
        Returns:
            Сгенерированный ответ
        """
        try:
            client = self._get_client()
            
            # Формируем payload для GigaChat (правильный формат!)
            payload = {
                "messages": [
                    {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                ]
            }
            
            # Вызов API GigaChat
            response = client.chat(payload)
            
            # Извлекаем текст ответа
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            
            logger.error("GigaChat returned empty response")
            return "Извините, не могу сгенерировать ответ. Попробуйте еще раз."
                
        except Exception as e:
            logger.error(f"GigaChat error: {e}")
            return "Произошла ошибка при генерации ответа. Пожалуйста, попробуйте позже."
    
    def close(self):
        if self._client:
            self._client = None
