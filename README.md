# PRISMAgent 🚀

*A modular, multi-agent framework with plug-and-play storage, tools, and UIs.*

---

## 1 · Why this repo exists

1. **Rapid prototyping** – Spin up Streamlit + file-based storage in minutes.  
2. **Future-proof** – Add Redis, Supabase (Postgres), Pinecone/Qdrant, Celery/Arq, or a React + Tailwind front-end **without refactoring core code**.  
3. **AI-first extensibility** – Agents, tools, tasks, and even third-party plug-ins are created at runtime through factories; the directory layout simply keeps them discoverable.

---

## 2 · High-level architecture

| Layer | Folder | Purpose |
|-------|--------|---------|
| **Config** | `src/project_name/config/` | Single source of truth (Pydantic Settings) for models, storage, env flags. |
| **Engine** | `src/project_name/engine/` | Pure domain logic: `agent_factory`, `runner`, OpenAI Agents hooks. |
| **Tools** | `src/project_name/tools/` | Function tools exposed to LLMs (`spawn_agent`, `web_search`, …). |
| **Storage** | `src/project_name/storage/` | File/Redis/Supabase/Pinecone back-ends behind one interface. |
| **Tasks** | `src/project_name/tasks/` | In-process async task runner; adapters ready for Celery / Arq. |
| **UI** | `src/project_name/ui/` | `streamlit_app/` for dev; `api/` (FastAPI + middleware) for prod. |
| **Plugins** | `src/project_name/plugins/` | Third-party extensions auto-discovered at startup. |
| **Frontend** | `frontend/` | Future Next.js + Tailwind SPA (optional). |
| **Deploy** | `deploy/` | Dockerfile, Compose, CI stub, cloud templates. |
| **Docs** | `docs/`, `mkdocs.yml` | MkDocs site; build with `mkdocs serve`. |
| **Tests** | `tests/` | `unit/`, `integration/`, `e2e/` + shared fixtures. |

---

## 3 · Quick start (local dev)

```bash
# 0) prerequisites
#    - Python 3.11+
#    - Docker Desktop (optional but recommended)
#    - (Mac/Win users) Cursor IDE or VS Code

git clone https://github.com/your-org/project_name.git
cd project_name
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"      # installs main + dev extras (ruff, pytest, etc.)

# 1) run Streamlit prototype
streamlit run src/project_name/ui/streamlit_app/main.py
# open http://localhost:8501

# 2) run FastAPI (for React/mobile)
uvicorn project_name.ui.api.fastapi_app:app --reload --port 8000
# open http://localhost:8000/docs

# 3) run unit tests
pytest -m "unit"
```

### Docker one-liner

```bash
docker compose -f deploy/docker-compose.yml up --build
# API on :8000, Streamlit on :8501, Redis mock on :6379
```

---

## 4 · Configuring storage back-ends

Edit **`src/project_name/config/storage.py`** or set env vars:

```bash
# File-based (default)
export STORAGE_BACKEND=file
# Redis
export STORAGE_BACKEND=redis
export REDIS_URL=redis://localhost:6379/0
# Supabase (Postgres)
export STORAGE_BACKEND=supabase
export SUPABASE_URL=https://xyz.supabase.co
export SUPABASE_KEY=your_service_key
# Pinecone / Qdrant
export STORAGE_BACKEND=vector
export VECTOR_PROVIDER=pinecone
export PINECONE_API_KEY=...
```

The application swaps implementations at runtime—no code changes.

---

## 5 · Adding your own pieces

### ➤ New tool
```python
# src/project_name/tools/greet.py
from agents import function_tool

@function_tool
def greet(name: str) -> str:
    return f"Hello, {name}!"
```
The `agent_factory` auto-discovers it (or list it explicitly).

### ➤ New plug-in
```python
# my_plugin/__init__.py
from project_name.plugins.registry import register_plugin

@register_plugin
class JokePlugin:
    name = "joke_plugin"
    tools = ["tell_joke"]
```
Copy into `plugins/` or `pip install my_plugin`; it shows up next launch.

### ➤ Background task
```python
from project_name.tasks.runner import run_task

async def nightly_cleanup():
    ...

run_task(nightly_cleanup, schedule="0 3 * * *")  # cron, in-process
```

---

## 6 · Deployment cheat-sheet

| Scenario | Command |
|----------|---------|
| Local dev containers | `docker compose up --build` |
| GitHub Actions CI | Push → `.github/workflows/ci.yml` runs tests + builds image |
| Cloud Run (GCP) | `gcloud run deploy --source .` |
| AWS ECS Fargate | Edit `deploy/cloud/aws/ecs-taskdef.json` → `aws ecs register-task-definition` |
| Azure Container Apps | `az containerapp up --source .` |

*All cloud manifests are placeholders—swap IDs/regions, then commit.*

---

## 7 · Testing matrix

```text
tests/
├─ unit/          # pure Python, no I/O
├─ integration/   # hits Redis / vector mocks
└─ e2e/           # spins Docker Compose, calls live REST endpoints
```
Run all in CI (`pytest -m "not slow"`).  
Mark slow or external tests with `@pytest.mark.integration` or `@pytest.mark.e2e`.

---

## 8 · Contributing

1. Fork + feature branch  
2. `pre-commit install` (Black, Ruff, Mypy run auto)  
3. Add or update tests—coverage must not drop  
4. Open PR → CI must pass  
5. One maintainer review + squash merge

---

## 9 · Roadmap

- [ ] Auth + rate-limit middleware  
- [ ] Vector memory RAG integration  
- [ ] React/Tailwind front-end (Next.js)  
- [ ] Celery/Arq driver in `tasks/`  
- [ ] Helm chart & Terraform modules  

> **Questions?** Open an issue or join the Discord. Happy hacking! 🎉