"""Modelos de dados fundamentais do PatchTime."""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


@dataclass(frozen=True)
class ResourceLimits:
    """Limites de recursos computacionais aplicados durante a execução de um desafio."""
    timeout_seconds: int = 300
    max_memory_mb: int = 2048
    max_cpu_cores: int = 2

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CheckResult:
    """Resultado individual de verificação do comando doctor."""
    name: str
    status: str  # "PASS", "WARN", "FAIL"
    message: str
    details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DoctorReport:
    """Relatório consolidado de integridade do ambiente gerado por patchtime doctor."""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_version: str = ""
    git_version: Optional[str] = None
    docker_available: bool = False
    docker_version: Optional[str] = None
    isolation_mode: str = "local_process"  # "container" ou "local_process"
    checks: List[CheckResult] = field(default_factory=list)

    @property
    def is_operational(self) -> bool:
        """Indica se os pré-requisitos essenciais para operação local estão satisfeitos."""
        return not any(check.status == "FAIL" for check in self.checks)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["is_operational"] = self.is_operational
        return data


@dataclass(frozen=True)
class ProblemStatement:
    """Enunciado descritivo do bug apresentado ao agente participante."""
    title: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChallengeProvenance:
    """Metadados de rastreabilidade e autoria histórica do desafio."""
    base_commit: str
    reference_commit_hash: Optional[str] = None  # Omitido em manifesto público
    issue_reference: Optional[str] = None

    def to_dict(self, redact_secret: bool = True) -> Dict[str, Any]:
        data = asdict(self)
        if redact_secret:
            data.pop("reference_commit_hash", None)
        return data


@dataclass(frozen=True)
class ChallengeMetadata:
    """Metadados de identificação do repositório e runtime do desafio."""
    source_repo: str
    language: str
    runtime_version: str
    created_at: str
    difficulty: str = "medium"
    provenance: Optional[ChallengeProvenance] = None

    def to_dict(self, redact_secret: bool = True) -> Dict[str, Any]:
        data = {
            "source_repo": self.source_repo,
            "language": self.language,
            "runtime_version": self.runtime_version,
            "created_at": self.created_at,
            "difficulty": self.difficulty,
        }
        if self.provenance:
            data["provenance"] = self.provenance.to_dict(redact_secret=redact_secret)
        return data


@dataclass
class ChallengeManifest:
    """Representação estruturada de um desafio de benchmark (challenge.v1.json)."""
    id: str
    schema_version: str
    metadata: ChallengeMetadata
    problem_statement: ProblemStatement
    environment: Dict[str, Any]
    evaluation: Dict[str, Any]

    def to_dict(self, redact_secret: bool = True) -> Dict[str, Any]:
        return {
            "id": self.id,
            "schema_version": self.schema_version,
            "metadata": self.metadata.to_dict(redact_secret=redact_secret),
            "problem_statement": self.problem_statement.to_dict(),
            "environment": self.environment,
            "evaluation": self.evaluation,
        }


@dataclass
class EvaluationVerdict:
    """Resultado formal apurado pela engine de avaliação sobre o patch gerado."""
    status: str  # "RESOLVED", "PARTIAL_FIX", "REGRESSION", "FAILED", "ERROR"
    summary: str
    fail_to_pass_passed: List[str] = field(default_factory=list)
    fail_to_pass_failed: List[str] = field(default_factory=list)
    pass_to_pass_passed: List[str] = field(default_factory=list)
    pass_to_pass_failed: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0

    @property
    def is_resolved(self) -> bool:
        return (
            self.status == "RESOLVED"
            and len(self.fail_to_pass_failed) == 0
            and len(self.pass_to_pass_failed) == 0
        )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["is_resolved"] = self.is_resolved
        return data

