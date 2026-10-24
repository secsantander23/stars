"""Ponto de entrada principal da Interface de Linha de Comando do PatchTime."""

import argparse
import sys
from typing import List, Optional

from patchtime import __version__
from patchtime.cli.commands.doctor import run_doctor


def create_parser() -> argparse.ArgumentParser:
    """Cria e configura o analisador de argumentos da CLI."""
    parser = argparse.ArgumentParser(
        prog="patchtime",
        description="PatchTime: Infraestrutura experimental para benchmark de agentes de programação em bugs reais.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Exibe a versão instalada do PatchTime e encerra.",
    )

    subparsers = parser.add_subparsers(
        title="Comandos disponíveis",
        dest="command",
        metavar="<comando>",
    )

    # Subcomando: doctor
    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Diagnostica o ambiente de execução, ferramentas necessárias e modos de isolamento.",
    )
    doctor_parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Emite o diagnóstico em formato JSON estruturado.",
    )

    # Subcomando: challenge
    challenge_parser = subparsers.add_parser(
        "challenge",
        help="Gerencia e valida desafios de benchmark.",
    )
    challenge_sub = challenge_parser.add_subparsers(dest="challenge_subcommand", metavar="<ação>")
    challenge_list = challenge_sub.add_parser("list", help="Lista desafios locais disponíveis.")
    challenge_list.add_argument("--dir", default="./challenges", help="Diretório de busca dos desafios.")
    challenge_validate = challenge_sub.add_parser("validate", help="Valida conformidade do manifesto de um desafio.")
    challenge_validate.add_argument("path", help="Caminho do arquivo de desafio (challenge.json).")

    # Subcomando: benchmark
    benchmark_parser = subparsers.add_parser(
        "benchmark",
        help="Executa e compara baterias de testes com agentes.",
    )
    benchmark_sub = benchmark_parser.add_subparsers(dest="benchmark_subcommand", metavar="<ação>")
    benchmark_run = benchmark_sub.add_parser("run", help="Executa uma tentativa com um agente sobre um desafio.")
    benchmark_run.add_argument("--challenge", required=True, help="Identificador ou caminho do desafio.")
    benchmark_run.add_argument("--agent", required=True, help="Nome do adaptador de agente a ser utilizado.")
    benchmark_run.add_argument("--timeout", type=int, default=300, help="Tempo limite em segundos.")
    benchmark_compare = benchmark_sub.add_parser("compare", help="Compara execuções distintas de agentes.")
    benchmark_compare.add_argument("run1", help="ID da primeira execução.")
    benchmark_compare.add_argument("run2", help="ID da segunda execução.")

    # Subcomando: results
    results_parser = subparsers.add_parser(
        "results",
        help="Consulta e exporta relatórios de execuções passadas.",
    )
    results_sub = results_parser.add_subparsers(dest="results_subcommand", metavar="<ação>")
    results_show = results_sub.add_parser("show", help="Exibe detalhes de uma execução específica.")
    results_show.add_argument("run_id", help="Identificador da execução.")
    results_export = results_sub.add_parser("export", help="Exporta dados estruturados da execução.")
    results_export.add_argument("run_id", help="Identificador da execução.")
    results_export.add_argument("--format", default="json", choices=["json"], help="Formato de exportação.")

    # Subcomando: repo
    repo_parser = subparsers.add_parser(
        "repo",
        help="Inspeciona repositórios Git em busca de candidatos a bugs históricos.",
    )
    repo_sub = repo_parser.add_subparsers(dest="repo_subcommand", metavar="<ação>")
    repo_inspect = repo_sub.add_parser("inspect", help="Analisa o histórico Git e detecta potenciais correções de bugs.")
    repo_inspect.add_argument("path_or_url", help="Caminho local ou URL de clone do repositório.")
    repo_inspect.add_argument("--min-confidence", type=float, default=0.7, help="Limiar mínimo de confiança (0.0 a 1.0).")

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Ponto de entrada executável do utilitário."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    if parsed_args.command == "doctor":
        return run_doctor(output_json=parsed_args.output_json)

    # Subcomandos das próximas fases (ainda em desenvolvimento)
    print(
        f"Comando '{parsed_args.command}' reconhecido no contrato da CLI, "
        f"mas sua implementação completa pertence à fase subsequente do roadmap (consulte AGENT.md)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

