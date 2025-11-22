import httpx
from typing import Dict, Any, Optional
from src.core.config import settings
from src.core.schemas import KFUCallbackResponse
import asyncio


class KFUApiClient:
    """Клиент для работы с API КФУ"""
    
    def __init__(self):
        self.base_url = settings.kfu_api_url
        self.api_key = settings.kfu_api_key
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    async def send_classification_result(self, callback_url: str, result: KFUCallbackResponse) -> bool:
        """
        Отправка результата классификации обратно в КФУ
        
        При интеграции с реальным API КФУ:
        - Раскомментировать код ниже
        - Настроить правильный callback_url
        - Добавить обработку ошибок
        """
        try:
            # TODO: Раскомментировать при интеграции с КФУ
            # response = await self.client.post(
            #     callback_url,
            #     json=result.model_dump(mode='json')
            # )
            # response.raise_for_status()
            
            # Заглушка для разработки
            print(f"[MOCK] Sending result to KFU callback: {callback_url}")
            print(f"[MOCK] Result: {result.model_dump_json(indent=2)}")
            return True
            
        except httpx.HTTPError as e:
            print(f"Error sending result to KFU: {e}")
            return False
    
    async def get_ticket_details(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение деталей заявки из КФУ
        
        При интеграции с реальным API КФУ:
        - Раскомментировать код ниже
        - Настроить правильный endpoint
        """
        try:
            # TODO: Раскомментировать при интеграции с КФУ
            # response = await self.client.get(f"/tickets/{ticket_id}")
            # response.raise_for_status()
            # return response.json()
            
            # Заглушка для разработки
            print(f"[MOCK] Fetching ticket details for: {ticket_id}")
            return {
                "ticket_id": ticket_id,
                "status": "open",
                "title": "Test ticket",
                "description": "Test description"
            }
            
        except httpx.HTTPError as e:
            print(f"Error fetching ticket from KFU: {e}")
            return None
    
    async def update_ticket_status(self, ticket_id: str, status: str, assigned_to: Optional[str] = None) -> bool:
        """
        Обновление статуса заявки в КФУ
        
        При интеграции с реальным API КФУ:
        - Раскомментировать код ниже
        - Настроить правильный endpoint
        """
        try:
            # TODO: Раскомментировать при интеграции с КФУ
            # payload = {"status": status}
            # if assigned_to:
            #     payload["assigned_to"] = assigned_to
            # 
            # response = await self.client.patch(
            #     f"/tickets/{ticket_id}",
            #     json=payload
            # )
            # response.raise_for_status()
            
            # Заглушка для разработки
            print(f"[MOCK] Updating ticket {ticket_id} status to: {status}")
            if assigned_to:
                print(f"[MOCK] Assigning to: {assigned_to}")
            return True
            
        except httpx.HTTPError as e:
            print(f"Error updating ticket in KFU: {e}")
            return False
    
    async def close(self):
        """Закрытие клиента"""
        await self.client.aclose()


_kfu_client: Optional[KFUApiClient] = None


def get_kfu_client() -> KFUApiClient:
    """Получение singleton экземпляра KFU клиента"""
    global _kfu_client
    if _kfu_client is None:
        _kfu_client = KFUApiClient()
    return _kfu_client
