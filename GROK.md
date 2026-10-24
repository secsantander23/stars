# GROK.md — Diretrizes para xAI Grok & Grok-Code no PatchTime

> **Manual Operacional para Modelos da Família Grok (xAI)**  
> Projeto: **PatchTime** | Stack: **Python 3.12+**

---

## 1. Missão do Modelo no Repositório
Você está atuando como engenheiro sênior no desenvolvimento da infraestrutura de benchmark do **PatchTime**.
Seu papel é criar código seguro, testável, modular e fortemente tipado em Python 3.12+.

---

## 2. Comandos Operacionais Essenciais

```bash
# Diagnóstico de integridade do ambiente
python -m patchtime.cli.main doctor

# Execução da suíte de testes do PatchTime
python -m unittest discover -s tests -p "test_*.py"
```

---

## 3. Catálogo de Skills em `.opencode/skills/`
Antes de modificar componentes específicos do PatchTime, consulte as instruções detalhadas da skill correspondente:
- **Perícia de Commits e Histórico Git:** `.opencode/skills/patchtime-repo-forensics/SKILL.md`
- **Especificação de Desafios (`challenge.v1.json`):** `.opencode/skills/patchtime-challenge-authoring/SKILL.md`
- **Extração de Snapshots Pré-Fix:** `.opencode/skills/patchtime-snapshot-reconstruction/SKILL.md`
- **Isolamento de Processos e Quotas de Recursos:** `.opencode/skills/patchtime-sandbox-security/SKILL.md`
- **Validação de Testes Comportamentais:** `.opencode/skills/patchtime-evaluation-integrity/SKILL.md`
- **Construção de Adaptadores de Agentes:** `.opencode/skills/patchtime-agent-adapter/SKILL.md`
- **Execução Experimental e Métricas de Benchmark:** `.opencode/skills/patchtime-benchmark-experiments/SKILL.md`
- **Engenharia de Testes Internos do PatchTime:** `.opencode/skills/patchtime-test-engineering/SKILL.md`

---

## 4. Regras Absolutas de Segurança
1. **Sem Execuções Desprotegidas:** Nunca utilize `shell=True` ao disparar subprocessos.
2. **Defesa Contra Vazamentos:** Durante avaliações, a solução humana e o histórico futuro do Git são confidenciais e nunca devem ser expostos ao agente participante.
3. **Imparcialidade Metodológica:** A correção de um bug é comprovada exclusivamente pela execução de testes de comportamento automatizados (*Fail-to-Pass* e *Pass-to-Pass*), e não por similaridade com o diff do patch original.
