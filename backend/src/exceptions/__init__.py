"""Базовые исключения приложения"""


class ApplicationException(Exception):
    """Базовое исключение приложения"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class TicketAnalysisException(ApplicationException):
    """Исключение при анализе заявки"""
    pass


class KFUIntegrationException(ApplicationException):
    """Исключение при интеграции с КФУ"""
    pass


class AIProviderException(ApplicationException):
    """Исключение при работе с AI провайдером"""
    pass
