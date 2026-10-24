---
name: patchtime-snapshot-reconstruction
description: Reconstruir snapshots históricos do código no commit base anterior à correção, expurgando histórico futuro do Git, patches de referência e vazamentos de dados. Ative ao extrair árvores de arquivos históricas, higienizar repositórios para o agente ou validar se o estado pré-fix é autêntico.
---

# PatchTime Snapshot Reconstruction — Procedimento Operacional

## Identidade
Esta skill é especializada na cirurgia e reconstrução física do código-fonte em um momento histórico exato (imediatamente anterior ao bug fix). Ela garante que o workspace entregue ao agente de IA represente fielmente o estado do projeto no commit base, bloqueando todas as vias pelas quais a solução humana futura possa vazar.

## Quando utilizar
- Ao implementar ou executar rotinas de extração de snapshots (`src/patchtime/challenge/snapshot.py`).
- Ao preparar o diretório de trabalho efêmero onde o agente participante atuará.
- Ao auditar um workspace de desafio para certificar a ausência de histórico Git futuro, commits reveladores, reflogs ou patches residuais.
- Ao verificar a integridade criptográfica dos arquivos extraídos contra o commit base.

## Quando não utilizar
- Para redigir o manifesto descritivo do desafio (utilize `patchtime-challenge-authoring`).
- Para executar os testes de avaliação da solução (utilize `patchtime-evaluation-integrity`).
- Para configurar políticas de isolamento de processo e container (utilize `patchtime-sandbox-security`).

## Pré-requisitos
- Repositório Git de origem clonado e com commit base acessível.
- Hash SHA-40 do commit base validado.
- Ferramenta Git disponível no PATH.
- Diretório de destino temporário com permissão de escrita e espaço em disco suficiente.

---

## Procedimento de Reconstrução Hermética

### 1. Resolução Explícita do Commit Base
1. Valide a existência e o tipo do objeto Git:
   ```bash
   git cat-file -t <BASE_COMMIT_HASH>
   # Deve retornar obrigatoriamente: "commit"
   ```
2. Confirme a relação cronológica com o commit fix (`<FIX_COMMIT_HASH>`):
   ```bash
   git merge-base --is-ancestor <BASE_COMMIT_HASH> <FIX_COMMIT_HASH>
   # Código de saída 0 confirma que o base commit é ancestral legítimo do fix
   ```

### 2. Extração Fiel dos Arquivos (Sem Metadados do Git)
**REGRA DE OURO:** Jamais copie o diretório `.git` original para o workspace do agente participante. O `.git` contém os commits futuros com o fix e mensagens de commit reveladoras.
1. Utilize `git archive` para extrair os arquivos limpos diretamente da árvore do commit base:
   ```bash
   git archive --format=tar <BASE_COMMIT_HASH> | tar -x -C <DESTINATION_WORKSPACE>
   ```
2. Caso o projeto utilize submódulos Git:
   - Inspecione `.gitmodules` no commit base.
   - Extraia os submódulos nas revisões exatas registradas naquele commit base específico.
3. Se o agente precisar de um repositório Git funcional para trabalhar (ex.: para executar `git diff` ou criar branches locais):
   - Inicialize um **novo repositório Git efêmero e anônimo** no workspace de destino:
     ```bash
     cd <DESTINATION_WORKSPACE>
     git init -b main
     git config user.name "PatchTime Sandbox"
     git config user.email "sandbox@patchtime.local"
     git add -A
     git commit -m "Initial challenge state"
     ```
   - Dessa forma, o agente tem ferramentas de Git funcionais, mas seu histórico possui apenas 1 commit neutro e zero rastros da solução futura.

### 3. Varredura Anti-Vazamento (Leakage Scrubbing)
Inspecione minuciosamente a árvore extraída à procura de vetores residuais de vazamento:
1. **Arquivos temporários e patches:**
   - Procure por `*.patch`, `*.diff`, `*.rej`, `*.orig` esquecidos.
2. **Caches de build e bytecode:**
   - Remova recursivamente `__pycache__`, `*.pyc`, `.pytest_cache`, `node_modules`, `dist/`, `build/`.
3. **Logs e arquivos de CI/CD:**
   - Inspecione se arquivos de issue salvos localmente contêm a solução.
4. **Verificação de Hash Tree:**
   - Compare a árvore de arquivos com a árvore registrada no Git:
     ```bash
     git rev-parse <BASE_COMMIT_HASH>^{tree}
     ```

---

## Regras de Decisão
- Se o commit base contiver submódulos inacessíveis, repositórios privados ou artefatos Git-LFS corrompidos: **Interrompa a reconstrução** e marque o snapshot como `UNREPRODUCIBLE_EXTERNAL_DEPENDENCY`.
- Se qualquer arquivo no workspace contiver menção ao hash do commit fix ou ao autor do fix futuro: **Remova o artefato ou higienize o texto**.

## Segurança
- **Operação Não Destrutiva:** Nunca execute `git checkout -f`, `git clean -fdx` ou `git reset --hard` no repositório de trabalho principal do usuário. Todas as operações de extração devem ser direcionadas a um diretório temporário descartável.
- **Prevenção de Zip Slip / Tarbomb:** Na descompactação do arquivo do snapshot, valide se nenhum caminho contém `../` ou aponta para fora de `<DESTINATION_WORKSPACE>`.

## Verificação
1. O workspace possui os arquivos funcionais correspondentes ao commit base.
2. A árvore `.git` original **não está presente** no workspace.
3. A execução de `git log` dentro do workspace do agente (se inicializado) exibe apenas o commit inicial anônimo.
4. O hash SHA da árvore gerada é idêntico ao do commit base do Git.

## Saídas Esperadas
- Diretório de workspace pronto e sanitizado.
- Arquivo `snapshot_meta.json` contendo:
  - `base_commit_hash`
  - `tree_hash`
  - `extraction_timestamp`
  - `files_count`
  - `verification_status` (`VERIFIED` ou `CORRUPTED`)

## Integração com outras skills
- Recebe instruções de: **`patchtime-challenge-authoring`**.
- Entrega o workspace sanitizado para: **`patchtime-sandbox-security`** e **`patchtime-agent-adapter`**.

