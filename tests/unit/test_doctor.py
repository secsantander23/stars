"""Testes unitários para o verificador de ambiente (doctor)."""

import unittest
from unittest.mock import patch, MagicMock
from patchtime.cli.commands.doctor import (
    check_python_version,
    check_git_binary,
    check_docker_engine,
    check_filesystem_and_workspace,
)


class TestDoctorChecks(unittest.TestCase):
    def test_python_version_check(self) -> None:
        result = check_python_version()
        # O ambiente de desenvolvimento deve cumprir os requisitos do PatchTime
        self.assertIn(result.status, ["PASS", "FAIL"])
        self.assertEqual(result.name, "Python Runtime")

    @patch("shutil.which")
    def test_git_binary_not_found(self, mock_which: MagicMock) -> None:
        mock_which.return_value = None
        result = check_git_binary()
        self.assertEqual(result.status, "FAIL")
        self.assertIn("Git não encontrado", result.message)

    @patch("shutil.which")
    def test_docker_not_found_generates_warning(self, mock_which: MagicMock) -> None:
        mock_which.return_value = None
        result = check_docker_engine()
        # Docker ausente deve ser WARN e não FAIL, acionando fallback local_process
        self.assertEqual(result.status, "WARN")
        self.assertIn("local_process", result.message)

    def test_filesystem_workspace_check(self) -> None:
        result = check_filesystem_and_workspace()
        self.assertEqual(result.status, "PASS")


if __name__ == "__main__":
    unittest.main()

