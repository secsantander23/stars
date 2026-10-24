"""Implementação do comando 'patchtime doctor'."""

import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

from patchtime.core.models import CheckResult, DoctorReport


def check_python_version() -> CheckResult:
    """Verifica se o interpretador Python cumpre o requisito mínimo (>= 3.12)."""
    major, minor, micro = sys.version_info[:3]
    version_str = f"{major}.{minor}.{micro}"
    if sys.version_info >= (3, 12):
        return CheckResult(
            name="Python Runtime",
            status="PASS",
            message=f"Python {version_str} atende ao requisito (>= 3.12)",
            details=sys.executable,
        )
    return CheckResult(
        name="Python Runtime",
        status="FAIL",
        message=f"Python {version_str} incompatível. O PatchTime requer Python >= 3.12.",
        details=sys.executable,
    )


def check_git_binary() -> CheckResult:
    """Verifica a presença e versão do utilitário Git."""
    git_path = shutil.which("git")
    if not git_path:
        return CheckResult(
            name="Git CLI",
            status="FAIL",
            message="Git não encontrado no PATH. O PatchTime depende do Git para mineração e snapshots.",
        )
    try:
        proc = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        version_str = proc.stdout.strip()
        return CheckResult(
            name="Git CLI",
            status="PASS",
            message=f"{version_str} detectado e operacional",
            details=git_path,
        )
    except Exception as exc:
        return CheckResult(
            name="Git CLI",
            status="FAIL",
            message=f"Erro ao consultar versão do Git: {exc}",
            details=git_path,
        )


def check_docker_engine() -> CheckResult:
    """Verifica a presença do daemon Docker para isolamento baseado em contêineres."""
    docker_path = shutil.which("docker")
    if not docker_path:
        return CheckResult(
            name="Isolamento Docker",
            status="WARN",
            message="Docker não encontrado no PATH. O PatchTime operará com isolamento nativo (local_process).",
            details="Para ambientes multi-tenant e proteção máxima, instale e inicie o Docker Desktop/Engine.",
        )
    try:
        proc = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if proc.returncode == 0:
            return CheckResult(
                name="Isolamento Docker",
                status="PASS",
                message="Daemon Docker ativo e pronto para isolamento conteinerizado OCI",
                details=docker_path,
            )
        return CheckResult(
            name="Isolamento Docker",
            status="WARN",
            message="Binário Docker encontrado, mas o daemon não parece ativo. Modo ativo: local_process.",
            details=proc.stderr.strip() or "Daemon inativo",
        )
    except Exception as exc:
        return CheckResult(
            name="Isolamento Docker",
            status="WARN",
            message=f"Falha ao consultar Docker: {exc}. Modo ativo: local_process.",
            details=docker_path,
        )


def check_filesystem_and_workspace() -> CheckResult:
    """Verifica se o sistema de arquivos permite criação e limpeza de workspaces temporários."""
    try:
        with tempfile.TemporaryDirectory(prefix="patchtime_doctor_") as tmp_dir:
            test_file = Path(tmp_dir) / "write_probe.tmp"
            test_file.write_text("patchtime probe", encoding="utf-8")
            content = test_file.read_text(encoding="utf-8")
            if content != "patchtime probe":
                raise IOError("Conteúdo lido difere do gravado")
        return CheckResult(
            name="Workspace Temporário",
            status="PASS",
            message="Criação, escrita e limpeza de diretórios efêmeros operando com segurança",
            details=tempfile.gettempdir(),
        )
    except Exception as exc:
        return CheckResult(
            name="Workspace Temporário",
            status="FAIL",
            message=f"Falha ao manipular diretório temporário: {exc}",
            details=tempfile.gettempdir(),
        )


def run_doctor(output_json: bool = False) -> int:
    """Executa todas as verificações do ambiente e emite relatório."""
    report = DoctorReport()
    report.python_version = platform.python_version()

    checks = [
        check_python_version(),
        check_git_binary(),
        check_docker_engine(),
        check_filesystem_and_workspace(),
    ]
    report.checks = checks

    # Extrai dados dos checks
    for check in checks:
        if check.name == "Git CLI" and check.status == "PASS" and check.details:
            report.git_version = check.message
        elif check.name == "Isolamento Docker":
            if check.status == "PASS":
                report.docker_available = True
                report.isolation_mode = "container"
            else:
                report.docker_available = False
                report.isolation_mode = "local_process"

    if output_json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return 0 if report.is_operational else 1

    # Saída formatada amigável para terminal
    print("=" * 68)
    print("  PATCHTIME DOCTOR — Diagnóstico de Ambiente & Isolamento")
    print("=" * 68)
    print(f"Sistema Operacional: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Modo de Isolamento Padrão: {report.isolation_mode.upper()}")
    print("-" * 68)

    badge_map = {
        "PASS": "[  OK  ]",
        "WARN": "[ AVISO]",
        "FAIL": "[FALHA ]",
    }

    for check in report.checks:
        badge = badge_map.get(check.status, "[ ???  ]")
        print(f"{badge} {check.name}: {check.message}")
        if check.details and check.status in ("WARN", "FAIL"):
            print(f"         └─ Nota: {check.details}")

    print("-" * 68)
    if report.is_operational:
        print("Status Final: OPERACIONAL. O PatchTime está pronto para execução.")
        if not report.docker_available:
            print("Observação: Usando fallback de processos locais isolados para execuções.")
        print("=" * 68)
        return 0
    else:
        print("Status Final: BLOQUEADO. Corrija as falhas acima antes de prosseguir.")
        print("=" * 68)
        return 1

