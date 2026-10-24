# PatchTime ⏱️

> **Infraestrutura experimental reproduzível para benchmark de agentes de programação em bugs reais.**

O **PatchTime** é uma ferramenta open source criada para transformar bugs históricos de projetos reais em desafios rigorosamente reproduzíveis para agentes de Inteligência Artificial. 

A ferramenta recupera o estado do código imediatamente anterior à correção original, encapsula o problema em um ambiente seguro e hermético (sem que o modelo tenha acesso à solução humana futura), executa tentativas de resolução com diferentes agentes e avalia os resultados por meio de testes comportamentais automatizados.

---

## 🎯 Por que o PatchTime?

A maioria dos benchmarks atuais sofre de um ou mais dos seguintes problemas:
1. **Contaminação de Dados (Data Contamination):** Modelos de IA já viram a solução original em seu conjunto de treinamento.
2. **Avaliação Frágil:** Avaliar código por semelhança textual com o patch original descarta soluções válidas e inovadoras que corrigem o mesmo bug.
3. **Falta de Isolamento:** Execução desprotegida de código de terceiros e de código gerado por modelos autônomos na máquina do desenvolvedor.
4. **Vazamento da Solução (Leakage):** Deixar o histórico `.git` completo exposto, permitindo ao agente inspecionar commits futuros e copiar a correção.

O **PatchTime** resolve esses problemas com:
- **Separação Hermética:** A solução de referência e os testes ocultos residem em área protegida, inacessível ao agente avaliado.
- **Isolamento Multinível:** Suporte nativo a execução em contêineres Docker/OCI ou em workspaces efêmeros e descartáveis locais com subprocessos protegidos.
- **Avaliação por Comportamento:** Veredito emitido com base em testes automatizados (*Fail-to-Pass* e *Pass-to-Pass*), prevenindo regressões.
- **Multi-Modelos:** Interface aberta para comparar agentes proprietários e de código aberto sob condições idênticas.

---

## 🤖 Ecossistema Multi-Modelos Suportado

O PatchTime foi projetado para acomodar qualquer agente ou modelo de programação de forma modular e isolada:

| Ecossistema | Modelos / Ferramentas | Modo de Integração |
| :--- | :--- | :--- |
| **Claude** | Claude 3.7 Sonnet, Claude Code CLI | Processo Headless CLI ou API Anthropic direta |
| **ChatGPT / OpenAI** | GPT-4o, o1, o3-mini | Tool Calling / Function Calling com controle de raciocínio |
| **Grok** | Grok-2, Grok-Code | API xAI com ferramentas de edição de workspace |
| **Kiro / Cursor** | Assistentes baseados em contexto e IDE | Conectores CLI / Pontes de workspace `.cursorrules` |
| **OpenCode / OSS** | Aider, OpenHands (OpenDevin), SWE-agent | CLI aberto com DeepSeek-R1, Qwen 2.5 Coder e Llama 3 |

*Consulte a especificação arquitetural completa dos adaptadores em nosso plano de multi-modelos.*

---

## 🚀 Instalação e Início Rápido

### Pré-requisitos
- **Python:** Versão 3.12 ou superior
- **Git:** Versão 2.30+
- **Docker:** *(Opcional, mas recomendado para isolamento máximo em contêineres)*

### Instalação em Modo de Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/patchtime/patchtime.git
cd patchtime

# Instale em modo editável
pip install -e .
```

### Diagnóstico do Ambiente
Para verificar se seu ambiente está pronto e qual modo de isolamento está ativo:

```bash
patchtime doctor
```

Exemplo de saída:
```text
====================================================================
  PATCHTIME DOCTOR — Diagnóstico de Ambiente & Isolamento
====================================================================
Sistema Operacional: Windows 11 (AMD64)
Modo de Isolamento Padrão: LOCAL_PROCESS
--------------------------------------------------------------------
[  OK  ] Python Runtime: Python 3.14.7 atende ao requisito (>= 3.12)
[  OK  ] Git CLI: git version 2.56.0 detectado e operacional
[ AVISO] Isolamento Docker: Docker não encontrado no PATH. Modo ativo: local_process.
         └─ Nota: Para ambientes multi-tenant e proteção máxima, instale e inicie o Docker.
[  OK  ] Workspace Temporário: Criação, escrita e limpeza de diretórios efêmeros operando com segurança
--------------------------------------------------------------------
Status Final: OPERACIONAL. O PatchTime está pronto para execução.
Observação: Usando fallback de processos locais isolados para execuções.
====================================================================
```

---

## 🛠️ Comandos Principais do CLI

```bash
# 1. Diagnosticar o sistema
patchtime doctor

# 2. Inspecionar histórico Git de um repositório em busca de bugs candidatos
patchtime repo inspect ./meu-projeto --min-confidence 0.8

# 3. Validar se um manifesto de desafio é válido e seguro
patchtime challenge validate ./challenges/py-requests-4021/challenge.json

# 4. Executar benchmark com um modelo específico
patchtime benchmark run --challenge py-requests-4021 --agent claude

# 5. Comparar o desempenho entre dois modelos no mesmo desafio
patchtime benchmark compare run-claude-01 run-chatgpt-01

# 6. Exibir e exportar resultados
patchtime results show run-claude-01
patchtime results export run-claude-01 --format json
```

---

## 📐 Arquitetura do Repositório

```
patchtime/
├── AGENT.md                 # Manual operacional estrito para agentes e desenvolvedores
├── README.md                # Este documento
├── pyproject.toml           # Manifesto do projeto e dependências de build
├── src/
│   └── patchtime/
│       ├── cli/             # Interface de linha de comando (doctor, repo, challenge, benchmark)
│       ├── core/            # Modelos de dados imutáveis, exceções e regras centrais
│       ├── analyzer/        # Mineração de commits históricos e detecção de bugs
│       ├── challenge/       # Construtor de desafios, validador de esquemas e snapshots
│       ├── environment/     # Sandboxes de isolamento (local_process e docker_container)
│       ├── runner/          # Adaptadores para Claude, ChatGPT, Grok, Kiro, OpenCode
│       ├── evaluation/      # Motor de avaliação e testes comportamentais independentes
│       └── benchmark/       # Orquestração de matrizes de testes e geração de relatórios
├── tests/
│   ├── unit/                # Testes unitários de modelos, doctor e exceções
│   ├── integration/         # Testes de isolamento de workspaces e runners
│   └── e2e/                 # Cenários ponta a ponta com repositório sintético
└── docs/                    # Especificações de esquemas e contratos de adaptadores
```

---

## 🛡️ Segurança e Governança

O PatchTime trata qualquer repositório analisado e qualquer código gerado por IA como **código não confiável**.
- Nenhum script arbitrário é executado diretamente no host sem sandbox.
- Credenciais e chaves de API nunca são repassadas ao ambiente onde o código do desafio é executado.
- Para orientações detalhadas de engenharia, consulte o [**`AGENT.md`**](AGENT.md).

---

## 📄 Licença

Distribuído sob a licença **Apache 2.0**. Consulte o arquivo de licença para mais informações.

