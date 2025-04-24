# PRISMAgent Core Package

This document provides details for AI assistants on the core package structure.

## Package Organization

The PRISMAgent package follows a modular design with clear separation of concerns:

- `config/`: Configuration models using Pydantic
- `engine/`: Core domain logic with no I/O dependencies
- `tools/`: OpenAI function tools for agent capabilities
- `storage/`: Pluggable backends for persistence (file, Redis, Supabase, vector)
- `tasks/`: Lightweight asynchronous task management
- `plugins/`: Extensibility system
- `ui/`: User interfaces (FastAPI and Streamlit)
- `util/`: Cross-cutting utilities

## Design Guidelines

1. Each module should have minimal dependencies on other modules
2. The engine module contains domain logic and should not have I/O dependencies
3. Storage adapters implement common interfaces defined in `storage/base.py`
4. Optional functionality should be implemented via the plugin system
5. UI layers should depend on the engine and storage, but not vice versa

## Development Practices

- Use type hints consistently throughout the codebase
- Follow the existing patterns for dependency injection
- Keep modules focused on a single responsibility
- Use protocols for interface definitions
- Add comprehensive docstrings for all public APIs
