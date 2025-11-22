"""
WebSocket endpoint для real-time обновлений
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List


class ConnectionManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Отправка сообщения всем подключенным клиентам"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()
router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/updates")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint для получения real-time обновлений о работе агентов
    
    Клиент подключается и получает обновления в формате:
    {
        "type": "agent_step" | "progress" | "completed",
        "ticket_id": str,
        "agent_name": str,
        "action": str,
        "result": str
    }
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Ожидаем сообщений от клиента (ping/pong)
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
