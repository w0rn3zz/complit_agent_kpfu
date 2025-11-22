from enum import Enum


class WorkTypeCategory(str, Enum):
    """Категории типов работ"""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    ACCESS = "access"
    CONSULTATION = "consultation"
    OTHER = "other"
    NOT_RELEVANT = "not_relevant"
