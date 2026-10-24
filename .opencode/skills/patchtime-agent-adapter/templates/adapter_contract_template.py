"""Template de Contrato para Novos Adaptadores de Agentes de IA no PatchTime."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

from patchtime.core.models import ProblemStatement, ResourceLimits


@dataclass(frozen=True)
class AdapterValidationResult:
    """Resultado da checagem de pré-requisitos de um adaptador de agente."""
    is_available: bool
    version: Optional[str] = None
    error_message: Optional[str] = None
    install_guidance: Optional[str] = None


@dataclass(frozen=True)
class AgentExecutionOutput:
    """Saída normalizada da tentativa executada por um agente de programação."""
    adapter_name: str
    status: str  # "SUCCESS_EXIT", "AGENT_CRASH", "INFRA_TIMEOUT", "INFRA_ERROR"
    exit_code: int
    execution_time_seconds: float
    stdout: str
    stderr: str
    patch_diff: Optional[str] = None
    modified_files: List[str] = None
    token_usage: Optional[Dict[str, int]] = None
    cost_estimate_usd: Optional[float] = None


class BaseAgentAdapter(ABC):
    """Interface abstrata obrigatória para todos os adaptadores de agentes."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Identificador curto do adaptador (ex.: 'claude-code', 'chatgpt-o3', 'aider')."""
        pass

    @abstractmethod
    def validate_environment(self) -> AdapterValidationResult:
        """Verifica se o executável, SDK ou chaves necessárias estão acessíveis."""
        pass

    @abstractmethod
    def run_attempt(
        self,
        workspace_dir: Path,
        problem: ProblemStatement,
        limits: ResourceLimits,
    ) -> AgentExecutionOutput:
        """Executa a tentativa do agente dentro do workspace higienizado.
        
        Args:
            workspace_dir: Diretório temporário isolado contendo o código no commit base.
            problem: Enunciado sanitizado do bug.
            limits: Limites de timeout, memória e CPU.
            
        Returns:
            AgentExecutionOutput com o resultado bruto e o diff produzido.
        """
        pass

