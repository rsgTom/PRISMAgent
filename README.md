# PRISMAgent 🚀

*A modular, multi-agent framework with plug-and-play storage, tools, and UIs.*

---

## 1 · Why this repo exists

1. **Rapid prototyping** — Spin up Streamlit + file-based storage in minutes.  
2. **Future-proof** — Add Redis, Supabase (Postgres), Pinecone/Qdrant, Celery/Arq, or a React + Tailwind front-end **without refactoring core code**.  
3. **AI-first extensibility** — Agents, tools, tasks, and even third-party plug-ins are created at runtime through factories; the directory layout simply keeps them discoverable.

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
pip install -e ".[dev,env]"  # installs main + dev extras + dotenv

# Create an environment file
cp .env.example .env
# Edit .env with your OpenAI API key and other settings

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

Edit **`.env`** file or set environment variables:

```bash
# File-based (default)
STORAGE_BACKEND=memory
# Redis
STORAGE_BACKEND=redis
REDIS_URL=redis://localhost:6379/0
# Supabase (Postgres)
STORAGE_BACKEND=supabase
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_KEY=your_service_key
# Vector Storage (for embeddings)
VECTOR_PROVIDER=memory     # In-memory (default for development)
VECTOR_PROVIDER=redis      # Redis with RediSearch
VECTOR_PROVIDER=redisvl    # Redis Vector Library
VECTOR_PROVIDER=pinecone   # Pinecone
PINECONE_API_KEY=your_api_key
PINECONE_INDEX=your_index
```

The application swaps implementations at runtime—no code changes.

### Vector Storage

PRISMAgent supports multiple vector database backends for storing and retrieving embeddings:

- **In-memory**: Simple in-memory store for development and testing
- **Redis**: Uses Redis with RediSearch for vector operations
- **RedisVL**: Uses Redis Vector Library for advanced vector capabilities
- **Pinecone**: Uses Pinecone cloud vector database service

Example usage:

```python
from PRISMAgent.storage import VectorStore

# Create a vector store with the configured backend
vector_store = VectorStore()

# Store a vector with metadata
vector_store.upsert("doc-1", embedding_vector, {"text": "Sample document"})

# Query for similar vectors
results = vector_store.query(query_vector, k=5)
```

See the [Vector Storage Documentation](docs/api/storage/vector_storage.md) and [examples](examples/) for more details.

---

## 5 · Environment Variables

PRISMAgent uses environment variables for configuration. You can set these in a `.env` file in the root directory, or by setting them in your environment.

### Creating a .env file

```bash
# Copy the example file
cp .env.example .env

# Edit the file with your settings
nano .env
```

### Required Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key

### Optional Environment Variables

- `DEFAULT_MODEL`: Default model to use (default: "o3-mini")
- `MODEL_TEMPERATURE`: Temperature for model generation (default: 0.7)
- `MODEL_MAX_TOKENS`: Maximum tokens to generate (default: 1000)
- `STORAGE_BACKEND`: Storage backend to use (default: "memory")
- `STORAGE_PATH`: Path for file storage (default: "./data")
- `LOG_LEVEL`: Logging level (default: "INFO")

See `.env.example` for a complete list of available configuration options.

---

## 6 · Adding your own pieces

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

## 7 · Deployment cheat-sheet

| Scenario | Command |
|----------|---------|
| Local dev containers | `docker compose up --build` |
| GitHub Actions CI | Push → `.github/workflows/ci.yml` runs tests + builds image |
| Cloud Run (GCP) | `gcloud run deploy --source .` |
| AWS ECS Fargate | Edit `deploy/cloud/aws/ecs-taskdef.json` → `aws ecs register-task-definition` |
| Azure Container Apps | `az containerapp up --source .` |

*All cloud manifests are placeholders—swap IDs/regions, then commit.*

---

## 8 · Testing matrix

```text
tests/
├── unit/          # pure Python, no I/O
├── integration/   # hits Redis / vector mocks
└── e2e/           # spins Docker Compose, calls live REST endpoints
```

Run all in CI (`pytest -m "not slow"`).  
Mark slow or external tests with `@pytest.mark.integration` or `@pytest.mark.e2e`.

---

## 9 · Contributing

1. Fork + feature branch  
2. `pre-commit install` (Black, Ruff, Mypy run auto)  
3. Add or update tests—coverage must not drop  
4. Open PR → CI must pass  
5. One maintainer review + squash merge

---

## 10 · Roadmap & Project Organization

### Project Organization

We're using GitHub Projects to organize our work. Check out these project boards for current status:

- [PRISMAgent Development Roadmap (#23)](https://github.com/rsgTom/PRISMAgent/issues/23) - Complete overview of all issues and priorities
- [Critical Fixes & Immediate Tasks (#24)](https://github.com/rsgTom/PRISMAgent/issues/24) - Tracking urgent issues needing immediate attention
- [Testing & Quality Improvements (#25)](https://github.com/rsgTom/PRISMAgent/issues/25) - Tracking test coverage and code quality initiatives
- [Feature Development & Enhancements (#26)](https://github.com/rsgTom/PRISMAgent/issues/26) - New features and enhancements on the roadmap

### Roadmap Items

- [ ] Auth + rate-limit middleware  
- [x] Vector memory RAG integration  
- [ ] React/Tailwind front-end (Next.js)  
- [ ] Celery/Arq driver in `tasks/`  
- [ ] Helm chart & Terraform modules  

### Current Priorities

1. **Critical Fixes** - Complete async implementation in storage backends
2. **Core Features** - Implement chat history storage and vector storage
3. **Testing & Quality** - Improve test coverage and implement standard logging
4. **Infrastructure** - Set up CI/CD pipeline with GitHub Actions

> **Questions?** Open an issue or join the Discord. Happy hacking! 👉
