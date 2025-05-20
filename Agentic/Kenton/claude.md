# 🚦 Claude Code – Locked‑Down Engineering Guide (v2025‑05‑17)

## 0. Mission
Build a Deep Research AI agent using the **OpenAI Agents SDK (v1.30+)** and **Responses API**, inspired by OpenAI’s own Deep Research capability. This agent should:
- Take in a high-level research query.
- Autonomously plan, gather, summarize, compare, reflect.
- Output a structured, cited report.

You are a senior, disciplined engineer. Obey all rules below as **hard constraints**.

---

## 1. Workflow ‒ Plan → Confirm → Execute

1. **Explore / Read** – Understand the files/code. Do **not** modify yet.
2. **Plan** – Write your intended actions in markdown (no code yet).
3. Wait for explicit **"OK Claude"** confirmation.
4. **Execute** – Implement **only one plan step**, output as a **unified git diff** (`--- /path/file …`).
5. Repeat steps until complete. Then: `git commit -m "feat: …"`

If requirements are ambiguous, ask before coding.

---

## 2. Output Rules
- **Only emit diffs**, never whole files.
- **Only touch these folders** unless told otherwise:
  - `src/` → Python source code
  - `tools/` → Agent tool functions
  - `tests/` → Unit or system tests
- **Never guess logic or silently rework structure** – always check

---

## 3. Project Overview (Deep Research Agent)

| Component | Description |
|----------|-------------|
| `main.py` | Launches the agent with a sample query |
| `agent_config.py` | Defines Agent: name, instructions, reflection mode |
| `tools/web_search.py` | Tool to retrieve web info via SerpAPI |
| `tools/summarize.py` | Summarizes long text chunks |
| `tools/compare_sources.py` | Identifies discrepancies or cross-verifies claims |
| `tools/report_generator.py` | Builds structured, citation-rich output |
| `tests/` | Simple verification of tool outputs |

---

## 4. Engineering Constraints
- Use `openai` SDK `>=1.30`
- Enable `auto_continue` and `enable_reflection` on Agent
- Load API key from `.env` via `python-dotenv`
- Log tool outputs for tracing
- Use `Runner.run_sync(agent, prompt)` pattern
- Output structured `.md` or `.json` report

## CRITICAL: API INTEGRATION REQUIREMENTS
- **ALWAYS** use the OpenAI SDK for all API integrations
- **NEVER** use Anthropic, Claude, or other LLM providers for any LLM, search, or vector database functionality (external data APIs like weather, news, etc. are fine)
- **ENSURE** all frontend and backend components use exactly the same OpenAI agent configuration
- **MAINTAIN** consistent agent behavior between CLI and web interface
- **VERIFY** that any streaming implementation uses OpenAI's streaming format

### 4.1 Error Handling Guidelines
All tools should implement diagnostic-rich error handling with:

```python
class AgentExecutionError(Exception):
    def __init__(self, message, code=None, hint=None, resolution=None, source=None):
        super().__init__(message)
        self.code = code         # e.g., "FS001" for File Search Error #1
        self.hint = hint         # Explanation of what likely went wrong
        self.resolution = resolution  # How to fix it
        self.source = source     # Where the error occurred
```

### 4.2 Vector Store / File Search Implementation
When using OpenAI Agents SDK for file search:

- Always use `vector_store_ids` as an array: `vector_store_ids=[vector_store_id]`
- For API message attachments to specific files, use `file_id` (singular)
- Never use `file_id: None` - either provide a valid ID or omit the parameter
- Set `OPENAI_VECTOR_STORE_ID` in .env file (not VECTOR_STORE_ID)
- For function tools, implement proper error handling with diagnostic codes

---

## 5. Example Workflow: Phase 1

### Plan
- Set up Poetry or pip + venv
- Install dependencies: `openai`, `httpx`, `python-dotenv`, `requests`
- Create: `src/`, `tools/`, `tests/`, `.env`, `.gitignore`, `main.py`, `agent_config.py`
- Add stub files for each tool

🛑 Await **"OK Claude"** before coding this.

---

