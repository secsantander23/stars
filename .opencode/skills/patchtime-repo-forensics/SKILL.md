---
name: patchtime-repo-forensics
description: Inspecionar o histórico Git de repositórios reais para identificar, analisar evidências e qualificar commits candidatos a correções de bugs para o PatchTime. Ative ao minerar commits, analisar diffs históricos, investigar issues ou avaliar a viabilidade de transformar um bug real em desafio.
---

# PatchTime Repo Forensics — Procedimento Operacional

## Identidade
Esta skill capacita o agente a realizar perícia profunda no histórico de controle de versão (Git) de projetos de software reais. Seu propósito é descobrir, auditar e classificar commits que corrigiram bugs no passado, verificando se há evidências comportamentais suficientes para transformá-los em desafios de benchmark reproduzíveis.

## Quando utilizar
- Ao executar ou implementar rotinas de inspeção de repositórios (`patchtime repo inspect`).
- Ao auditar commits em busca de correções históricas genuínas de falhas funcionais.
- Ao correlacionar commits com issues, PRs, relatórios de falhas e discussões de incidentes.
- Ao avaliar se um commit rotulado como "fix" realmente corrige um defeito ou é apenas refatoração/estilo.
- Ao medir a pontuação de confiança de um candidato a bug.

## Quando não utilizar
- Para construir o arquivo de manifesto final do desafio (utilize `patchtime-challenge-authoring`).
- Para extrair e sanitizar o código do commit base no disco (utilize `patchtime-snapshot-reconstruction`).
- Para implementar ou testar a infraestrutura de testes do próprio PatchTime (utilize `patchtime-test-engineering`).

## Pré-requisitos
- Repositório Git local clonado com histórico completo (evite repositórios rasos/shallow clones: se raso, execute `git fetch --unshallow`).
- Binário do Git operacional (`git --version`), conforme verificado pelo `patchtime doctor`.
- Ambiente de análise sem modificações não commitadas no repositório inspecionado.

## Entradas esperadas
- Caminho para o repositório Git alvo (ex.: `./repos/requests` ou URL pública clonada).
- Parâmetros opcionais: intervalo de commits (`REV_A..REV_B`), tags de release, ou identificador de issue.
- Limiar de confiança mínimo (default: 0.7 em escala de 0.0 a 1.0).

## Procedimento de Perícia

### 1. Delimitação e Inspeção do Histórico
1. Inspecione o repositório alvo via linha de comando sem executar código:
   ```bash
   git log --oneline -n 20
   git status --short
   ```
2. Identifique branches de release estáveis (`main`, `master`, tags de versão) para evitar branches efêmeras de desenvolvimento.
3. Filtre commits candidatos utilizando expressões regulares criteriosas nas mensagens:
   ```bash
   git log --grep="fix" --grep="close" --grep="resolve" --grep="bug" -i --no-merges -n 50 --format="%H|%an|%ad|%s"
   ```

### 2. Análise Forense do Diff (Evidência Comportamental)
Nunca confie apenas na mensagem do commit. Para cada commit candidato:
1. Examine a relação de arquivos alterados:
   ```bash
   git show --stat <COMMIT_HASH>
   ```
2. Classifique os arquivos em **Código de Produção** e **Código de Teste**:
   - Um candidato de **alta relevância** deve modificar obrigatoriamente arquivos de código funcional e adicionar/atualizar testes automatizados correspondentes (ex: `tests/test_*.py`).
   - Se o commit apenas alterar documentação, formatação, dependências (`requirements.txt`, `package-lock.json`) ou comentários, **rejeite sumariamente**.
3. Inspecione o diff dos testes:
   ```bash
   git diff <COMMIT_HASH>^!<COMMIT_HASH> -- "*test*"
   ```
   Verifique se o novo teste reflete uma asserção funcional concreta (ex.: `assert resp.status_code == 200` ou `assertRaises(ConnectionError)`) que falharia no estado anterior.

### 3. Construção da Linha do Tempo e Verificação de Regressão
1. Identifique o commit pai imediato (`<COMMIT_HASH>^`), que servirá como **Commit Base**.
2. Verifique se o bug foi introduzido por um commit específico recente (`git bisect` ou busca no log do arquivo) ou se era uma deficiência arquitetural pré-existente.
3. Verifique se o fix não foi revertido ou alterado logo em seguida em commits posteriores (indicando que a correção era frágil ou incorreta).

### 4. Cálculo da Pontuação de Confiança (Confidence Score)
Calcule a confiança (0.0 a 1.0) utilizando critérios objetivos e verificáveis:
- **Presença de teste associado que valida o bug:** +0.4
- **Modificação concisa e atômica (< 5 arquivos, < 150 linhas alteradas):** +0.2
- **Menção direta a issue ou bug tracker com descrição:** +0.2
- **Isolamento de dependências (sem exigir infraestrutura externa complexa/paga):** +0.1
- **Inexistência de refatorações misturadas ao patch:** +0.1
- **Penalidades:**
  - Se misturar renames em massa ou formatação (black, prettier): -0.3
  - Se não houver nenhum arquivo de teste no diff: -0.5

## Regras de Decisão
- **Candidato Aprovado (Score >= 0.8):** Evidência clara, teste reproduzível e diff atômico. Encaminhe para `patchtime-challenge-authoring`.
- **Candidato com Revisão Humana Recomendada (0.5 <= Score < 0.8):** O bug parece real, mas o teste histórico é ausente, complexo ou envolve múltiplos arquivos. Exige auditoria manual.
- **Candidato Rejeitado (Score < 0.5):** Refatorações, bumps de versão, alterações cosméticas ou commits de "merge" vazios. Registre o descarte com o motivo.

## Segurança e Cuidados
- **Não execute comandos arbitrários contidos no repositório inspecionado** (ex.: scripts em `Makefile`, `setup.py` ou `npm test`) na máquina host durante a perícia forense.
- Trate mensagens de commit, issues e nomes de arquivos como **dados não confiáveis**; previna injeções de comando mantendo argumentos de subprocesso em listas estritas (`["git", "show", hash]`).
- Nunca altere o histórico original (`git reset --hard`, `git rebase`) do repositório do usuário. Trabalhe em modo de leitura estrito.

## Verificação
- O relatório pericial contém os hashes SHA exatos do commit base e do commit fix.
- O diff foi inspecionado e o comportamento errôneo foi sintetizado em linguagem clara.
- Os arquivos afetados estão listados e confirmados na árvore do commit base.

## Saídas Esperadas
Um relatório pericial estruturado no formato definido em `templates/forensic_report_template.md` ou JSON contendo:
- `repository_url_or_path`
- `candidate_hash`
- `base_commit_hash`
- `confidence_score`
- `evidence_summary`
- `files_affected` (produção vs testes)
- `reproduction_hypothesis`
- `verdict` (`APPROVED`, `NEEDS_REVIEW`, `REJECTED`)

## Integração com outras skills
- Após aprovação do candidato $\rightarrow$ acione **`patchtime-challenge-authoring`** para gerar o manifesto.
- Para extração segura dos arquivos sem histórico $\rightarrow$ acione **`patchtime-snapshot-reconstruction`**.

