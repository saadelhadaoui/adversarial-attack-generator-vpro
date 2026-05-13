# Update 7 — How to Use & Full Change Log

## How to use the system right now

### 1. Start Ollama
```bash
ollama serve
# if you haven't pulled the model yet:
ollama pull qwen2.5:14b-instruct-q4_K_M
```

### 2. Run the Streamlit app
```bash
cd /home/saad/Documents/adversarial-attack-generator-vpro
/home/saad/venv/bin/streamlit run streamlit_app.py
```

### 3. Run the CLI end-to-end demo
```bash
/home/saad/venv/bin/python run_e2e_demo.py
```

### 4. Run pytest tests
```bash
/home/saad/venv/bin/pytest tests/test_end_to_end.py -v -s
```

---

## In the Streamlit UI — what to do

Go to **Section 04 → Chatbot Arena**, then use these tabs:

| Tab | What to do |
|---|---|
| **🚀 Live Defense Run** | Click buttons ①→④ in order to see the full learning demo. Toggle mode to `CONTROLLED_EXFILTRATION` before ③. |
| **🌱 Seed Library** | Browse all 70 pre-built seeds. Click **"Run this seed"** on any seed to fire it through the real pipeline. |
| **🧪 Manual Tests** | One-click predefined tests (benign, prompt injection, jailbreak, data exfiltration). |
| **🔍 Agent Trace** | See the full pipeline trace of the last interaction with DB confirmation badges. |
| **🗄️ DB Memory View** | Live SQLite rows — learned patterns, defender rules, RAG events, recent interactions. |
| **📊 Metrics** | Real charts from SQLite — defense score over time, action distribution, attack success. |

---

## Full list of all changes made across both sessions

### Backend (already worked, no changes needed)

| File | Status |
|---|---|
| `llm/client.py` | Ollama client using `qwen2.5:14b-instruct-q4_K_M` |
| `memory/structured_memory.py` | SQLite with 6 tables + **added `_migrate()`** for schema compatibility |
| `memory/company_data_store.py` | Fake company data RAG + honeytoken detection |
| `defender_agent/agent.py` | Hybrid logic: deterministic rules + RAG retrieval + LLM |
| `evaluator_agent/agent.py` | Deterministic honeytoken/data-leak checks + LLM scoring |
| `learning_agent/agent.py` | Writes learned patterns and rules to SQLite |
| `chatbot/assistant.py` | Routes PASS/BLOCK/REFORMULATE/ALLOW_WITH_MONITORING |
| `orchestration/graph.py` | Full pipeline: Input→Defender→RAG→Chatbot→Evaluator→Learner→SQLite |

### New files added

| File | What it does |
|---|---|
| `utils/chatbot_engine.py` | Routes UI messages to real `DefenseGraph` pipeline |
| `utils/attack_seed_loader.py` | Loads seeds from JSON files, filter functions |
| `data/seeds/generate_seeds.py` | Generates seeds from real benchmark datasets |
| `data/seeds/jailbreakbench_seeds.json` | 30 seeds from JailbreakBench (loaded from HF) |
| `data/seeds/hackaprompt_seeds.json` | 20 seeds from HackAPrompt taxonomy |
| `data/seeds/advbench_huggingface_seeds.json` | 20 seeds from AdvBench taxonomy |
| `data/seeds/unified_attack_seeds.json` | All 70 seeds merged |
| `run_e2e_demo.py` | CLI demo with 8 tests and pass/fail output |
| `tests/test_end_to_end.py` | pytest suite for all 10 scenarios |

### UI files rewritten

| File | What changed |
|---|---|
| `ui/chatbot_arena.py` | Full rewrite — 7 tabs, Live Defense Run, DB memory view, metrics, seed library, mode toggle, export trace |
| `ui/simulation_section.py` | Replaced fake `run_safe_simulation()` with real SQLite data |
| `ui/evidence_section.py` | Replaced fake charts with real SQLite charts |
| `streamlit_app.py` | Removed fake simulation state, added defense mode state |
