"""Testes unitários para os modelos de dados e manifestos do PatchTime."""

import unittest
from patchtime.core.models import (
    ResourceLimits,
    DoctorReport,
    CheckResult,
    ProblemStatement,
    ChallengeProvenance,
    ChallengeMetadata,
    ChallengeManifest,
    EvaluationVerdict,
)


class TestModels(unittest.TestCase):
    def test_resource_limits_defaults(self) -> None:
        limits = ResourceLimits()
        self.assertEqual(limits.timeout_seconds, 300)
        self.assertEqual(limits.max_memory_mb, 2048)
        self.assertEqual(limits.max_cpu_cores, 2)
        d = limits.to_dict()
        self.assertEqual(d["timeout_seconds"], 300)

    def test_doctor_report_operational_status(self) -> None:
        # Relatório com apenas PASS e WARN deve ser operacional
        report = DoctorReport(
            checks=[
                CheckResult(name="Python", status="PASS", message="OK"),
                CheckResult(name="Docker", status="WARN", message="Aviso isolamento local"),
            ]
        )
        self.assertTrue(report.is_operational)

        # Relatório com FAIL não deve ser operacional
        report_fail = DoctorReport(
            checks=[
                CheckResult(name="Git", status="FAIL", message="Git ausente"),
            ]
        )
        self.assertFalse(report_fail.is_operational)

    def test_challenge_secret_redaction(self) -> None:
        prov = ChallengeProvenance(
            base_commit="abc1234",
            reference_commit_hash="secret_fix_5678",
            issue_reference="https://github.com/example/issue/1",
        )
        # Manifesto público redige a solução
        public_dict = prov.to_dict(redact_secret=True)
        self.assertNotIn("reference_commit_hash", public_dict)
        self.assertEqual(public_dict["base_commit"], "abc1234")

        # Manifesto privado preserva o segredo de referência
        private_dict = prov.to_dict(redact_secret=False)
        self.assertEqual(private_dict["reference_commit_hash"], "secret_fix_5678")

    def test_evaluation_verdict_resolution(self) -> None:
        verdict = EvaluationVerdict(
            status="RESOLVED",
            summary="Bug resolvido com sucesso",
            fail_to_pass_passed=["test_bug"],
            pass_to_pass_passed=["test_regression_1"],
        )
        self.assertTrue(verdict.is_resolved)

        # Se houver falhas no pass-to-pass (regressão), não é considerado resolvido
        verdict_with_regression = EvaluationVerdict(
            status="RESOLVED",
            summary="Bug resolvido mas com regressão",
            fail_to_pass_passed=["test_bug"],
            pass_to_pass_failed=["test_regression_1"],
        )
        self.assertFalse(verdict_with_regression.is_resolved)


if __name__ == "__main__":
    unittest.main()

