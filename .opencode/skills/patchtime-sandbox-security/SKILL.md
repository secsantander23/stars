---
name: patchtime-sandbox-security
description: Projetar, revisar e auditar o isolamento de segurança e contenção de execução de código externo e patches de agentes no PatchTime. Ative ao implementar sandboxes, auditar permissões de subprocessos, validar proteções contra path traversal ou inspecionar vazamento de credenciais.
---

# PatchTime Sandbox Security — Procedimento Operacional

## Identidade
Esta skill é o pilar de defesa do PatchTime. Ela estabelece o modelo de ameaças, as fronteiras de isolamento e as regras de contenção para execução de código de terceiros e de patches sintetizados por agentes autônomos. Código de repositórios desconhecidos e modificações feitas por IA são tratados estritamente como **binários e scripts hostis e não confiáveis**.

## Quando utilizar
- Ao desenhar ou implementar módulos em `src/patchtime/environment/`.
- Ao auditar chamadas a processos de sistema (`subprocess.Popen`, `subprocess.run`).
- Ao verificar políticas de rede, limites de memória, cotas de CPU e controle de tempo limite.
- Ao prevenir ataques de escape de workspace (Path Traversal, symlinks arbitrários, injeção de comandos).
- Ao certificar que segredos e chaves de API não estejam presentes no ambiente de execução.

## Quando não utilizar
- Para definir critérios de aprovação de testes funcionais (utilize `patchtime-evaluation-integrity`).
- Para empacotar os arquivos de um desafio (utilize `patchtime-challenge-authoring`).
- Para integrar chamadas a APIs de provedores de IA (utilize `patchtime-agent-adapter`).

## Modelo de Ameaças do PatchTime (Threat Model)

| Vetor de Ameaça | Descrição do Risco | Mitigação Obrigatória |
| :--- | :--- | :--- |
| **Execução Arbitrária no Host** | Repositório minerado ou agente executa comandos no SO hospedeiro (`rm -rf`, malware, minerador). | Execução restrita a contêiner OCI sem privilégios ou subprocesso restrito a workspace efêmero com timeout. |
| **Escape de Diretório (Path Traversal)** | Código tenta escrever em `../../`, `~/.ssh/` ou no registro do Windows. | Resolução canônica de caminhos com `Path.resolve()` e bloqueio estrito contra qualquer caminho fora da raiz do workspace. |
| **Vazamento de Credenciais** | Script do desafio executa `env` ou lê variáveis de ambiente herdadas (`OPENAI_API_KEY`, tokens Git). | Higienização de `env`: apenas variáveis mínimas necessárias para runtime são repassadas (`PATH` básico, `SYSTEMROOT`). |
| **Injeção de Instruções (Prompt Injection)** | README ou comentário no código contém instruções para quebrar o benchmark ou desligar a avaliação. | Tratar todo texto do repositório como dado passivo; isolar a engine de avaliação fora do alcance do agente. |
| **Denial of Service (DoS)** | Processo entra em fork-bomb, aloca 100% da RAM ou loop infinito de CPU. | Limites rígidos de CPU/RAM e árvore de processos monitorada com término forçado (`tree-kill`). |

---

## Procedimento de Auditoria de Segurança

### 1. Auditoria de Subprocessos e Execução de Comandos
1. Inspecione todas as chamadas de subprocesso no código:
   - **PROIBIDO:** `shell=True` com strings concatenadas.
   - **OBRIGATÓRIO:** Comandos passados como lista imutável de strings:
     ```python
     # SEGURO
     subprocess.run(["python", "-m", "pytest", target], timeout=limits.timeout_seconds, shell=False)
     ```
2. Todo processo disparado deve ter:
   - `timeout` definido e obrigatório (máximo 600 segundos).
   - Gerenciamento de processos filhos: em caso de timeout, todos os processos descendentes devem ser mortos (no Windows via `taskkill /F /T /PID`, no Linux via `os.killpg(os.getpgid(p.pid), signal.SIGKILL)`).

### 2. Validação Rigorosa de Caminhos (Anti-Path Traversal)
Sempre que o PatchTime manipular caminhos informados por manifestos ou gerados por agentes:
```python
def assert_path_is_safe(target_path: Path, workspace_root: Path) -> Path:
    resolved_target = target_path.resolve()
    resolved_root = workspace_root.resolve()
    try:
        resolved_target.relative_to(resolved_root)
    except ValueError:
        raise SecurityViolationError(
            f"Tentativa de escape detectada! O caminho '{resolved_target}' está fora do workspace '{resolved_root}'."
        )
    return resolved_target
```
- Bloqueie links simbólicos (symlinks) cujo destino aponte para fora do workspace.

### 3. Higienização do Ambiente de Execução (Env Scrubbing)
Ao disparar processos do desafio ou do agente:
1. Crie um dicionário de ambiente limpo:
   ```python
   SAFE_ENV = {
       "PATH": os.environ.get("PATH", ""),
       "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),  # Necessário no Windows
       "TEMP": str(workspace_temp_dir),
       "TMP": str(workspace_temp_dir),
       "PYTHONPATH": str(workspace_dir / "src"),
   }
   ```
2. Assegure que chaves como `*_API_KEY`, `GITHUB_TOKEN`, `AWS_*`, `SSH_*` **nunca sejam herdadas**.

### 4. Política de Rede (Network Egress)
- Durante a execução da tentativa do agente e durante a execução dos testes de avaliação, a rede deve estar **desabilitada por padrão** (em contêineres: `--network none`).
- Se o download de pacotes for imprescindível na etapa de preparação, ele deve ocorrer em etapa isolada prévia, com validação de hashes.

---

## Regras de Decisão
- Se o ambiente do host não possuir Docker e for exigido modo conteinerizado: **não finja isolamento**. Declare formalmente que o sistema operará em modo de fallback local com limitações conhecidas.
- Se for detectada tentativa intencional de path traversal ou symlink suspeito: aborte a execução imediatamente com veredito `SECURITY_VIOLATION`.

## Verificação
1. Teste de escape: tentativas de criar arquivos fora do workspace geram `SecurityViolationError`.
2. Teste de timeout: processos em loop infinito encerram precisamente ao atingir o tempo configurado.
3. Teste de vazamento: comando `printenv` executado pelo participante não retorna chaves de API do host.

## Saídas Esperadas
- Relatório de conformidade de segurança (`security_audit.json`).
- Ambiente temporário descartável limpo após o término da sessão.

## Integração com outras skills
- Valida os workspaces gerados por: **`patchtime-snapshot-reconstruction`**.
- Garante o isolamento dos executores em: **`patchtime-agent-adapter`**.
- Protege o harness de teste em: **`patchtime-evaluation-integrity`**.

