# PRISMAgent Issues Catalog

This document provides a detailed inventory of known issues in the PRISMAgent codebase, categorized by type and severity. Use this as a reference when planning development work.

## Critical Issues (Blocking Functionality)

### C1: Missing Tool Factory Implementation
- **Description**: The code references `tool_factory` but the implementation doesn't exist
- **Files**: 
  - `src/PRISMAgent/engine/factory.py` (references the function)
  - `src/PRISMAgent/tools/__init__.py` (should export the function)
- **Impact**: Prevents tool creation, breaking core functionality
- **Solution**: Create a new file `src/PRISMAgent/tools/factory.py` that implements the tool factory
- **Status**: FIXED in PR #1 - Added proper tool_factory implementation and exports

### C2: Parameter Mismatches
- **Description**: Function signatures don't match their call sites
- **Files**:
  - `src/PRISMAgent/tools/spawn.py` (passes parameters not declared in factory.py)
  - `src/PRISMAgent/ui/streamlit_app/main.py` (passes mismatched parameters)
- **Impact**: Runtime errors or incorrect behavior
- **Solution**: Audit all function calls and align signatures
- **Status**: FIXED in PR - Added proper parameter handling in spawn_agent to accept both string tool names and callable tools

### C3: Incomplete Storage Registry
- **Description**: Storage registry is incomplete and references backends that don't exist
- **Files**: 
  - `src/PRISMAgent/storage/__init__.py`
  - `src/PRISMAgent/storage/base.py`
- **Impact**: Storage functionality fails or uses incorrect backend
- **Solution**: Complete the registry implementation and ensure backends exist

### C4: Missing Async Implementation
- **Description**: FastAPI endpoints use async but storage backends are often synchronous
- **Files**: 
  - `src/PRISMAgent/ui/api/routers/chat.py`
  - `src/PRISMAgent/storage/file_backend.py`
- **Impact**: Blocking I/O in async context, performance issues
- **Solution**: Implement proper async patterns throughout storage backends

## Major Issues (Limited Functionality)

### M1: Unimplemented Chat History
- **Description**: Chat history endpoints return empty arrays
- **Files**: `src/PRISMAgent/ui/api/routers/chat.py`
- **Impact**: Chat history features don't work
- **Solution**: Implement chat history storage and retrieval

### M2: Incomplete Vector Storage
- **Description**: Vector storage references but implementation is incomplete
- **Files**: 
  - `src/PRISMAgent/storage/vector_backend.py`
  - `src/PRISMAgent/storage/vector_store.py`
- **Impact**: Vector search capabilities don't work
- **Solution**: Complete vector storage implementation

### M3: Missing Plugin System
- **Description**: Plugin system mentioned in documentation but not implemented
- **Impact**: No plugin extensibility
- **Solution**: Create plugin registry and discovery mechanism

### M4: Missing Tasks Module
- **Description**: Tasks module mentioned in documentation but doesn't exist
- **Impact**: No background task execution
- **Solution**: Implement tasks module and scheduling

## Minor Issues (Nuisances)

### N1: Documentation Inconsistencies
- **Description**: Documentation describes features that aren't implemented
- **Files**: `README.md`, `AI_README.md`
- **Impact**: User confusion
- **Solution**: Update documentation to reflect current state

### N2: Unclear Error Messages
- **Description**: Error handling is minimal with generic messages
- **Files**: Various
- **Impact**: Difficult debugging
- **Solution**: Improve error handling with specific messages

### N3: Hardcoded Configuration
- **Description**: Many settings are hardcoded rather than configurable
- **Files**: Various
- **Impact**: Limited flexibility
- **Solution**: Move settings to configuration

## Testing Gaps

### T1: Missing Engine Tests
- **Description**: Engine module lacks comprehensive tests
- **Files**: `tests/unit/test_factory.py` (incomplete)
- **Impact**: Regressions not caught
- **Solution**: Add tests for all engine components

### T2: Missing Storage Tests
- **Description**: Storage backends lack tests
- **Files**: No test files for storage
- **Impact**: Storage functionality unreliable
- **Solution**: Add tests for all storage backends

### T3: Missing API Tests
- **Description**: API endpoints lack tests
- **Files**: No test files for API
- **Impact**: API changes may break clients
- **Solution**: Add tests for all API endpoints

## Feature Requests (Future Work)

### F1: Multiple LLM Provider Support
- **Description**: Support for providers beyond OpenAI
- **Priority**: Medium
- **Complexity**: High

### F2: Enhanced Monitoring
- **Description**: Add telemetry and monitoring for agents
- **Priority**: Medium
- **Complexity**: Medium

### F3: Web-based Admin UI
- **Description**: More sophisticated UI beyond Streamlit
- **Priority**: Low
- **Complexity**: High

## Action Item Tracking

| ID | Assigned To | Status | Started | Completed | Notes |
|----|-------------|--------|---------|-----------|-------|
| C1 | | Completed | | ✅ | Fixed in PR #1 |
| C2 | | Completed | | ✅ | Fixed parameter handling in spawn_agent |
| C3 | | Not Started | | | |
| C4 | | Not Started | | | |
| M1 | | Not Started | | | |
| M2 | | Not Started | | | |
| M3 | | Not Started | | | |
| M4 | | Not Started | | | |

---

This document will be updated as issues are resolved and new ones are discovered.