# Architecture Overview

PRISMAgent follows a clean architecture approach, with clear separation between the domain logic and I/O components.

## Key Components

```text
PRISMAgent/
│
├─ config/           # All runtime config objects (Pydantic)
├─ engine/           # Domain logic (no I/O)
├─ tools/            # OpenAI function tools
├─ storage/          # Persistence back-ends (pluggable)
├─ tasks/            # Lightweight task runner (async, in-proc)
├─ plugins/          # First-class plug-in system
├─ ui/               # Python-native user interfaces
└─ util/             # Cross-cutting helpers
```

## Component Details

### Config

Manages all runtime configurations using Pydantic models:

- **BaseSettings**: Core settings with environment variable precedence
- **Model Config**: OpenAI model settings and cost caps
- **Storage Config**: Configuration for selected storage backend

### Engine

Contains the core domain logic with no direct I/O dependencies:

- **Factory**: Creates and configures agents
- **Hooks**: Dynamic handoff mechanisms between agents
- **Runner**: Executes agent workflows (both sync and streaming)

### Tools

OpenAI function tools that can be used by agents:

- **Spawn Agent Tool**: Allows agents to spawn other agents
- **Web Search**: Example additional tool

### Storage

Pluggable storage backends for persistence:

- **Base**: Registry and Memory Provider protocols
- **Implementations**: File, Redis, Supabase, and vector store options

### Tasks

Lightweight asynchronous task management:

- **Runner**: Executes tasks asynchronously
- **Scheduler**: Simple interval-based scheduler

### Plugins

Extensibility system for adding functionality:

- **Registry**: Discovers and loads plugins
- **Plugin Protocol**: Interface for implementing plugins

### UI

Dual user interface approach:

- **FastAPI**: Production-ready API
- **Streamlit**: Development dashboard

## Interaction Flow

1. Configuration is loaded via the Config module
2. Engine Factory creates agents based on configuration
3. Agents use Tools to perform actions
4. Engine Runner executes agent workflows
5. Storage module persists agent state
6. UI layer provides access to the system
7. Tasks module handles async operations
8. Plugins extend functionality as needed
