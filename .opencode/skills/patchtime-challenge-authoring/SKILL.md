---
name: patchtime-challenge-authoring
description: Transformar candidatos a bugs investigados em desafios formais, reproduzíveis e versionados do PatchTime. Ative ao criar manifestos challenge.v1.json, redigir enunciados neutros, configurar comandos de ambiente ou validar a integridade de um pacote de desafio.
---

# PatchTime Challenge Authoring — Procedimento Operacional

## Identidade
Esta skill orienta a transformação de um candidato a bug histórico (qualificado pela perícia forense) em um desafio padronizado, seguro e versionado pelo PatchTime. Ela estabelece a redação do manifesto público, a redação do enunciado descritivo sem vazamento da resposta, o empacotamento dos critérios de execução e a segregação de artefatos protegidos de avaliação.

## Quando utilizar
- Ao implementar ou executar comandos de criação e validação de desafios (`patchtime challenge build`, `patchtime challenge validate`).
- Ao estruturar novos manifestos no formato `challenge.v1.json`.
- Ao elaborar o enunciado do problema (`problem_statement`), assegurando clareza analítica sem dar dicas sobre a solução humana.
- Ao separar o que é dado público para o agente participante do que são metadados confidenciais de avaliação.

## Quando não utilizar
- Para minerar ou filtrar commits em repositórios brutos (utilize `patchtime-repo-forensics`).
- Para gerar snapshots físicos de arquivos no sistema de arquivos (utilize `patchtime-snapshot-reconstruction`).
- Para auditar a robustez de isolamento do sandbox (utilize `patchtime-sandbox-security`).
- Para aferir matematicamente os resultados de aprovação em testes (utilize `patchtime-evaluation-integrity`).

## Pré-requisitos
- Relatório pericial aprovado gerado pela skill `patchtime-repo-forensics`.
- Commit base (`base_commit`) e commit de referência (`reference_commit_hash`) plenamente identificados.
- Especificação de esquema JSON em `references/challenge.schema.json`.

## Ciclo de Vida de um Desafio
Todo desafio transita obrigatoriamente por 3 estados:
1. **Candidate:** Bug identificado, mas cujos testes e ambiente ainda não foram executados localmente para confirmação.
2. **Validated Challenge:** Desafio cujo ambiente foi testado com êxito: o teste do bug falha no commit base e passa com a solução de referência, sem quebrar testes existentes.
3. **Published Challenge:** Desafio congelado, com hashes imutáveis, pronto para integração em suítes públicas de benchmark.

---

## Procedimento de Autoria

### 1. Elaboração do Enunciado do Problema (Problem Statement)
O enunciado deve permitir ao agente de programação compreender a falha funcional como faria um engenheiro de software lendo uma issue real de produção.
- **Título (`title`):** Resumo conciso da falha (ex.: *"Socket resource leak on connection retry timeout"*).
- **Descrição (`description`):**
  - Descreva as condições de contorno, entradas problemáticas e saídas incorretas.
  - Inclua trechos de traceback ou mensagens de erro observadas no commit base, se disponíveis.
  - **PROIBIÇÃO DE VAZAMENTO:** Nunca mencione os nomes de arquivos exatos e números de linhas que devem ser alterados caso isso não fizesse parte da issue original. Jamais descreva a lógica do patch humano (ex.: *"Adicione um bloco try/finally na linha 42 do arquivo socket.py"*).

### 2. Configuração do Ambiente e Requisitos
Defina com rigor de versões:
- `language`: ex.: `"python"`.
- `runtime_version`: ex.: `"3.12"`.
- `install_command`: comando determinístico de preparação (ex.: `"pip install -r requirements-test.txt"`).
- `resource_limits`:
  - `timeout_seconds`: padrão 300 segundos.
  - `max_memory_mb`: padrão 2048 MB.
  - `max_cpu_cores`: padrão 2 núcleos.

### 3. Separação de Testes Visíveis e Ocultos
Configure a seção `evaluation`:
- `visible_tests`: Testes unitários pré-existentes que o participante pode inspecionar e rodar livremente para checar se quebrou algo.
- `fail_to_pass_tests`: Testes específicos do bug que **devem falhar no commit base** e **passar após a correção**. No manifesto público, são mantidos em segredo até o término da tentativa do agente.
- `pass_to_pass_tests`: Testes de regressão do projeto que devem continuar passando.
- `test_command`: comando padrão de execução de teste (ex.: `"pytest {test_target}"`).

### 4. Geração do Manifesto Público vs Metadados Restritos
Ao exportar o desafio:
1. Gere o manifesto público `challenge.json` **omitindo explicitamente**:
   - `reference_commit_hash`
   - Testes de avaliação ocultos
   - O diff da solução original
2. Armazene os dados de referência restritos em `eval_protected/reference_spec.json`, fora do diretório de workspace onde o participante trabalhará.

### 5. Validação com o Modelo do PatchTime
Verifique a conformidade instanciando e validando contra os modelos de dados em `src/patchtime/core/models.py` (`ChallengeManifest`, `ChallengeMetadata`, `ProblemStatement`).

---

## Regras de Decisão
- Se a reprodução do bug exigir serviços pagos, chaves de API externas ou banco de dados legado indisponível: **rejeite o desafio** ou encapsule um mock local determinístico.
- Se o teste histórico não for reprodutível no commit base (ou seja, passar antes mesmo do fix): o desafio é **INVÁLIDO**. Retorne à fase forense.

## Segurança
- O manifesto público não deve conter variáveis de ambiente secretas, tokens de autenticação ou caminhos absolutos do host.
- Valide que o `id` do desafio contenha apenas caracteres seguros (`[a-z0-9_-]`), evitando caracteres de controle ou separadores de caminho (`/`, `\`).

## Verificação
Execute a validação estática do arquivo gerado:
1. Sintaxe JSON válida.
2. Cumprimento do schema `references/challenge.schema.json`.
3. Ausência comprovada da string do `reference_commit_hash` e do diff da solução no manifesto público.

## Saídas Esperadas
- Arquivo público `challenge.json`.
- Arquivo restrito de avaliação `eval_protected/reference_spec.json`.
- Relatório de validação com status (`VALIDATED` ou `FAILED`).

## Integração com outras skills
- Recebe candidatos de: **`patchtime-repo-forensics`**.
- Encaminha para isolamento em: **`patchtime-snapshot-reconstruction`**.
- Encaminha os critérios de teste para: **`patchtime-evaluation-integrity`**.

