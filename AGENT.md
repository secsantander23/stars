# AGENT.md — Manual Operacional do Desenvolvedor de IA: PatchTime

> **Documento Normativo e Operacional do Projeto PatchTime**  
> **Versão do Manual:** 1.0.0  
> **Escopo:** Guia de engenharia, arquitetura, segurança, reprodutibilidade e governança de código para agentes autônomos e desenvolvedores de IA atuando neste repositório.

---

## 1. Contexto e Diagnóstico Inicial do Repositório

### 1.1. Estado Atual da Base de Código
- **Workspace:** `c:\Users\IADados\Downloads\trending-git`
- **Controle de Versão:** Repositório Git inicializado (`branch: main`), sem commits prévios ou arquivos de código legados.
- **Ambiente de Runtime Detectado no Host:**
  - **Python:** `3.14.x` (com `pip 26.x`)
  - **Git:** `2.56.x`
  - **Node.js:** `v24.21.x`
  - **Docker:** Não detectado no PATH da máquina hospedeira.
- **Decisão Arquitetural Fundamental:**  
  Como o repositório é novo e limpo, a pilha tecnológica escolhida para o PatchTime é **Python 3.12+**. Essa escolha se justifica pela maturidade de suas bibliotecas para análise de Git (`GitPython`/`pygit2` ou invocações seguras do CLI Git), validação de esquemas tipados (`pydantic` ou `dataclasses`), suporte nativo a subprocessos assíncronos e ampla interoperabilidade com benchmarks de IA.  
  Dado que Docker pode não estar disponível em todos os ambientes hospedeiros (incluindo o host atual), a arquitetura deve fornecer **múltiplas camadas de isolamento**: uma camada nativa baseada em workspaces temporários descartáveis com subprocessos restritos, e uma camada conteinerizada (Docker/OCI) acionada quando o daemon estiver presente.

### 1.2. Layout de Diretórios Padronizado do Projeto
O agente de desenvolvimento deve estruturar o repositório seguindo rigorosamente a seguinte organização:

```
trending-git/
├── AGENT.md                       # Este manual de operações
├── README.md                      # Documentação de entrada e guia rápido do usuário
├── CONTRIBUTING.md                # Diretrizes de contribuição open source
├── SECURITY.md                    # Política de segurança e reporte responsável de falhas
├── pyproject.toml                 # Definição do pacote, dependências e ferramentas de build
├── src/
│   └── patchtime/
│       ├── __init__.py            # Inicialização e versão do pacote
│       ├── cli/                   # Interface de linha de comando (Click ou Typer/Argparse)
│       │   ├── __init__.py
│       │   ├── main.py            # Ponto de entrada do CLI
│       │   └── commands/          # Subcomandos (doctor, repo, challenge, benchmark, results)
│       ├── core/                  # Entidades centrais, modelos de dados e exceções
│       │   ├── __init__.py
│       │   ├── models.py          # Modelos de dados (Challenge, Run, Result, AgentConfig)
│       │   └── exceptions.py      # Hierarquia formal de exceções do PatchTime
│       ├── analyzer/              # Repository Analyzer: mineração de histórico e candidatos
│       │   ├── __init__.py
│       │   ├── git_miner.py       # Inspeção de commits, logs e heurísticas de diff
│       │   └── candidate.py       # Geração e pontuação de confiança de candidatos
│       ├── challenge/             # Challenge Builder e Snapshot Manager
│       │   ├── __init__.py
│       │   ├── builder.py         # Construção do pacote de desafio e sanitização
│       │   ├── snapshot.py        # Reconstrução do estado pré-fix e remoção de vazamento
│       │   └── validator.py       # Validação estrita do manifesto do desafio
│       ├── environment/           # Environment Builder & Sandboxing
│       │   ├── __init__.py
│       │   ├── base.py            # Interface abstrata de isolamento
│       │   ├── local_process.py   # Isolamento local (chroot/tempdir/restrições de env)
│       │   └── container.py       # Isolamento OCI/Docker (quando disponível)
│       ├── runner/                # Agent Runner & Adaptadores
│       │   ├── __init__.py
│       │   ├── base.py            # Contrato padronizado de adaptador de agente
│       │   └── adapters/          # Adaptadores concretos (mock, cli, custom)
│       ├── evaluation/            # Evaluation Engine
│       │   ├── __init__.py
│       │   ├── evaluator.py       # Execução independente de testes e aferição de comportamento
│       │   └── diff_inspector.py  # Análise de integridade de arquivos e alterações
│       └── benchmark/             # Benchmark Engine & Reporting
│           ├── __init__.py
│           ├── orchestrator.py    # Orquestrador de baterias de testes e matrizes de agentes
│           ├── storage.py         # Persistência local reproduzível (.patchtime/runs)
│           └── reporter.py        # Geração de saídas legíveis e exportação JSON
├── tests/
│   ├── unit/                      # Testes unitários (parsers, schemas, calculadoras)
│   ├── integration/               # Testes de integração (snapshots, sandboxes, runners)
│   ├── e2e/                       # Cenários ponta a ponta com repositórios sintéticos
│   ├── security/                  # Testes de escape de path, injeção e sanitização de segredos
│   └── fixtures/                  # Repositórios mock e manifestos sintéticos controlados
└── docs/                          # Documentação arquitetural e especificações
    ├── challenge-spec-v1.md       # Especificação formal do manifesto de desafio
    └── agent-adapter-spec.md      # Especificação do contrato para novos agentes
```

---

## 2. Visão do Produto e Missão do PatchTime

### 2.1. O que é o PatchTime
O **PatchTime** é uma ferramenta open source de infraestrutura experimental voltada a transformar bugs históricos reais de projetos de software em desafios de programação rigorosamente reproduzíveis, seguros e isolados para avaliação de agentes de Inteligência Artificial.

A metodologia central do PatchTime reside em:
1. Identificar, através do histórico Git e evidências associadas, correções genuínas de bugs passados.
2. Reconstruir com exatidão matemática o snapshot do projeto imediatamente anterior à correção (commit base).
3. Encapsular o problema em um ambiente hermético, expurgando do alcance do agente qualquer menção, arquivo, log ou metadado que revele o patch de referência original.
4. Orquestrar a execução de um ou mais agentes autônomos de programação sobre o workspace sanitizado.
5. Avaliar o código gerado de forma autônoma e externa, executando testes de comportamento (visíveis e ocultos) para verificar se o bug foi de fato corrigido sem causar regressões.
6. Gerar relatórios auditáveis, registrando métricas exatas de resolução, tempos, recursos e falhas de infraestrutura.

### 2.2. Perguntas-Chave que o PatchTime Responde
- O agente resolve falhas lógicas reais ou apenas sintetiza padrões artificiais/de brinquedo?
- O agente introduz regressões não intencionais no código ao tentar solucionar o bug?
- Qual modelo ou harness apresenta maior consistência estatística diante de um conjunto fixo de desafios?
- Quanto tempo e quantas iterações de ferramentas cada agente demanda para convergir?
- O patch gerado resolve o problema comportamentalmente ou apenas se assemelha superficialmente ao patch do autor humano?
- Os resultados obtidos por uma equipe são fielmente reproduzíveis em outra máquina?

### 2.3. Princípios Metodológicos Inegociáveis
1. **Reprodutibilidade Estrita:** Nenhum benchmark tem validade se os commits, hashes, dependências e parâmetros de execução não forem explicitamente registrados e reexecutáveis.
2. **Imparcialidade Metodológica:** Condições idênticas de tempo, timeout, recursos computacionais e informações disponíveis devem ser garantidas a todos os agentes sob comparação.
3. **Hermetismo e Anti-Vazamento:** A solução original jamais pode vazar para o agente avaliado.
4. **Avaliação por Comportamento:** O critério de sucesso é a passagem em testes automatizados rigorosos, e nunca a similaridade textual pura com o diff original (soluções válidas e criativas podem diferir do patch humano).
5. **Segurança por Padrão:** Código de terceiros e patches gerados por modelos de IA são considerados **dados e binários não confiáveis**. Jamais execute código arbitrário sem isolamento.
6. **Honestidade Científica:** Nunca infira superioridade entre agentes sem significância estatística, nunca invente métricas e diferencie sempre *resultado medido* de *estimativa*.

---

## 3. Modelo Operacional do Agente Desenvolvedor

O agente de IA que desenvolve o PatchTime opera sob o papel de **Engenheiro de Sistemas e Arquiteto de Software Sênior**. Não é aceitável a geração cega de arquivos sem validação de coerência, nem a suposição leviana de que comandos ou testes tiveram êxito.

### 3.1. Os Três Estados Formais de Trabalho
Ao responder sobre qualquer tarefa, o agente deve categorizar o status estritamente em:
- **Concluído (`DONE`):** A implementação foi finalizada, os testes unitários/integrados pertinentes foram executados e passaram com êxito demonstrável nos logs.
- **Parcialmente Concluído (`PARTIAL`):** O código foi implementado, mas existem testes pendentes, ferramentas ausentes no host ou limitações conhecidas expressamente documentadas.
- **Bloqueado (`BLOCKED`):** Há um impedimento concreto de infraestrutura, permissão ou inconsistência arquitetural que requer intervenção externa antes do avanço.

### 3.2. Proibição de Falsificação e Alucinação de Evidências
- **PROIBIDO** declarar que um teste passou sem tê-lo executado via ferramenta de terminal.
- **PROIBIDO** gerar métricas fictícias de benchmark ou simulações simuladas como se fossem execuções reais.
- **PROIBIDO** supor que Docker, ferramentas CLI ou bibliotecas existem no sistema sem validar previamente seu funcionamento.

### 3.3. Ciclo Operacional de Desenvolvimento (Fases A a F)
Para toda e qualquer solicitação de implementação no PatchTime, o agente deve seguir o ciclo:
```
[A. Compreender] ──> [B. Planejar] ──> [C. Implementar] ──> [D. Verificar] ──> [E. Revisar] ──> [F. Relatar]
```

1. **Etapa A — Compreender:** Inspecionar os arquivos envolvidos, dependências, riscos de segurança e efeitos colaterais em contratos públicos existentes.
2. **Etapa B — Planejar:** Elaborar um plano enxuto com escopo definido, identificando testes a adicionar e formas de verificação.
3. **Etapa C — Implementar:** Escrever código idiomático, fortemente tipado, com documentação clara, tratamento explícito de exceções e separação de responsabilidades.
4. **Etapa D — Verificar:** Executar linters, checagens de tipo e testes automatizados. Analisar os logs reais de saída.
5. **Etapa E — Revisar:** Realizar auto-inspeção do diff: verificar vazamentos de arquivos sensíveis, caminhos absolutos acidentais e regressões.
6. **Etapa F — Relatar:** Emitir relatório sucinto com arquivos modificados, comandos executados com respectivos códigos de retorno, limitações remanescentes e próximos passos.

---

## 4. Arquitetura Lógica e Componentes do PatchTime

A arquitetura do PatchTime é estruturada em 8 subsistemas desacoplados, com fronteiras rígidas de responsabilidade:

```
┌────────────────────────────────────────────────────────────────────────┐
│                          PATCHTIME CLI ENGINE                          │
└───────┬───────────────────┬───────────────────┬──────────────────┬─────┘
        │                   │                   │                  │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐  ┌──────▼──────┐
│  Repository    │  │   Challenge    │  │   Historical   │  │ Environment │
│    Analyzer    │  │    Builder     │  │Snapshot Manager│  │   Builder   │
└────────────────┘  └───────┬────────┘  └────────────────┘  └──────┬──────┘
                            │                                      │
                    ┌───────▼──────────────────────────────────────▼──────┐
                    │               ORCHESTRATOR & RUNNER                 │
                    │   ┌─────────────────────┐  ┌────────────────────┐   │
                    │   │    Agent Runner     │  │ Evaluation Engine  │   │
                    │   │ (Isolated Adapter)  │  │ (Separate Harness) │   │
                    │   └─────────────────────┘  └────────────────────┘   │
                    └─────────────────────────┬───────────────────────────┘
                                              │
                                    ┌─────────▼────────┐
                                    │ Results, Storage │
                                    │   & Reporting    │
                                    └──────────────────┘
```

### 4.1. Repository Analyzer (`src/patchtime/analyzer/`)
- **Propósito:** Examinar repositórios Git reais e extrair candidatos a desafios baseados em bugs históricos.
- **Fontes de Evidência Auditadas:**
  - Padrões de commit messages (`fix`, `bug`, `closes #`, `resolves #`, etc.).
  - Presença de alterações simultâneas em arquivos de código de produção e arquivos de teste (`test_*.py`, `*_spec.js`, etc.).
  - Detecção de correções de regressões (commits que revertem ou corrigem alterações recentes).
  - Variação líquida de complexidade e tamanho de diff (desafios atômicos e concisos são preferíveis a grandes refatorações).
- **Classificação de Confiança de Candidatos:**
  - Todo candidato recebe uma pontuação (`confidence_score: 0.0 - 1.0`) e um conjunto de evidências estruturadas.
  - Commits com testes que falhavam antes da correção e passam após a correção recebem confiança máxima.
  - Commits sem testes modificados ou puramente cosméticos recebem pontuação baixa e exigem validação manual humana obrigatória.

### 4.2. Challenge Builder (`src/patchtime/challenge/builder.py`)
- **Propósito:** Transformar um candidato validado em um pacote de desafio padronizado, seguro e versionado.
- **Regra de Sigilo da Solução:**
  - O `Challenge Builder` divide as informações em dois escopos:
    1. **Manifesto Público do Desafio (`challenge.json`):** Descrição do problema extraída de issues/mensagens sanitizadas, ambiente necessário, scripts de preparação, testes visíveis permitidos ao agente.
    2. **Metadados Restritos de Avaliação (`eval_spec.json` ou cofre de testes):** Commit da solução humana, patch de referência, testes ocultos de verificação e asserções que comprovam a correção do bug.
  - O agente avaliado **nunca** tem acesso aos metadados restritos.

### 4.3. Historical Snapshot Manager (`src/patchtime/challenge/snapshot.py`)
- **Propósito:** Reconstruir o estado exato dos arquivos no commit base (anterior ao fix).
- **Regras Operacionais:**
  - Não exportar o diretório `.git` completo com histórico futuro acessível ao agente. O histórico futuro contém a resposta.
  - Estratégia de extração segura: `git archive` do commit base para um diretório limpo e isolado, ou criação de um novo repositório Git local efêmero contendo estritamente um único commit inicial anônimo (`"Initial challenge state"`), impossibilitando comandos como `git log` ou `git reflog` de alcançarem o patch original.
  - Registro imutável: o hash SHA do commit base e do commit de referência devem ser gravados nos metadados do PatchTime.

### 4.4. Environment Builder (`src/patchtime/environment/`)
- **Propósito:** Configurar o ambiente de execução com isolamento e reprodutibilidade.
- **Estratégia Multinível:**
  - **Nível 1 (Host com Docker/OCI):** Constrói contêiner com sistema de arquivos restrito, limites de CPU (`--cpus`), memória (`--memory`), sem privilégios de root (`--user 1000:1000`) e rede desligada durante a execução (`--network none`), exceto na etapa controlada de download de dependências (se estritamente necessária).
  - **Nível 2 (Fallback Local Sem Docker):** Criação de diretório temporário isolado (`tempfile.TemporaryDirectory`), variáveis de ambiente higienizadas (`PATH` controlado, sem repasse de chaves de API do usuário hospedeiro), e execução com subprocessos dotados de timeouts rígidos e destruição garantida de árvores de processos (`psutil` / `taskkill` no Windows).
- **Segredos:** Jamais injetar chaves privadas, credenciais do sistema hospedeiro ou variáveis como `GITHUB_TOKEN`, `OPENAI_API_KEY`, etc., no ambiente onde o agente avaliado executa código arbitrário do repositório.

### 4.5. Agent Runner (`src/patchtime/runner/`)
- **Propósito:** Executar a tentativa de resolução através de uma interface padronizada de adaptadores de agentes de IA.
- **Contrato Abstrato (`BaseAgentAdapter`):**
  - Todo adaptador deve implementar métodos explícitos:
    - `validate_environment() -> AdapterValidationResult` (verifica se os binários do agente estão presentes e configurados).
    - `run_attempt(workspace: Path, prompt: str, limits: ResourceLimits) -> AgentExecutionOutput`.
  - Tratamento de Falhas:
    - O PatchTime categoriza o encerramento em:
      - `SUCCESS_EXIT`: Agente encerrou declarando término dentro do tempo limite.
      - `AGENT_CRASH`: O processo do agente quebrou com código de saída diferente de zero.
      - `INFRA_TIMEOUT`: O agente excedeu o tempo máximo permitido (wall-clock timeout).
      - `INFRA_ERROR`: Falha de sistema de arquivos, permissão ou ambiente host (não imputada ao agente).
  - Isolamento de logs: `stdout` e `stderr` do processo do agente devem ser capturados em arquivos separados e sanitizados contra vazamento de strings sensíveis.

### 4.6. Evaluation Engine (`src/patchtime/evaluation/`)
- **Propósito:** Determinar de forma incontestável se o bug foi resolvido e se houve quebra de compatibilidade/regressões.
- **Princípio da Separação de Poderes:**
  - O processo de avaliação é disparado **fora do alcance** do agente participante.
  - Uma vez finalizada a tentativa do agente, o PatchTime injeta os testes de avaliação (armazenados em diretório protegido externo) no workspace ou em um container limpo com as alterações do agente e executa a suíte de testes.
- **Categorias de Testes na Avaliação:**
  1. **Testes de Regressão (Suite Base):** Garantem que o código original funcional não foi destruído. Devem passar no commit base e continuar passando após a alteração do agente.
  2. **Testes do Bug (Fail-to-Pass):** Testes que atestam a falha reportada. No commit base devem **falhar**; após a alteração do agente devem **passar**.
  3. **Testes Ocultos (Edge Cases adicionais):** Testes sintéticos adicionais para garantir que o modelo não realizou um "hardcode" simplório ou contorno frágil.
- **Veredito Comportamental:**
  - O resultado é calculado como:
    - `RESOLVED`: Todos os testes Fail-to-Pass passaram AND todos os testes Pass-to-Pass continuam passando.
    - `PARTIAL_FIX`: Parte dos testes do bug passaram, mas houve falhas residuais.
    - `REGRESSION`: O agente introduziu quebras em funcionalidades pré-existentes.
    - `FAILED`: O bug não foi resolvido.

### 4.7. Benchmark Engine (`src/patchtime/benchmark/`)
- **Propósito:** Orquestrar execuções em lote, repetições estatísticas e controle experimental.
- **Capacidades:**
  - Execução de matrizes: $N$ desafios $\times$ $M$ agentes $\times$ $K$ repetições.
  - Congelamento de versão: cada execução vincula o hash SHA da ferramenta PatchTime, a versão do esquema do desafio e a versão exata do binário do agente.
  - Repetição determinística: capacidade de reexecutar exatamente a mesma semente ou configuração de experimento para auditar discrepâncias.

### 4.8. Results and Reporting (`src/patchtime/benchmark/reporter.py`)
- **Propósito:** Apresentar dados científicos, objetivos e transparentes.
- **Métricas Registradas:**
  - Taxa de Resolução Global (`pass@1`, `pass@k`).
  - Total de testes aprovados/reprovados.
  - Tempo médio de execução por desafio.
  - Consumo de recursos (memória de pico, CPU time).
  - Taxa de timeout e taxa de falhas de infraestrutura.
  - Número de arquivos e linhas modificadas pelo agente.
- **Formatos de Exportação:**
  - Tabela formatada para terminal (Rich/Text).
  - Documento estruturado JSON auditável com esquema estrito para consumo programático.

---

## 5. Princípios de Justiça dos Benchmarks (Fairness)

Para evitar resultados enganosos ou benchmarks enviesados, o agente desenvolvedor do PatchTime deve incorporar as seguintes salvaguardas no código:

### 5.1. Prevenção Rígida contra Vazamento de Solução (Data Leakage)
1. **Sanitização de Mensagens de Commit e Issues:**
   - Textos de issues ou descrições de bugs não devem conter trechos como *"Fixed in commit abc1234"* ou snippets contendo a implementação exata do patch.
2. **Higienização do Sistema de Arquivos:**
   - Nenhuma pasta `.git` com commits posteriores ao commit base deve residir no workspace do agente.
   - Nenhum arquivo temporário como `patch.diff`, `reference.py` ou logs da análise histórica pode permanecer acessível.
3. **Imparcialidade contra Estilo de Código:**
   - A avaliação **não faz diff semântico** com o patch humano para atribuir pontuação de sucesso. Se o agente adotar uma abordagem alternativa válida que satisfaça todos os testes de comportamento e performance sem violar contratos, a solução é considerada correta.

### 5.2. Validade dos Critérios de Teste
- Um desafio **só é válido para benchmark** se for demonstrável que:
  $$\text{Resultado}(\text{Commit Base}, \text{Teste do Bug}) == \text{FAIL}$$
  $$\text{Resultado}(\text{Commit Humano de Referência}, \text{Teste do Bug}) == \text{PASS}$$
- Se o teste do bug passar no commit base, o desafio é considerado inconsistente (não reproduz o bug) e deve ser sumariamente descartado ou marcado como inválido pelo `patchtime challenge validate`.

---

## 6. Isolamento e Segurança

Como o PatchTime manipula repositórios de código aberto arbitrários e executa código gerado por modelos autônomos, as seguintes diretrizes são de cumprimento compulsório:

### 6.1. Proteção de Caminho e Sistema de Arquivos (Anti-Path Traversal)
- Todas as operações de leitura, escrita e extração de tarballs/zips de desafios devem passar por validação estrita de fronteiras (`Path.resolve()` verificado contra a raiz do workspace).
- Bloqueio imediato contra arquivos contendo `../`, symlinks que apontem para fora do workspace ou nomes reservados de sistema no Windows (`NUL`, `CON`, `PRN`, etc.).

### 6.2. Política de Subprocessos Seguros
- **Jamais** utilizar `shell=True` em chamadas `subprocess.Popen` ou `subprocess.run` ao lidar com parâmetros oriundos de repositórios, nomes de branches, comandos de manifesto ou entradas de usuário.
- Todos os comandos devem ser repassados como listas explícitas de argumentos (`["git", "checkout", "..."]`).
- Todo processo disparado deve possuir um `timeout` explicitamente definido (em segundos). Processos que estourarem o tempo devem sofrer encerramento em cascata (`tree kill`).

### 6.3. Tratamento de Instruções Não Confiáveis (Prompt Injection & Jailbreak Defense)
- READMEs, comentários de código, docstrings e textos de issues minerados de repositórios externos devem ser tratados como **dados textuais não confiáveis**, nunca como instruções de sistema para o PatchTime.
- O PatchTime não deve permitir que metadados em arquivos de repositório alterem configurações globais, desabilitem checagens de segurança ou façam bypass nas regras de isolamento.

---

## 7. Interface de Linha de Comando (CLI)

A CLI do PatchTime deve ser ergonômica, consistente, apresentar mensagens acionáveis e fornecer códigos de saída padronizados (0 para sucesso, 1 para falha lógica de comando, 2 para erro de sintaxe/argumento, 3 para falha de infraestrutura).

### 7.1. Especificação dos Comandos Centrais

```bash
# 1. Diagnóstico do ambiente e verificação de dependências
patchtime doctor

# 2. Análise de repositório Git em busca de candidatos a bugs históricos
patchtime repo inspect <path-or-url> [--min-confidence 0.7] [--max-candidates 10]

# 3. Gerenciamento e validação de desafios
patchtime challenge list [--dir ./challenges]
patchtime challenge validate <path-to-challenge>
patchtime challenge build --repo <repo> --base <commit> --fix <commit> --out <dir>

# 4. Execução de benchmarks
patchtime benchmark run --challenge <id-or-path> --agent <adapter-name> [--timeout 300] [--repeats 1]
patchtime benchmark compare <run-id-1> <run-id-2>

# 5. Visualização e exportação de resultados
patchtime results show <run-id>
patchtime results export <run-id> --format json [--output file.json]
```

### 7.2. Contrato do Comando `patchtime doctor`
O comando `patchtime doctor` deve obrigatoriamente checar e reportar:
1. Versão do Python e integridade das dependências internas.
2. Disponibilidade e versão do binário do Git.
3. Status do daemon Docker/OCI (se presente ou ausente, indicando o modo de isolamento ativo).
4. Permissões de escrita no diretório de trabalho e armazenamento local (`.patchtime/`).
5. Espaço disponível em disco para criação de workspaces efêmeros.
6. Adaptadores de agentes instalados e funcionais no host.

---

## 8. Formato e Especificação do Desafio (`challenge.v1.json`)

Todo desafio do PatchTime é representado por um manifesto formal versionado. O arquivo deve ser validado estritamente via esquema:

```json
{
  "$schema": "https://patchtime.dev/schemas/challenge.v1.json",
  "id": "py-requests-leak-4021",
  "schema_version": "1.0.0",
  "metadata": {
    "source_repo": "https://github.com/example/repo",
    "language": "python",
    "runtime_version": "3.12",
    "created_at": "2026-10-24T12:00:00Z",
    "difficulty": "medium",
    "provenance": {
      "base_commit": "a1b2c3d4e5f67890123456789012345678901234",
      "reference_commit_hash": "b2c3d4e5f678901234567890123456789012345a",
      "issue_reference": "https://github.com/example/repo/issues/4021"
    }
  },
  "problem_statement": {
    "title": "Memory leak upon connection retry failure",
    "description": "When an HTTP connection fails repeatedly under retry logic, session sockets remain unclosed leading to resource exhaustion. The session must cleanly close unestablished sockets on exceptions."
  },
  "environment": {
    "type": "python",
    "dependencies_file": "requirements-test.txt",
    "install_command": "pip install -r requirements-test.txt",
    "resource_limits": {
      "timeout_seconds": 300,
      "max_memory_mb": 2048,
      "max_cpu_cores": 2
    }
  },
  "evaluation": {
    "visible_tests": [
      "tests/test_basic_connection.py"
    ],
    "fail_to_pass_tests": [
      "tests/test_retry_leak.py::test_socket_cleanup_on_retry_fail"
    ],
    "pass_to_pass_tests": [
      "tests/test_session.py",
      "tests/test_adapters.py"
    ],
    "test_command": "pytest {test_target}"
  }
}
```

> **Atenção:** Em ambientes de execução para agentes, o manifesto público omite completamente a chave `reference_commit_hash` e qualquer menção a soluções ou patches.

---

## 9. Armazenamento e Reproduzibilidade

### 9.1. Arquitetura Local-First para o MVP
- O PatchTime adota arquitetura **Local-First**, sem dependência de banco de dados remoto ou serviços em nuvem pagos para sua operação fundamental.
- Raiz de armazenamento padrão: `.patchtime/` (localizada no diretório de trabalho do usuário ou no workspace atual).
- Estrutura de persistência:
  ```
  .patchtime/
  ├── config.json               # Configurações locais do PatchTime
  ├── challenges/               # Cache local de desafios extraídos
  │   └── <challenge-id>/
  │       ├── challenge.json
  │       ├── repo_snapshot.tar.gz
  │       └── eval_protected/   # Testes ocultos e metadados confidenciais
  └── runs/                     # Histórico auditável de execuções
      └── <run-id>/
          ├── run_meta.json     # Metadados do agente, versões, parâmetros, horários
          ├── result.json       # Veredito detalhado e métricas de teste
          ├── agent_stdout.log  # Saída padrão capturada do agente
          ├── agent_stderr.log  # Saída de erros capturada do agente
          └── patch_produced.diff # Diff final gerado pelo agente sobre o commit base
  ```

### 9.2. Sanitização de Logs e Artefatos
- Antes de persistir qualquer arquivo de log em `.patchtime/runs/`, o PatchTime deve passar os buffers por um filtro de higienização que substitui padrões de credenciais conhecidas (`Bearer [A-Za-z0-9_\-\.]+`, `ghp_[A-Za-z0-9]{36}`, chaves de API) por marcadores sanitizados (`[REDACTED_SECRET]`).

---

## 10. Estratégia de Testes do Próprio PatchTime

O PatchTime deve ser testado através de uma pirâmide de testes rigorosa:

### 10.1. Testes Unitários (`tests/unit/`)
- Validação de esquemas JSON de desafios (campos obrigatórios, tipos, versões de esquema).
- Sanitizadores de caminhos e verificadores de segurança de diretório.
- Parsers de commits Git, cálculo de diff e heurísticas de relevância.
- Formatadores de relatórios e normalizadores de saída do pytest.

### 10.2. Testes de Integração (`tests/integration/`)
- Extração de snapshot histórico a partir de repositório Git local sintético.
- Criação e limpeza de workspaces temporários de isolamento.
- Execução controlada de adaptadores mock com aferição precisa de timeout.
- Injeção e isolamento de testes na engine de avaliação.

### 10.3. Testes Ponta a Ponta (`tests/e2e/`)
- O repositório deve manter em `tests/fixtures/synthetic_repo/` um mini-projeto Python versionado via script.
- O cenário E2E deve:
  1. Construir o desafio sintético.
  2. Executar um agente "mock perfeito" (que aplica a correção esperada) $\rightarrow$ Verificar veredito `RESOLVED`.
  3. Executar um agente "mock defeituoso" (que quebra testes existentes) $\rightarrow$ Verificar veredito `REGRESSION`.
  4. Executar um agente "mock inerte" (que não faz nada) $\rightarrow$ Verificar veredito `FAILED`.
  5. Executar um agente "mock travado" (em loop infinito) $\rightarrow$ Verificar status `INFRA_TIMEOUT`.
  6. Validar a geração e o esquema do arquivo `result.json`.

---

## 11. Roteiro de Implementação Incremental (Fases 1 a 7)

O desenvolvimento do PatchTime pelo agente de IA deve seguir estritamente as fases abaixo. Nenhuma fase posterior deve ser iniciada antes que a anterior esteja estável, testada e funcional:

| Fase | Foco Principal | Entregáveis Essenciais |
| :--- | :--- | :--- |
| **Fase 1** | **Fundação & Estrutura Base** | `pyproject.toml`, hierarquia de pacotes `src/patchtime/`, modelo de erros `exceptions.py`, comando `patchtime doctor`, testes unitários base. |
| **Fase 2** | **Desafio Mínimo Reproduzível** | Especificação do manifesto `challenge.v1.json`, módulo `validator.py`, mecanismo de snapshot `snapshot.py`, fixture sintética para testes. |
| **Fase 3** | **Agent Runner & Isolamento** | Interface `BaseAgentAdapter`, executor de subprocesso com sandbox de diretório temporário, controle de tempo limite, adaptador mock. |
| **Fase 4** | **Engine de Avaliação Independente** | Executor de testes isolado (`evaluator.py`), separação de testes visíveis/ocultos, classificação do veredito (`RESOLVED`, `FAILED`, `REGRESSION`). |
| **Fase 5** | **Benchmark & Reprodutibilidade** | Persistência local em `.patchtime/runs/`, orquestrador de múltiplos desafios, exportação em JSON e apresentação formatada na CLI. |
| **Fase 6** | **Análise Histórica de Repositórios Reais** | Minerador de histórico Git (`git_miner.py`), pontuação de candidatos a bug e automação da montagem de desafios. |
| **Fase 7** | **Expansão de Ecossistema** | Suporte a conteinerização Docker completa, adaptadores adicionais para agentes conhecidos do ecossistema, interface visual avançada. |

---

## 12. Padrões de Código e Princípios de Engenharia

Ao implementar código no PatchTime, o agente deve seguir sem desvios as seguintes regras:

1. **Tipagem Estrita:** Todo o código Python deve usar type annotations abrangentes (`typing` / `types`). Nenhuma função deve ser criada sem tipos definidos em argumentos e retorno.
2. **Manipulação Segura de Arquivos:** Utilizar exclusivamente `pathlib.Path` para operações de sistema de arquivos. Nunca concatenar caminhos via strings simples.
3. **Tratamento Específico de Erros:** Proibido o uso de `except Exception: pass` ou captura genérica sem tratamento ou re-lançamento da exceção encapsulada na hierarquia de `PatchTimeException`.
4. **Sem Dependências Desnecessárias:** Preferir bibliotecas consagradas da biblioteca padrão do Python (`pathlib`, `subprocess`, `dataclasses`, `json`, `argparse`/`sys`). Dependências externas devem ser estritamente justificadas em `pyproject.toml`.
5. **Idempotência:** Scripts de preparação, limpeza e avaliação devem ser idempotentes; reexecutar uma operação não deve corromper o estado do sistema.

---

## 13. O que o Agente NUNCA Deve Fazer (Anti-Padrões Proibidos)

1. **NÃO implementar módulos fictícios** ou mocks falsos apenas para fingir completude visual sem código funcional por trás.
2. **NÃO expor o patch de referência ou o histórico futuro do Git** ao agente avaliado sob hipótese alguma.
3. **NÃO executar código desconhecido diretamente na raiz da máquina hospedeira** sem encapsulamento em diretório temporário descartável ou contêiner.
4. **NÃO assumir que ferramentas externas (como Docker) estão instaladas** sem prévia checagem via código.
5. **NÃO utilizar similaridade de diff textual** como régua primária para aferir se um bug foi solucionado.
6. **NÃO alterar configurações globais do sistema operacional**, arquivos pessoais do usuário ou variáveis fora do diretório do projeto.
7. **NÃO efetuar commits, criação de tags ou publicações em repositórios remotos** sem instrução expressa e inequívoca do usuário.
8. **NÃO omitir ou suprimir mensagens de erro reais** de testes ou ferramentas em relatórios.
9. **NÃO misturar configurações incompatíveis** de benchmarks em relatórios comparativos.
10. **NÃO criar abstrações prematuras** e dezenas de camadas indiretas antes que o fluxo básico do MVP esteja funcionando e testado.

---

## 14. Guia Rápido de Ação para o Agente em Cada Turno

Ao ser acionado pelo usuário para implementar ou modificar funcionalidades no PatchTime:
1. **Consulte este `AGENT.md`** para garantir alinhamento com a arquitetura e com a fase vigente do projeto.
2. **Analise o estado do código:** execute os testes unitários existentes antes de iniciar qualquer nova alteração.
3. **Implemente de forma incremental:** faça pequenas alterações coesas, respeitando as fronteiras de cada módulo.
4. **Escreva testes concomitantes:** qualquer nova funcionalidade ou correção de bug deve vir acompanhada do seu respectivo teste automatizado.
5. **Execute a validação:** rode os testes via terminal e observe atentamente a saída real.
6. **Relate com precisão:** apresente arquivos alterados, resultados observados dos testes e o estado atual da entrega (`DONE`, `PARTIAL` ou `BLOCKED`).

