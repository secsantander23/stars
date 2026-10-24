---
name: patchtime-agent-adapter
description: Desenvolver, testar e manter adaptadores de execução padronizados para integrar agentes de IA (Claude, ChatGPT, Grok, Kiro, OpenCode, Aider, etc.) ao PatchTime. Ative ao implementar novos runners, auditar contratos de ferramentas externas, capturar métricas de execução ou tratar falhas de subprocessos de agentes.
---

# PatchTime Agent Adapter — Procedimento Operacional

## Identidade
Esta skill orienta a concepção, implementação e teste de adaptadores padronizados no PatchTime. Sua responsabilidade é criar pontes seguras, previsíveis e herméticas entre a infraestrutura do PatchTime e os diversos agentes autônomos de programação (proprietários e open source), garantindo tratamento uniforme de timeouts, isolamento de processos e captura auditável de saída.

## Quando utilizar
- Ao criar ou revisar adaptadores em `src/patchtime/runner/adapters/`.
- Ao estender a interface abstrata `BaseAgentAdapter` para novas ferramentas (Claude Code CLI, OpenAI Function Calling, xAI Grok, Aider, OpenHands).
- Ao implementar validação de pré-requisitos (`validate_environment`) para checar se ferramentas externas ou credenciais de IA estão configuradas antes do benchmark.
- Ao tratar a captura de `stdout`, `stderr`, consumo de tokens e códigos de retorno dos executores de agentes.

## Quando não utilizar
- Para configurar regras de sandbox de sistema de arquivos e SO (utilize `patchtime-sandbox-security`).
- Para executar os testes comportamentais que julgam a solução (utilize `patchtime-evaluation-integrity`).
- Para orquestrar tabelas comparativas entre múltiplos agentes (utilize `patchtime-benchmark-experiments`).

## Pré-requisitos
- Contrato base `BaseAgentAdapter` em `src/patchtime/runner/base.py`.
- Modelos de dados em `src/patchtime/core/models.py` (`ResourceLimits`, `ProblemStatement`).
- Documentação oficial da CLI ou API da ferramenta externa a ser integrada (não adivinhe parâmetros nem flags).

---

## O Contrato Padronizado de um Adaptador

Todo adaptador deve implementar estritamente a interface definida em `templates/adapter_contract_template.py`:

```python
class BaseAgentAdapter(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Identificador único do adaptador (ex: 'claude-code', 'chatgpt-o3', 'aider')."""
        pass

    @abstractmethod
    def validate_environment(self) -> AdapterValidationResult:
        """Verifica se binários, chaves e dependências estão prontos antes de iniciar."""
        pass

    @abstractmethod
    def run_attempt(
        self,
        workspace_dir: Path,
        problem: ProblemStatement,
        limits: ResourceLimits,
    ) -> AgentExecutionOutput:
        """Executa a tentativa do agente dentro do workspace higienizado."""
        pass
```

---

## Procedimento de Implementação de um Novo Adaptador

### 1. Pesquisa e Validação dos Parâmetros Oficiais da Ferramenta
1. Consulte a documentação oficial da ferramenta ou execute localmente `--help` para confirmar:
   - Sinalizador para execução não-interativa / headless (ex.: `claude -p`, `aider --yes --no-git`).
   - Mecanismo para limitar iterações ou orçamento de tokens.
   - Formato dos logs gerados.
2. **PROIBIÇÃO:** Não invente flags fictícias ou formatos JSON imaginários.

### 2. Higienização e Construção dos Argumentos
1. Execute a ferramenta passando argumentos como lista explícita de strings:
   ```python
   cmd = [self.binary_path, "--headless", "--prompt", problem.description]
   ```
2. Defina o diretório de trabalho estritamente como a raiz do workspace descartável (`cwd=str(workspace_dir)`).
3. Repasse apenas variáveis de ambiente seguras. **Nunca** injete chaves de API desnecessárias no subprocesso se ele executar código de terceiros.

### 3. Gerenciamento de Ciclo de Vida e Timeout
1. Monitore a execução do subprocesso com `limits.timeout_seconds`.
2. Em caso de estouro de tempo:
   - Mate a árvore de processos do agente imediatamente.
   - Registre o status explícito: `INFRA_TIMEOUT`.
3. Capture separadamente:
   - `stdout` em `agent_stdout.log`
   - `stderr` em `agent_stderr.log`

### 4. Categorização Rigorosa do Desfecho da Execução
O adaptador deve categorizar o encerramento do processo em 4 estados distintos:
- **`SUCCESS_EXIT`:** O processo do agente encerrou normalmente (exit code 0) dentro do tempo limite.
- **`AGENT_CRASH`:** O processo encerrou com erro (exit code != 0, out of memory, crash interno da ferramenta).
- **`INFRA_TIMEOUT`:** O agente excedeu o tempo máximo configurado.
- **`INFRA_ERROR`:** Falha de ambiente, disco cheio ou permissão negada no host (não imputável ao agente).

### 5. Extração do Diff Gerado
Ao final da execução, o adaptador deve inspecionar as alterações introduzidas pelo agente no workspace:
```bash
git diff HEAD > patch_produced.diff
```
Se nenhum arquivo tiver sido modificado, registre `no_changes_detected: true`.

---

## Regras de Decisão
- Se a ferramenta externa não estiver instalada na máquina hospedeira: o método `validate_environment()` deve retornar `status=UNAVAILABLE` com mensagem clara indicando o comando de instalação. Não quebre com exceção inesperada.
- Se a ferramenta externa solicitar confirmações interativas que bloqueiem a execução: configure obrigatoriamente a flag de auto-confirmação (ex: `--yes`, `--non-interactive`) ou rejeite o adaptador se este não suportar modo headless.
- Jamais crie um adaptador mock que retorne sucesso artificial para simular funcionamento. Adaptadores mock devem existir exclusivamente na suíte de testes (`tests/`).

## Verificação
1. Teste de validação: o comando `patchtime agent test <adapter-name>` reporta disponibilidade correta.
2. Teste de timeout simulado: adaptador responde corretamente quando o comando externo trava.
3. Teste de sanitização de saída: senhas e tokens não aparecem nos logs persistidos.

## Saídas Esperadas
Objeto `AgentExecutionOutput` contendo:
- `adapter_name`
- `status` (`SUCCESS_EXIT`, `AGENT_CRASH`, `INFRA_TIMEOUT`, `INFRA_ERROR`)
- `execution_time_seconds`
- `exit_code`
- `stdout_path`
- `stderr_path`
- `patch_path`
- `tokens_used` (se reportado pelo provedor)

## Integração com outras skills
- Recebe limites e políticas de: **`patchtime-sandbox-security`**.
- Entrega o workspace alterado para avaliação em: **`patchtime-evaluation-integrity`**.
- Fornece métricas de tempo e recursos para: **`patchtime-benchmark-experiments`**.

