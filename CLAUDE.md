# CLAUDE.md — Diretrizes para Claude & Claude Code no PatchTime

> **Guia Oficial de Operação para Claude Code CLI e Anthropic Claude**  
> Projeto: **PatchTime** | Stack: **Python 3.12+**

---

## 1. Comandos Principais de Build, Teste e Diagnóstico

```bash
# Diagnóstico de ambiente e isolamento
python -m patchtime.cli.main doctor
# ou (se instalado via pip install -e .)
patchtime doctor

# Executar toda a suíte de testes unitários do PatchTime
python -m unittest discover -s tests -p "test_*.py"

# Executar um arquivo de teste unitário específico
python -m unittest tests/unit/test_doctor.py
python -m unittest tests/unit/test_models.py
python -m unittest tests/unit/test_exceptions.py
```

---

## 2. Princípios de Engenharia e Padrões de Código

1. **Python 3.12+ com Tipagem Estrita:**
   - Todo código novo deve incluir anotações completas de tipos (`typing`).
   - Use `dataclasses(frozen=True)` para modelos imutáveis.
2. **Manipulação Segura de Arquivos:**
   - Use exclusivamente `pathlib.Path`. Nunca faça concatenação manual de strings em caminhos.
   - Valide sempre `target_path.resolve().relative_to(workspace_root.resolve())` para prevenir Path Traversal.
3. **Subprocessos Herméticos:**
   - **Veto Absoluto a `shell=True`**. Comandos devem ser passados em listas explícitas de argumentos (`["git", "archive", ...]`).
   - Todos os subprocessos devem possuir `timeout` configurado e encerramento em cascata (`tree-kill`).
4. **Isolamento de Credenciais:**
   - Chaves de API (`ANTHROPIC_API_KEY`, etc.) residem apenas no orquestrador. Nunca injete essas chaves nos workspaces onde códigos externos ou testes são executados.

---

## 3. Catálogo de Skills Especializadas (Carregamento Sob Demanda)

O Claude deve carregar e consultar os manuais especializados em `.opencode/skills/` conforme a tarefa solicitada:

| Especialidade / Tarefa | Skill a Consultar |
| :--- | :--- |
| **Mineração de Histórico & Análise de Commits** | [`.opencode/skills/patchtime-repo-forensics/SKILL.md`](.opencode/skills/patchtime-repo-forensics/SKILL.md) |
| **Criação e Validação de Desafios (`challenge.v1.json`)** | [`.opencode/skills/patchtime-challenge-authoring/SKILL.md`](.opencode/skills/patchtime-challenge-authoring/SKILL.md) |
| **Reconstrução Histórica e Expurgo de Histórico Git** | [`.opencode/skills/patchtime-snapshot-reconstruction/SKILL.md`](.opencode/skills/patchtime-snapshot-reconstruction/SKILL.md) |
| **Segurança de Sandbox, Subprocessos e Quotas** | [`.opencode/skills/patchtime-sandbox-security/SKILL.md`](.opencode/skills/patchtime-sandbox-security/SKILL.md) |
| **Avaliação Comportamental (*Fail-to-Pass* / *Pass-to-Pass*)** | [`.opencode/skills/patchtime-evaluation-integrity/SKILL.md`](.opencode/skills/patchtime-evaluation-integrity/SKILL.md) |
| **Adaptadores de Agentes (Claude Code, OpenAI, Grok, Aider)** | [`.opencode/skills/patchtime-agent-adapter/SKILL.md`](.opencode/skills/patchtime-agent-adapter/SKILL.md) |
| **Orquestração de Benchmarks e Métricas *pass@k*** | [`.opencode/skills/patchtime-benchmark-experiments/SKILL.md`](.opencode/skills/patchtime-benchmark-experiments/SKILL.md) |
| **Testes Internos e Fixtures Sintéticas do PatchTime** | [`.opencode/skills/patchtime-test-engineering/SKILL.md`](.opencode/skills/patchtime-test-engineering/SKILL.md) |

---

## 4. O que NUNCA Fazer

- **NÃO invente resultados de testes:** Execute os comandos reais e leia a saída antes de reportar.
- **NÃO exponha o patch de referência:** Durante benchmarks, a solução humana jamais pode vazar para o modelo participante.
- **NÃO crie módulos fictícios:** Implemente código real e testável de forma incremental.
- **NÃO execute comandos destrutivos no Git:** Nunca faça `git reset --hard` na árvore de trabalho principal do usuário.
