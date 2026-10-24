# Guia de Fixtures Sintéticas para Testes do PatchTime

Fixtures sintéticas são mini-projetos autocontidos utilizados para validar o PatchTime sem dependência de clones lentos da internet.

### Estrutura Padrão de uma Fixture Sintética (`tests/fixtures/synthetic_calc/`)

```
synthetic_calc/
├── pyproject.toml
├── src/
│   └── calc/
│       ├── __init__.py
│       └── core.py          # Contém o bug intencional no commit base
└── tests/
    ├── test_arithmetic.py   # Teste Pass-to-Pass (regressão)
    └── test_division.py     # Teste Fail-to-Pass (o bug específico)
```

### Regras para Criação de Fixtures:
1. **Zero Dependências Externas:** As fixtures devem rodar utilizando unicamente bibliotecas padrão do Python (ex.: `math`, `unittest`).
2. **Determinismo:** Nenhuma operação assíncrona com sleep aleatório ou geração de números pseudo-aleatórios sem semente fixa.
3. **Tamanho Mínimo:** Todo o projeto sintético deve ter menos de 100 linhas de código no total, garantindo execução em menos de 1 segundo.
4. **Patches de Referência Testáveis:**
   - Forneça em `fixtures/patches/` um patch válido que corrige o bug (`correct_fix.patch`) e um patch incompleto (`bad_fix.patch`) para testar o avaliador.

