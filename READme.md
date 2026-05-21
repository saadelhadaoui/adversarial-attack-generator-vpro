# Adaptive Multi-Agent LLM Defense Lab

Adaptive Multi-Agent LLM Defense Lab is a Streamlit and Python research demo for testing defensive behavior around adversarial LLM prompts. It runs a closed loop of defender, protected chatbot, evaluator, learner, and persistent memory components using safe synthetic data, redacted attack patterns, Ollama, and SQLite.

The project is built for defensive security research and education. It does not use real company data, real credentials, or live attack payloads.

## What It Does

- Runs a protected company-style chatbot through a multi-agent defense pipeline.
- Detects benign prompts, prompt injection, jailbreak-style prompts, and synthetic data exfiltration attempts.
- Supports two operating modes:
  - `PROTECTION`: blocks detected exfiltration and unsafe requests.
  - `CONTROLLED_EXFILTRATION`: allows selected first-time synthetic leaks for demonstration, then learns and blocks repeats.
- Uses Ollama for local LLM calls through `llm/client.py`.
- Persists interactions, learned patterns, defender rules, RAG events, and metrics in SQLite.
- Displays a live Streamlit UI with chat, manual tests, live defense runs, database views, seed views, and metrics.
- Includes command-line demos and end-to-end pytest coverage.
- Includes optional presentation/report generation scripts using screenshot assets.

## Safety Scope

This project intentionally uses:

- Synthetic company records from `data/mock_company_data.csv` and `data/mock_company_data.json`.
- Synthetic honeytokens such as fake API key markers.
- Redacted or benchmark-derived prompt patterns for defensive evaluation.
- Local persistence in `data/defense_lab.db`.

It does not intentionally generate real exploit code, real credential material, or real data theft instructions.

## Architecture

```text
User or Attacker Input
        |
        v
Defender Agent
  - classifies risk
  - checks learned SQLite memory
  - chooses PASS, BLOCK, REFORMULATE, or ALLOW_WITH_MONITORING
        |
        v
Protected Assistant / Company Bot
  - answers safe requests
  - refuses blocked requests
  - retrieves synthetic company data only when explicitly allowed
        |
        v
Evaluator Agent
  - scores the interaction
  - detects honeytoken or internal data exposure
  - marks attack success, false positives, and defense score
        |
        v
Learning Agent
  - extracts abstract patterns
  - generates defender rules
  - writes learned memory to SQLite
        |
        v
SQLite Memory + Streamlit Dashboard
```

Core orchestrator: `orchestration/graph.py`

## Repository Layout

```text
attacker_agent/        Safe redacted attack seed selection and attack generation
chatbot/               Protected assistant and company bot policy behavior
data/                  Policies, mock company data, attack seeds, benchmark seed files
defender_agent/        Risk rules, policy loading, and defender decisions
evaluator_agent/       Defense scoring and leak/honeytoken evaluation
learning_agent/        Pattern extraction and defender rule generation
llm/                   Ollama HTTP client and prompt templates
memory/                SQLite schema, structured memory, vector memory stub, company data store
orchestration/         DefenseGraph pipeline and state dataclasses
reports/               Optional PowerPoint/report generation scripts
screenshots/           UI and presentation image assets
tests/                 End-to-end pytest suite
ui/                    Streamlit sections, styling, components, and dashboards
utils/                 Chatbot engine, seed loading, safe text, adapters
visualizations/        Plotly charts and HTML diagrams
```

Top-level entry points:

- `streamlit_app.py`: Streamlit web app.
- `run_e2e_demo.py`: full command-line demo.
- `check_system.py`: environment and component health check.
- `tests/test_end_to_end.py`: automated E2E tests.
- `data/seeds/generate_seeds.py`: combines configured attack seed sources.
- `reports/generate_project_pptx.py`: generates image-based PPTX.
- `reports/generate_editable_project_pptx.py`: generates editable PPTX.
- `reports/generate_teacher_structure_pptx.py`: generates teacher/presentation structure deck.
- `setup_agents.py`: older/scaffold-style agent setup script retained in the repo.

## Requirements

### System Requirements

- Python 3.8 or newer.
- Ollama installed and running for full LLM behavior.
- SQLite support, included with standard Python.

### Ollama Model

Default model:

```bash
qwen2.5:14b-instruct-q4_K_M
```

Install and start Ollama:

```bash
ollama pull qwen2.5:14b-instruct-q4_K_M
ollama serve
```

The app reads:

- `OLLAMA_HOST`, default `http://127.0.0.1:11434`
- `OLLAMA_MODEL`, default `qwen2.5:14b-instruct-q4_K_M`

Example:

```bash
export OLLAMA_HOST=http://127.0.0.1:11434
export OLLAMA_MODEL=qwen2.5:14b-instruct-q4_K_M
```

### Python Dependencies

Install declared project dependencies:

```bash
pip install -r requirements.txt
```

`requirements.txt` currently declares:

- `streamlit`
- `pandas`
- `pyarrow`
- `numpy`
- `plotly`
- `requests`
- `datasets`

Additional tools used by repo scripts but not declared in `requirements.txt`:

- `pytest` for `tests/test_end_to_end.py`
- `Pillow` for report generation scripts in `reports/`

Install them when needed:

```bash
pip install pytest pillow
```

## Quick Start

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
pip install pytest pillow
```

3. Start Ollama in another terminal:

```bash
ollama serve
```

4. Pull the default model if it is not already available:

```bash
ollama pull qwen2.5:14b-instruct-q4_K_M
```

5. Check the system:

```bash
python check_system.py
```

6. Run the Streamlit UI:

```bash
streamlit run streamlit_app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Running the Demo

Run the end-to-end terminal demo:

```bash
python run_e2e_demo.py
```

The demo covers:

- Benign request passing.
- Protection mode blocking data exfiltration.
- Controlled exfiltration first attempt with monitoring.
- Repeat attempt blocked through learned memory.
- Persistence across a new graph instance.
- Prompt injection redacted pattern blocking.
- Jailbreak redacted pattern blocking.
- Metrics computed from real SQLite rows.

The demo writes its latest output to:

```text
data/last_demo_results.json
```

## Running Tests

```bash
pytest tests/test_end_to_end.py -v -s
```

The tests require Ollama to be reachable. If Ollama is not running, the test fixture skips the suite.

## Streamlit UI

Start the app:

```bash
streamlit run streamlit_app.py
```

Pages:

- `Overview`: project overview, agents, loop, architecture, and final section.
- `Chatbot Arena`: interactive chat, manual safe test buttons, live traces, mode selector, Ollama status.
- `Results`: latest trace, database rows, loaded attack seeds, memory, evidence, simulation, and evaluation metrics.

Useful UI actions:

- Switch between `PROTECTION` and `CONTROLLED_EXFILTRATION`.
- Send a custom prompt.
- Run manual tests from `data/chatbot_demo_policy.json`.
- Run the live defense sequence to show learning before and after repeated patterns.
- Reset learned memory.
- Export a trace JSON from the results page.

## Modes

### `PROTECTION`

Default mode. The defender blocks detected unsafe requests, including synthetic data exfiltration, prompt injection, and jailbreak-style attempts.

### `CONTROLLED_EXFILTRATION`

Demonstration mode. Unknown synthetic exfiltration patterns can be allowed with monitoring so the evaluator can mark the leak and the learning agent can save a pattern/rule. A repeat of the same learned pattern should then be blocked.

## SQLite Memory

Default database:

```text
data/defense_lab.db
```

The database is created automatically by `memory/structured_memory.py`.

Tables:

- `interactions`: every processed input and resulting decision.
- `learned_patterns`: abstract learned attack patterns.
- `defender_rules`: generated rules created from learned patterns.
- `evaluator_results`: detailed scoring rows.
- `rag_events`: pattern/rule/company data retrieval events.
- `metrics_history`: aggregate metrics schema.

Inspect manually:

```bash
sqlite3 data/defense_lab.db "SELECT COUNT(*) FROM interactions;"
sqlite3 data/defense_lab.db "SELECT * FROM learned_patterns;"
sqlite3 data/defense_lab.db "SELECT * FROM defender_rules;"
sqlite3 data/defense_lab.db "SELECT * FROM rag_events ORDER BY timestamp DESC LIMIT 5;"
```

Reset learned patterns and defender rules from Python:

```python
from memory.structured_memory import StructuredMemory

memory = StructuredMemory()
memory.clear_learned_memory()
```

## Data and Policies

Main policy/data files:

- `data/chatbot_policy.json`
- `data/chatbot_demo_policy.json`
- `data/company_data_policy.json`
- `data/defender_policy.json`
- `data/evaluator_policy.json`
- `data/learning_policy.json`
- `data/safe_text_policy.json`
- `data/attack_seed_policy.json`
- `data/mock_company_data.csv`
- `data/mock_company_data.json`

Attack seed files:

- `data/seeds/unified_attack_seeds.json`
- `data/seeds/hackaprompt_seeds.json`
- `data/seeds/advbench_huggingface_seeds.json`
- `data/seeds/jailbreakbench_seeds.json`
- `data/seeds/JailBreakV_28K.csv`
- `data/seeds/advbench/harmful_behaviors.csv`
- `data/seeds/advbench/harmful_strings.csv`

`data/attack_seed_policy.json` also references `data/seeds/hackaprompt.parquet`; if that file is absent, the loader skips it and falls back to other configured JSON/CSV/fallback seeds.

Generate a combined seed JSON:

```bash
python data/seeds/generate_seeds.py
```

This writes:

```text
data/seeds/unified_attack_seeds.generated.json
```

## Environment Variables

Policy paths can be overridden:

- `ATTACK_SEED_POLICY_PATH`
- `CHATBOT_DEMO_POLICY_PATH`
- `CHATBOT_POLICY_PATH`
- `COMPANY_DATA_POLICY_PATH`
- `DEFENDER_POLICY_PATH`
- `EVALUATOR_POLICY_PATH`
- `LEARNING_POLICY_PATH`
- `SAFE_TEXT_POLICY_PATH`

Other configuration:

- `ATTACK_SEED_LIMIT_PER_FILE`: max rows loaded per structured attack seed file.
- `OLLAMA_HOST`: Ollama host URL.
- `OLLAMA_MODEL`: Ollama model name.

## Reports and Presentation Decks

Optional report scripts use assets from `screenshots/` and write output to `reports/`.

```bash
python reports/generate_project_pptx.py
python reports/generate_editable_project_pptx.py
python reports/generate_teacher_structure_pptx.py
```

These scripts require `Pillow`. The editable deck script builds PPTX XML directly with the Python standard library plus Pillow image inspection.

## Troubleshooting

### Ollama is offline

Check:

```bash
ollama serve
ollama list
ollama pull qwen2.5:14b-instruct-q4_K_M
```

Then run:

```bash
python check_system.py
```

### Model is missing

The UI and `LLMClient.health()` distinguish server availability from model availability. Pull the configured model:

```bash
ollama pull qwen2.5:14b-instruct-q4_K_M
```

### Database is locked

Close other SQLite clients or stop other running app instances. If this is only a local demo and you want a clean state, remove `data/defense_lab.db` and rerun the app or demo.

### No learned patterns appear

Use `CONTROLLED_EXFILTRATION` mode and run a synthetic exfiltration scenario. Learning happens when the evaluator marks an attack as successful and the learner extracts a pattern.

### Tests skip

Start Ollama and make sure the configured model is visible:

```bash
ollama serve
ollama list
```

## Development Notes

- Most application behavior is policy-driven through JSON files in `data/`.
- The pipeline entry point for programmatic use is `DefenseGraph`.
- The Streamlit UI uses helper functions from `utils/chatbot_engine.py`.
- `llm/client.py` calls Ollama with the HTTP API through `requests`; it does not use the Python `ollama` package.
- Runtime database state is local and generated. Do not treat `data/defense_lab.db` as source data.

Example programmatic call:

```python
from orchestration.graph import DefenseGraph
from memory.structured_memory import StructuredMemory

memory = StructuredMemory()
graph = DefenseGraph(structured_memory=memory, mode="PROTECTION")
result = graph.process_user_message("Explain prompt injection at a high level.")

print(result["defender"]["action"])
print(result["assistant_response"])
```

## License and Use

This is a research and demonstration system for defensive AI security education. Use it responsibly with synthetic data and safe redacted test patterns.
