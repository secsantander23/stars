# Checklist de Auditoria de Integridade de Testes — PatchTime

Utilize este checklist antes de homologar uma suíte de avaliação para um desafio.

### 1. Testabilidade no Commit Base
- [ ] O teste fail-to-pass foi executado no commit base limpo.
- [ ] O teste falhou comprovadamente no commit base.
- [ ] A falha no commit base decorre da lógica do bug, e não de ausência de dependências de ambiente.

### 2. Validação da Solução de Referência Humana
- [ ] O teste fail-to-pass foi executado aplicando o patch original humano.
- [ ] O teste passou integralmente com a correção de referência.
- [ ] Todos os testes pass-to-pass (regressão) continuaram passando com o patch humano.

### 3. Independência e Isolamento
- [ ] O teste de avaliação não faz chamadas a serviços remotos externos pela internet.
- [ ] O teste não depende de caminhos absolutos de diretório (`/home/...` ou `C:\Users\...`).
- [ ] O teste não depende de ordem aleatória de execução de fixtures.
- [ ] Os testes de avaliação ocultos residem fora do workspace acessível ao modelo.

### 4. Proteção Contra Evasão
- [ ] O harness de avaliação verifica se arquivos em `tests/` foram alterados indevidamente pelo participante.
- [ ] Asserções de teste validam o estado final dos objetos ou retornos, evitando apenas checagens triviais de tipo (`is not None`).

