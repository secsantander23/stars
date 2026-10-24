"""PatchTime: Infraestrutura experimental reproduzível para benchmark de agentes de programação."""

__version__ = "0.1.0"
__author__ = "PatchTime Contributors"

from patchtime.core.exceptions import (
    PatchTimeError,
    ConfigurationError,
    SecurityViolationError,
    IsolationError,
    ChallengeValidationError,
    ExecutionTimeoutError,
    AgentExecutionError,
    EvaluationError,
)

__all__ = [
    "__version__",
    "PatchTimeError",
    "ConfigurationError",
    "SecurityViolationError",
    "IsolationError",
    "ChallengeValidationError",
    "ExecutionTimeoutError",
    "AgentExecutionError",
    "EvaluationError",
]

