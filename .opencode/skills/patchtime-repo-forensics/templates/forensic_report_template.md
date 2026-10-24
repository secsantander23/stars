# Relatório Pericial de Candidato a Bug — PatchTime Forensics

## 1. Identificação Geral
- **Repositório:** `<URL ou Caminho Local>`
- **Data da Perícia:** `<AAAA-MM-DD HH:MM UTC>`
- **Commit do Fix (Referência):** `<SHA-40>`
- **Commit Base (Imediatamente Anterior):** `<SHA-40>`
- **Mensagem do Commit:** `<Mensagem original>`
- **Issue/PR Relacionada:** `<URL ou #ID ou N/A>`

## 2. Métricas de Complexidade do Diff
- **Arquivos de Produção Modificados:** `<Total>` (ex.: `src/module/client.py`)
- **Arquivos de Teste Modificados/Adicionados:** `<Total>` (ex.: `tests/test_client.py`)
- **Linhas Inseridas:** `+<X>`
- **Linhas Removidas:** `-<Y>`
- **Grau de Atomicidade:** `[ Alta (<50 linhas) | Média (50-150) | Baixa (>150) ]`

## 3. Síntese do Comportamento
- **Comportamento Incorreto Observado (No Commit Base):**
  > Descreva o que falha, a exceção gerada ou a inconsistência de dados.
- **Comportamento Esperado (Após a Correção):**
  > Descreva o comportamento correto garantido pela solução.

## 4. Auditoria de Testes
- **Teste Histórico Associado:** `<Caminho do teste::função_de_teste>`
- **Hipótese de Falha (Fail-to-Pass):** `[Sim, testável isoladamente | Não, teste acoplado | Inexistente]`
- **Dependências Externas Detectadas:** `[Nenhuma | Banco de dados | Rede externa | N/A]`

## 5. Pontuação de Confiança & Veredito
- **Pontuação Calculada:** `<0.0 a 1.0>`
- **Veredito:** `[ APROVADO PARA DESAFIO | REQUER REVISÃO HUMANA | REJEITADO ]`
- **Justificativa do Veredito:** `<Explicação objetiva da pontuação>`

