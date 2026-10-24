---
name: patchtime-test-engineering
description: Projetar, implementar e manter a suíte de testes de software do próprio projeto PatchTime (unitários, integração, e2e sintéticos e segurança). Ative ao adicionar testes para módulos do PatchTime, criar fixtures, testar o CLI ou garantir cobertura contra regressões.
---

# PatchTime Test Engineering — Procedimento Operacional

## Identidade
Esta skill é dedicada à engenharia da qualidade e validação contínua da **infraestrutura de software do próprio PatchTime**. Ao contrário da avaliação de bugs históricos minerados, esta especialidade garante que o código do PatchTime (CLI, parsers, sandboxes, modelos e runners) seja robusto, determinístico, auditável e imune a regressões internas.

## Quando utilizar
- Ao implementar ou refatorar qualquer módulo em `src/patchtime/`.
- Ao criar testes unitários para novos comandos do CLI ou novos modelos em `tests/unit/`.
- Ao desenvolver testes de integração para criação de workspaces temporários e captura de logs em `tests/integration/`.
- Ao criar ou manter fixtures sintéticas determinísticas para cenários ponta a ponta em `tests/fixtures/`.
- Ao auditar proteções de segurança em `tests/security/` (tentativas de path traversal, estouro de tempo e injeção).

## Quando não utilizar
- Para desenhar os testes que avaliam agentes em um benchmark histórico (utilize `patchtime-evaluation-integrity`).
- Para empacotar os arquivos de um desafio (utilize `patchtime-challenge-authoring`).
- Para inspecionar históricos de projetos externos (utilize `patchtime-repo-forensics`).

## Pré-requisitos
- Python 3.12+ operacional (verificado pelo comando `patchtime doctor`).
- Estrutura de testes padrão em `tests/` (`unit/`, `integration/`, `e2e/`, `security/`, `fixtures/`).
- Compatibilidade dupla: os testes devem poder ser executados tanto pelo executor nativo `python -m unittest discover tests` quanto pelo `pytest` quando instalado no ambiente.

---

## Pirâmide de Testes do PatchTime

```
             ┌─────────────────────────┐
             │       E2E Tests         │  1-2 fluxos sintéticos determinísticos
             │      (tests/e2e)        │  (desafio -> mock agent -> veredito)
             ├─────────────────────────┤
             │    Integration Tests    │  Isolamento de subprocessos,
             │   (tests/integration)   │  extração de tar e persistência
             ├─────────────────────────┤
             │     Security Tests      │  Anti-path traversal, symlinks hostis,
             │    (tests/security)     │  sanitização de logs e envs
             ├─────────────────────────┤
             │       Unit Tests        │  Modelos, exceções, comandos CLI,
             │      (tests/unit)       │  parsers de diff e cálculos
             └─────────────────────────┘
```

---

## Procedimento de Implementação de Testes

### 1. Testes Unitários (`tests/unit/`)
1. Todo novo modelo, função de parsing ou comando deve possuir cobertura direta.
2. Não faça chamadas externas de rede ou escrita em diretórios fixos do usuário; utilize mocks (`unittest.mock.patch`) ou `tempfile.TemporaryDirectory`.
3. Valide sempre três cenários:
   - **Caso Positivo:** Entrada válida, retorno conforme especificado.
   - **Caso Inválido:** Entrada incorreta, disparo da exceção correspondente (`assertRaises(PatchTimeError)`).
   - **Caso de Borda (Edge Case):** Entrada vazia, caracteres especiais, valores nulos.

### 2. Testes de Segurança (`tests/security/`)
1. Teste de tentativa de escrita fora do workspace:
   - Forneça caminhos com `../../etc/passwd` ou `C:\Windows\System32` e assegure o disparo imediato de `SecurityViolationError`.
2. Teste de contenção de variáveis sensíveis:
   - Simule a presença de `ANTHROPIC_API_KEY="sk-ant-123"` no ambiente do host e verifique se o subprocesso do desafio recebe um ambiente higienizado sem essa chave.
3. Teste de sanitização de logs:
   - Valide se tokens inseridos em saídas de log são substituídos por `[REDACTED_SECRET]`.

### 3. Cenário Ponta a Ponta com Fixture Sintética (`tests/e2e/`)
O PatchTime deve manter um mini-projeto sintético pequeno e determinístico para validar o ciclo completo:
1. **Fixture (`tests/fixtures/synthetic_calc/`):** Mini-biblioteca de cálculo com 1 bug intencional e 1 teste unitário que falha.
2. **Execução:**
   - Instancia o `ChallengeBuilder` sobre a fixture.
   - Executa o runner com um agente mock perfeito $\rightarrow$ Valida que o veredito final é `RESOLVED`.
   - Executa o runner com um agente mock inerte $\rightarrow$ Valida que o veredito final é `FAILED`.
   - Executa o runner com um agente mock travado $\rightarrow$ Valida que o timeout dispara `INFRA_TIMEOUT`.
3. **REGRA:** Nunca utilize mocks para simular todo o fluxo E2E; a execução de subprocesso local e a geração do arquivo `result.json` devem ocorrer de verdade no disco.

---

## Regras de Decisão
- Se um teste depender de ferramentas que podem não existir no host (ex.: Docker): utilize decorators de skip condicional:
  ```python
  @unittest.skipUnless(shutil.which("docker"), "Docker não disponível no host")
  def test_docker_isolation(self):
      ...
  ```
- Nenhum teste deve deixar diretórios ou arquivos residuais após a execução; use sempre context managers de limpeza garantida (`with tempfile.TemporaryDirectory()`).

## Verificação
1. Execute a suíte de testes:
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```
2. Todos os testes devem passar com código de saída 0.
3. Nenhuma advertência de arquivo não fechado ou exceção não tratada deve vazar no console.

## Saídas Esperadas
- Arquivos de teste limpos, documentados e fortemente tipados em `tests/unit/`, `tests/integration/`, `tests/security/` e `tests/e2e/`.
- Relatório de execução do unittest confirmando a quantidade de testes aprovados.

## Integração com outras skills
- Valida o código produzido por todas as outras skills.
- Testa as defesas concebidas em: **`patchtime-sandbox-security`**.
- Testa os adaptadores implementados em: **`patchtime-agent-adapter`**.

