"""Модуль агентов для обработки заявок"""

from .abbreviation_convert import AbbreviationConvertAgent
from .ticket_analyzer import TicketAnalyzerAgent
from .deep_ticket_analyzer import DeepTicketAnalyzerAgent
from .question_generator import QuestionGeneratorAgent
from .system_control import SystemControlAgent

__all__ = [
    "AbbreviationConvertAgent",
    "TicketAnalyzerAgent",
    "DeepTicketAnalyzerAgent",
    "QuestionGeneratorAgent",
    "SystemControlAgent",
]
