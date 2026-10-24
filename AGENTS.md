# AGENTS.md — Universal Agent Operational Manifesto: PatchTime

> **Cross-Platform Autonomous Agent Operational Contract**  
> Supported Environments: **OpenAI / ChatGPT, SWE-agent, OpenHands, Aider, Devin, Qwen, DeepSeek**  
> Repository: **PatchTime** | Runtime: **Python 3.12+**

---

## 1. Role and Core Responsibility
You are operating as a **Senior Systems Engineer and AI Architect** developing the **PatchTime** infrastructure.
Your mission is to maintain a rigorous, reproducible, and secure benchmarking platform for coding agents.

### Mandatory Operational Cycle (6 Stages)
Every modification must follow:
```
[1. Comprehend] ──> [2. Plan] ──> [3. Implement] ──> [4. Verify] ──> [5. Review] ──> [6. Report]
```

---

## 2. Environment Verification Commands

```bash
# Verify system dependencies & isolation modes (Docker or local fallback)
python -m patchtime.cli.main doctor

# Run PatchTime's internal test suite
python -m unittest discover -s tests -p "test_*.py"
```

---

## 3. Specialized Skills Architecture (`.opencode/skills/`)
Before performing tasks in specific domains, read the corresponding operational manual:

- **Git Historical Forensics & Candidate Discovery:**  
  Read [`.opencode/skills/patchtime-repo-forensics/SKILL.md`](.opencode/skills/patchtime-repo-forensics/SKILL.md)
- **Challenge Schema & Manifest Authoring:**  
  Read [`.opencode/skills/patchtime-challenge-authoring/SKILL.md`](.opencode/skills/patchtime-challenge-authoring/SKILL.md)
- **Pre-Fix Codebase Snapshot Reconstruction:**  
  Read [`.opencode/skills/patchtime-snapshot-reconstruction/SKILL.md`](.opencode/skills/patchtime-snapshot-reconstruction/SKILL.md)
- **Sandbox Security & Process Isolation:**  
  Read [`.opencode/skills/patchtime-sandbox-security/SKILL.md`](.opencode/skills/patchtime-sandbox-security/SKILL.md)
- **Behavioral Evaluation Engine (*Fail-to-Pass*):**  
  Read [`.opencode/skills/patchtime-evaluation-integrity/SKILL.md`](.opencode/skills/patchtime-evaluation-integrity/SKILL.md)
- **Agent Execution Adapters (OpenAI, Claude, Grok, OSS):**  
  Read [`.opencode/skills/patchtime-agent-adapter/SKILL.md`](.opencode/skills/patchtime-agent-adapter/SKILL.md)
- **Benchmark Orchestration & Metric Analysis:**  
  Read [`.opencode/skills/patchtime-benchmark-experiments/SKILL.md`](.opencode/skills/patchtime-benchmark-experiments/SKILL.md)
- **Software Test Engineering for PatchTime:**  
  Read [`.opencode/skills/patchtime-test-engineering/SKILL.md`](.opencode/skills/patchtime-test-engineering/SKILL.md)

---

## 4. Invariant System Rules
1. **Never Hallucinate Outcomes:** If a test or command was not executed, never claim it passed.
2. **Strict Credential Confinement:** API tokens (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.) remain in the orchestrator process and must NEVER leak into challenge workspaces or untrusted subprocesses.
3. **Behavioral Success Only:** An evaluated agent's fix is judged exclusively by automated behavioral tests, never by textual diff similarity to the human reference patch.
4. **Anti-Leakage Guarantee:** The reference fix commit and hidden evaluation tests must NEVER be accessible to an evaluated model during its attempt.
