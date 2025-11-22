"""API v1 endpoints"""

from fastapi import APIRouter
from . import tickets

router = APIRouter(prefix="/api/v1")

router.include_router(tickets.router)

__all__ = ["router"]
