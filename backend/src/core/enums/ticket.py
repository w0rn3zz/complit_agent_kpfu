from enum import Enum


class TicketSource(str, Enum):
    """Источник заявки"""
    WEB_UI = "web_ui"
    KFU_API = "kfu_api"
    WEBHOOK = "webhook"
    MANUAL = "manual"
