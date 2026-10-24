"""Testes unitários para a hierarquia de exceções do PatchTime."""

import unittest
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


class TestExceptions(unittest.TestCase):
    def test_base_exception_formatting(self) -> None:
        err = PatchTimeError("Falha genérica", details="Caminho inacessível")
        self.assertIn("Falha genérica", str(err))
        self.assertIn("Caminho inacessível", str(err))

    def test_base_exception_without_details(self) -> None:
        err = PatchTimeError("Mensagem simples")
        self.assertEqual(str(err), "Mensagem simples")

    def test_inheritance_tree(self) -> None:
        # Todas as exceções do PatchTime devem herdar de PatchTimeError
        exceptions_to_check = [
            ConfigurationError,
            SecurityViolationError,
            IsolationError,
            ChallengeValidationError,
            ExecutionTimeoutError,
            AgentExecutionError,
            EvaluationError,
        ]
        for exc_cls in exceptions_to_check:
            instance = exc_cls("Erro específico")
            self.assertIsInstance(instance, PatchTimeError)


if __name__ == "__main__":
    unittest.main()

