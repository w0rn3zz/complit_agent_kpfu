"""API v1 endpoints"""

from fastapi import APIRouter
from . import tickets, websocket

router = APIRouter(prefix="/api/v1")

router.include_router(tickets.router)
router.include_router(websocket.router)

__all__ = ["router"]
