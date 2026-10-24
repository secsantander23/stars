---
name: patchtime-evaluation-integrity
description: Garantir a validade científica, imparcialidade e integridade dos critérios de avaliação comportamental de correções geradas por agentes no PatchTime. Ative ao projetar suítes de testes fail-to-pass, auditar testes de regressão, prevenir falsos positivos e isolar a engine de avaliação.
---

# PatchTime Evaluation Integrity — Procedimento Operacional

## Identidade
Esta skill estabelece o rigor metodológico para julgar se a tentativa de um agente de programação resolveu verdadeiramente o problema. O princípio basilar do PatchTime é que **o sucesso é determinado pelo comportamento verificável do software em execução**, e nunca pela semelhança textual com o patch do desenvolvedor humano ou por explicações emitidas pelo modelo.

## Quando utilizar
- Ao desenhar ou implementar o motor de avaliação (`src/patchtime/evaluation/evaluator.py`).
- Ao auditar testes históricos herdados de um repositório para evitar testes frágeis, intermitentes (flaky) ou dependentes de ambiente.
- Ao conceber e isolar testes de avaliação ocultos (*hidden evaluation tests*).
- Ao analisar relatórios de execução para distinguir aprovação real de falsos positivos (soluções "hardcoded" ou contornos frágeis).

## Quando não utilizar
- Para inspecionar logs de Git em busca de novos bugs (utilize `patchtime-repo-forensics`).
- Para executar processos e gerenciar limites de CPU/memória (utilize `patchtime-sandbox-security`).
- Para agregar e comparar estatísticas entre múltiplos modelos (utilize `patchtime-benchmark-experiments`).

## Pré-requisitos
- Manifesto de desafio validado contendo as seções `evaluation`.
- Workspace do desafio com as alterações geradas pelo agente participante.
- Harness de testes automatizados suportado pelo projeto alvo (ex.: `pytest`, `unittest`, `jest`).

---

## Taxonomia e Separação dos Testes

O PatchTime divide os testes em 4 categorias rigorosas:

1. **Testes Visíveis de Desenvolvimento (`visible_tests`):**
   - Disponíveis dentro do workspace para que o agente possa executar enquanto desenvolve.
   - Servem para o agente entender a interface e verificar sanidade básica.
2. **Testes do Bug (*Fail-to-Pass*):**
   - Testes específicos que atestam a existência do defeito.
   - **Regra Fundamental de Validação:** Devem obrigatoriamente **FALHAR** no commit base e **PASSAR** quando o bug for corrigido.
3. **Testes de Regressão (*Pass-to-Pass*):**
   - Testes que cobrem o restante do sistema.
   - Devem **PASSAR** no commit base e **CONTINUAR PASSANDO** após a alteração do agente.
4. **Testes Ocultos de Verificação (*Hidden Tests*):**
   - Casos de borda adicionais mantidos fora do alcance do agente durante toda a tentativa.
   - Impedem que o agente programe um "atalho" ou hardcode específico apenas para os testes conhecidos.

---

## Procedimento de Avaliação Independente

### 1. Separação de Poderes na Execução
O participante nunca avalia a si mesmo. O processo de avaliação ocorre em uma etapa distinta:
1. O agente de IA encerra sua execução e gera o diff final no workspace.
2. O PatchTime congela o workspace (torna arquivos somente leitura se possível).
3. O PatchTime injeta os testes de avaliação restritos (`fail_to_pass` e `hidden_tests`) a partir de seu cofre seguro (`eval_protected/`).
4. Os testes são executados por um processo filho isolado, com captura bruta dos resultados.

### 2. Algoritmo de Emissão do Veredito
Avalie a matriz de resultados:

```
┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
│ Status dos Testes       │ Status dos Testes       │ Veredito Final Emitido  │
│ Fail-to-Pass (do Bug)   │ Pass-to-Pass (Regressão)│ pelo PatchTime          │
├─────────────────────────┼─────────────────────────┼─────────────────────────┤
│ Todos PASSAM            │ Todos PASSAM            │ RESOLVED                │
│ Parte PASSA             │ Todos PASSAM            │ PARTIAL_FIX             │
│ Qualquer resultado      │ Algum FALHA             │ REGRESSION              │
│ Todos FALHAM            │ Todos PASSAM            │ FAILED                  │
│ Timeout / Crash         │ N/A                     │ INFRA_TIMEOUT / ERROR   │
└─────────────────────────┴─────────────────────────┴─────────────────────────┘
```

### 3. Prevenção Contra Armadilhas de Avaliação
- **VETO ao Diff Textual:** Não rejeite uma solução apenas porque o agente utilizou uma biblioteca padrão diferente ou organizou a lógica de forma diversa do autor humano original.
- **Detecção de Testes Intermitentes (Flaky Tests):** Se um teste de regressão falhar aleatoriamente sem relação com a alteração, isole o teste e registre ressalva metodológica.
- **Detecção de Fraude / Mocking Indevido dos Testes:** O avaliador deve inspecionar se o agente tentou modificar ou apagar arquivos de teste existentes no workspace (`diff_inspector.py`). Modificações não autorizadas na suíte de testes desqualificam a tentativa imediatamente com status `EVALUATION_TAMPERING`.

---

## Regras de Decisão
- Se um teste fail-to-pass passar no commit base sem nenhuma alteração: o desafio é **INVÁLIDO**. Descarte o desafio.
- Se o agente resolver o bug principal, mas quebrar 1 teste de regressão essencial: o veredito obrigatório é **`REGRESSION`**, e nunca `RESOLVED`.
- Se a cobertura de testes do repositório original for precária: registre a limitação no relatório de resultado (`coverage_limitation: true`).

## Verificação
- O relatório de avaliação (`result.json`) é validado contra o modelo `EvaluationVerdict` em `src/patchtime/core/models.py`.
- O relatório discrimina detalhadamente quais testes específicos passaram e quais falharam.
- O tempo de execução de cada teste é registrado em milissegundos.

## Saídas Esperadas
- Arquivo `result.json` auditável contendo:
  - `status`: (`RESOLVED`, `PARTIAL_FIX`, `REGRESSION`, `FAILED`)
  - `fail_to_pass_passed`: lista de testes
  - `fail_to_pass_failed`: lista de testes
  - `pass_to_pass_passed`: lista de testes
  - `pass_to_pass_failed`: lista de testes
  - `execution_time_seconds`: tempo real medido

## Integração com outras skills
- Recebe a especificação de testes de: **`patchtime-challenge-authoring`**.
- Executa sobre o ambiente protegido por: **`patchtime-sandbox-security`**.
- Fornece métricas e vereditos consolidados para: **`patchtime-benchmark-experiments`**.

