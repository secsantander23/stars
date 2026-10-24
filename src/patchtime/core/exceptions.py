"""Hierarquia formal de exceções do PatchTime.

Nenhuma falha de segurança, violação de isolamento ou inconsistência de
manifesto deve silenciar exceções genéricas.
"""

from typing import Optional


class PatchTimeError(Exception):
    """Exceção base para todas as falhas controladas do PatchTime."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Detalhes: {self.details})"
        return self.message


class ConfigurationError(PatchTimeError):
    """Disparada quando argumentos, caminhos ou configurações são inválidos."""
    pass


class SecurityViolationError(PatchTimeError):
    """Disparada diante de tentativas de path traversal, symlink malicioso ou fuga de workspace."""
    pass


class IsolationError(PatchTimeError):
    """Disparada quando o ambiente de isolamento (processo ou container) falha ao inicializar."""
    pass


class ChallengeValidationError(PatchTimeError):
    """Disparada quando um manifesto de desafio não cumpre os requisitos de esquema ou integridade."""
    pass


class ExecutionTimeoutError(PatchTimeError):
    """Disparada quando um agente ou teste ultrapassa o tempo limite configurado."""
    pass


class AgentExecutionError(PatchTimeError):
    """Disparada quando o processo do agente encerra com falha ou erro inesperado."""
    pass


class EvaluationError(PatchTimeError):
    """Disparada quando o harness de avaliação não consegue executar ou apurar os testes."""
    pass

