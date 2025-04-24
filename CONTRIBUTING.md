# Contributing to PRISMAgent

Thank you for your interest in contributing to PRISMAgent! This document provides guidelines and workflows to ensure a smooth contribution process.

## Development Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rsgTom/PRISMAgent.git
   cd PRISMAgent
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e ".[dev,env]"  # Installs main + dev extras + dotenv
   ```

4. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Create an environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and other settings
   ```

## Code Style and Quality

PRISMAgent follows strict coding standards to maintain quality and consistency:

1. **Black** for code formatting
2. **Ruff** for linting
3. **Mypy (strict)** for type checking
4. **200 LOC limit** for any single file (excluding comments, docstrings, etc.)
5. **Factory pattern** for creating objects (never instantiate classes directly)

These standards are enforced by pre-commit hooks and CI/CD checks.

## Development Workflow

1. **Choose an issue**
   - Check the [ISSUES.md](ISSUES.md) file for a list of known issues
   - Look at the [Development Plan](DEVELOPMENT_PLAN.md) for priorities

2. **Create a feature branch**
   ```bash
   git checkout -b dev/your-feature-name
   ```

3. **Make changes**
   - Follow the Single Responsibility Principle
   - Keep files under 200 LOC
   - Use factory patterns consistently
   - Add appropriate unit tests

4. **Run tests locally**
   ```bash
   # Run unit tests
   pytest -m "unit"
   
   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=src/PRISMAgent
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "Descriptive message about changes"
   ```
   
   The pre-commit hooks will automatically check formatting, types, etc.

6. **Push changes**
   ```bash
   git push origin dev/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide a clear description of changes
   - Reference the issue number
   - Ensure CI checks pass

## Directory Structure Guidelines

Respect the directory boundaries:

1. **Config (`src/PRISMAgent/config/`)**
   - Pydantic settings models
   - Environment variable parsing
   - No business logic or I/O here

2. **Engine (`src/PRISMAgent/engine/`)**
   - Pure domain logic
   - Factory functions 
   - No direct I/O or network calls

3. **Tools (`src/PRISMAgent/tools/`)**
   - Functions that agents can use
   - Wrapped with `@function_tool` or `tool_factory()`
   - Should be small, focused, and well-documented

4. **Storage (`src/PRISMAgent/storage/`)**
   - Storage backend implementations
   - Keep I/O concerns isolated here
   - Follow async patterns consistently

5. **UI (`src/PRISMAgent/ui/`)**
   - Streamlit UI in `streamlit_app/`
   - FastAPI endpoints in `api/`
   - No business logic here

## Testing Requirements

All code contributions should include appropriate tests:

1. **Unit Tests**
   - Required for all new functionality
   - Focus on testing pure logic in isolation
   - Use mocks for external dependencies
   - Located in `tests/unit/`

2. **Integration Tests**
   - For testing interactions between components
   - May use mocked external services
   - Located in `tests/integration/`

3. **End-to-end Tests**
   - For testing complete workflows
   - Located in `tests/e2e/`

## Documenting Changes

Ensure your changes are properly documented:

1. **Update docstrings** for all new functions/classes
2. **Add examples** where appropriate
3. **Update README.md** for user-facing changes
4. **Add to CHANGELOG.md** for significant changes

## Fixing Critical Issues

When addressing the highest priority issues:

1. **Parameter Mismatches**
   - Use the `dev_tooling/parameter_audit.py` script to identify issues
   - Ensure you understand the intended behavior before fixing
   - Update all call sites to match function signatures

2. **Missing Implementations**
   - For missing functions like `tool_factory`, implement core functionality first
   - Follow existing patterns in the codebase
   - Add comprehensive tests

3. **Storage Issues**
   - Start with the in-memory backend
   - Ensure proper async patterns are used
   - Test with the simplest storage scenarios first

## Questions and Help

If you're unsure about anything:

1. Check the `open_questions.txt` file for known uncertainties
2. Add your question to that file if it's not already covered
3. Flag it in your PR or commit message

## Thank You!

Your contributions help make PRISMAgent better. We appreciate your time and effort!