# AI_README.md  

*A contract for autonomous agents (Cursor MCP, OpenAI-agents, Copilot, etc.) that read or write code in this repository.*

---

## 0 · TL;DR for Agents

1. **NEVER** grow a file beyond **200 LOC** (excluding comments, type stubs, tests).  
2. **NEVER** edit two concerns in one PR; one file → one logical change.  
3. **ALWAYS** add/adjust unit tests for every public function or class you touch.  
4. Construct **agents, tools, registries, runners, memory providers** through the *factories*—*never* via `Agent(...)` directly.  
5. Keep domain logic in **engine/**; push I/O or frameworks to **storage/** or **ui/**.  
6. Append uncertainties to **open_questions.txt** instead of guessing. Create the file if doesn't exist.
7. **Avoid duplicate and orphan code**. Check whether a function or file with the same scope exists under a similar name before creating it.
8. **Maintain** accurate documentation by updating existing .md files or creating new documentation in /docs when necessary.
9. Create, update, and maintain an accurate **directory_structure.txt** after making changes.

---

## 1 · Layer Cheat-Sheet

| Layer | Folder | Allowed Content | Forbidden Content |
|-------|--------|-----------------|-------------------|
| **Config** | `src/project_name/config/` | Pydantic `BaseSettings`, env parsing | Business logic, network I/O |
| **Engine** | `src/project_name/engine/` | Pure domain: factories, hooks, runner abstraction | HTTP, DB calls |
| **Tools** | `src/project_name/tools/` | `@function_tool` callables | Long computations, storage |
| **Storage** | `src/project_name/storage/` | `Registry` & `MemoryProvider` implementations | UI handlers |
| **Tasks** | `src/project_name/tasks/` | In-proc async job runner, sched adapters | Web code |
| **Plugins** | `src/project_name/plugins/` | 3rd-party extensions (`PluginProtocol`) | Core edits |
| **UI** | `src/project_name/ui/` | `api/` (FastAPI) + `streamlit_app/` | Engine logic |
| **Util** | `src/project_name/util/` | Logging, shared typing helpers | Heavy deps |
| **Frontend** | `frontend/` | React/Next.js + Tailwind (TypeScript) | Python |
| **Deploy** | `deploy/` | Dockerfile, GH Actions, cloud stubs | Source code |
| **Docs / Examples** | `docs/`, `examples/` | MkDocs pages, runnable demos | Production code |
| **Tests** | `tests/` | `unit/`, `integration/`, `e2e/` | App source |

---

## 2 · Factory Catalog

| Factory | Import Path | Purpose | Typical Call |
|---------|-------------|---------|--------------|
| `agent_factory` | `project_name.engine.factory` | Create & register `Agent` with default hooks | `agent_factory("sql_expert", tools=[query_tool])` |
| `tool_factory` | `project_name.tools` | Turn callable → OpenAI Function Tool | `tool_factory(fn, name="search")` |
| `registry_factory` | `project_name.storage` | Singleton registry (file / Redis / Supabase / vector) | `registry_factory()` |
| `runner_factory` | `project_name.engine.runner` | Wrap `Runner` (sync ⬌ stream) + observability | `runner_factory(stream=True)` |
| `memory_provider_factory` | `project_name.storage` | Pluggable vector/key-value memory backend | `memory_provider_factory("pinecone")` |

*Rule:* **Always** use these factories; do **not** instantiate classes directly.

---

## 3 · Coding Standards

```text
✓ Black + Ruff enforced by pre-commit
✓ Mypy strict (no implicit Any)
✓ One public entity per file when possible
✓ Async I/O only (httpx, aioredis) in storage/ui
✓ Docstrings: Google style

✗ No secrets in code (use env / config)
✗ No synchronous network calls in engine/
✗ No circular imports (run `pipdeptree`)
```

---

## 4 · Testing Matrix

| Folder | Scope | Marker | CI Policy |
|--------|-------|--------|-----------|
| `tests/unit/` | Pure Python, < 250 ms | *(none)* | Run on every PR |
| `tests/integration/` | Hits Redis / file / vector mocks | `@pytest.mark.integration` | Run on every PR |
| `tests/e2e/` | Docker Compose + live API | `@pytest.mark.e2e` | Nightly on *main* |

---

## 5 · Plugin Protocol (v0.1)

```python
from typing import Callable, Protocol, List
from project_name.engine import Agent

class PluginProtocol(Protocol):
    name: str
    tools: List[Callable]            # @function_tool decorated
    agents: List[Agent] | None       # optional canned agents
```

Register via:

```python
from project_name.plugins.registry import register_plugin
register_plugin(MyPlugin)
```

Plugins live in `project_name/plugins/` **or** expose an entry-point group `project_name.plugins`.

---

## 6 · Where to Place New Things

| Need | Folder | Steps |
|------|--------|-------|
| New tool | `tools/` | One <200 LOC file, add to `__all__`, tests |
| New storage backend | `storage/{name}_backend.py` | Implement interface, update `storage.__init__`, tests |
| Background job | `tasks/` | Add function + schedule; mark integration test |
| Middleware | `ui/api/middleware/` | Subclass `BaseHTTPMiddleware`; register in `fastapi_app.py` |
| New agent profile | Use `agent_factory` in engine code | Unit test under `tests/unit/` |

---

## 7 · Open Questions

*(append below; keep chronological).*

---

## 8 · Versioning & Branches

* `main` — always deployable  
* `dev/*` — feature branches  
* Tags `vX.Y.Z` — semantic version releases after CI green + smoke test

---

### Remember  
>
> **Small, typed, tested PRs keep humans happy and the CI green.**  
> If uncertain, leave a note in *Open Questions* instead of guessing.
