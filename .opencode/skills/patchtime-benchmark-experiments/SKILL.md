---
name: patchtime-benchmark-experiments
description: Orquestrar, reproduzir e contrastar baterias de benchmark entre múltiplos modelos e agentes de programação no PatchTime. Ative ao implementar suítes de experimentos, persistir relatórios de execução, calcular métricas pass@k ou auditar comparativos de desempenho.
---

# PatchTime Benchmark Experiments — Procedimento Operacional

## Identidade
Esta skill orienta o planejamento, a orquestração e a análise científica de experimentos no PatchTime. Ela estabelece regras de rigor estatístico e persistência auditável para que avaliações envolvendo múltiplos agentes (Claude, ChatGPT, Grok, Kiro, OpenCode) sejam plenamente reproduzíveis por terceiros e reflitam o desempenho real sem viés ou extrapolações indevidas.

## Quando utilizar
- Ao implementar ou executar comandos de benchmark (`patchtime benchmark run`, `patchtime benchmark compare`).
- Ao orquestrar matrizes de execução: $N$ desafios $\times$ $M$ agentes $\times$ $K$ repetições.
- Ao salvar metadados de execução em `.patchtime/runs/<run_id>/`.
- Ao calcular métricas consolidadas (*pass@1*, *pass@k*, taxa de timeout, estabilidade de regressão).
- Ao exportar relatórios comparativos estruturados em JSON para publicação científica ou painéis de resultados.

## Quando não utilizar
- Para inspecionar código de repositórios em busca de novos bugs (utilize `patchtime-repo-forensics`).
- Para executar a avaliação isolada de um teste específico (utilize `patchtime-evaluation-integrity`).
- Para implementar o conector de um agente externo (utilize `patchtime-agent-adapter`).

## Pré-requisitos
- Desafios validados no formato `challenge.v1.json`.
- Adaptadores de agentes com `validate_environment()` aprovado.
- Sistema de armazenamento local em `.patchtime/` inicializado.

---

## Procedimento de Execução e Orquestração

### 1. Definição Explícita da Configuração Experimental
Antes de disparar qualquer bateria de testes, o orquestrador deve registrar a configuração imutável do experimento:
- `experiment_id`: UUID único ou timestamp estruturado.
- `patchtime_version`: Versão exata do PatchTime (ex.: `0.1.0`).
- `agent_registry_info`: Nome e versão exata do binário ou modelo do agente (ex.: `claude-code@0.2.29`, `o3-mini@2025-01-31`).
- `resource_limits`: Timeout, RAM e CPU idênticos para todos os agentes sob comparação.
- `trials_per_challenge`: Quantidade de repetições ($k$) para cada par (desafio, agente).

### 2. Ciclo de Execução Hermético por Tentativa
Para cada iteração da matriz experimental:
1. Gere um identificador estável de execução (`run_id`).
2. Recupere o snapshot limpo do commit base.
3. Acione o agente via `BaseAgentAdapter.run_attempt()`.
4. Capture os logs e o patch resultante.
5. Execute a avaliação independente via `EvaluationEngine`.
6. Persista imediatamente o diretório `.patchtime/runs/<run_id>/` com:
   - `run_meta.json` (parâmetros, horários, versões)
   - `result.json` (veredito dos testes e métricas)
   - `agent_stdout.log` e `agent_stderr.log` (higienizados de credenciais)
   - `patch_produced.diff` (código gerado)

### 3. Cálculo de Métricas Sem Alucinação
As métricas agregadas devem ser calculadas de forma determinística:

$$\text{Taxa de Resolução (pass@1)} = \frac{\text{Total de Desafios com Veredito RESOLVED}}{\text{Total de Desafios Avaliados}}$$

$$\text{Taxa de Regressão} = \frac{\text{Total de Desafios com Veredito REGRESSION}}{\text{Total de Desafios Avaliados}}$$

$$\text{Taxa de Timeout} = \frac{\text{Total de Tentativas com INFRA\_TIMEOUT}}{\text{Total de Tentativas}}$$

- **REGRA DE RIGOR CIENTÍFICO:** Se um agente falhou devido a `INFRA_ERROR` (ex.: falha de rede do host ou disco cheio), a execução **NÃO** deve ser contabilizada como solução incorreta. Deve ser marcada como falha de infraestrutura e reexecutada.
- **Custos e Tokens:** Registre custos ou contagem de tokens **apenas** quando o provedor da API ou a ferramenta CLI fornecerem esses dados de forma mensurável no log. **Nunca invente ou estime custos fictícios**.

### 4. Protocolo de Comparação Justa entre Agentes
Ao executar `patchtime benchmark compare run_A run_B`:
- Verifique se ambos os runs utilizaram **a mesma versão do desafio** e **os mesmos limites de tempo**.
- Se os ambientes foram diferentes (ex.: um rodou local e outro conteinerizado), a discrepância deve ser destacada como ressalva metodológica no cabeçalho do relatório.
- Se o tamanho da amostra for pequeno ($N < 30$), o relatório deve incluir expressamente a nota:
  > *"Aviso: Amostra reduzida (N=X). Os resultados refletem tendências preliminares e não possuem significância estatística conclusiva para generalização."*

---

## Regras de Decisão
- Nunca omita execuções que falharam. Todo experimento deve ter 100% de suas execuções registradas.
- Se o usuário solicitar interrupção prematura (Ctrl+C), o orquestrador deve finalizar com segurança os processos filhos ativos e registrar o status `ABORTED_BY_USER`.

## Segurança
- Não persista tokens de autenticação ou chaves de API nos arquivos `run_meta.json`.
- Higienize logs capturados antes de gravar em disco (`[REDACTED_SECRET]`).

## Verificação
1. O diretório `.patchtime/runs/<run_id>/` contém todos os artefatos obrigatórios.
2. O arquivo exportado por `patchtime results export <run_id> --format json` valida contra o schema.
3. A reexecução de um desafio com semente determinística produz o mesmo snapshot.

## Saídas Esperadas
- Relatório consolidado de benchmark (`benchmark_summary.json`).
- Tabela legível em terminal exibindo a comparação entre agentes.

## Integração com outras skills
- Recebe desafios estruturados de: **`patchtime-challenge-authoring`**.
- Coordena adaptadores implementados com: **`patchtime-agent-adapter`**.
- Coleta vereditos da skill: **`patchtime-evaluation-integrity`**.

