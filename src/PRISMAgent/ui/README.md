# PRISMAgent User Interfaces

This directory contains the various user interfaces for PRISMAgent:

- `streamlit_app/` - Streamlit-based web interface for development and prototyping
- `api/` - FastAPI-based REST API for production use

## Streamlit App

The Streamlit app provides a user-friendly web interface for interacting with PRISMAgent. It allows you to:

- Configure and create different agent types
- Interact with agents via a chat interface
- Use specialized tools like code execution and web search
- Manage multiple agents in a single session

### Running the Streamlit App

To run the Streamlit app:

```bash
# From the project root
streamlit run src/PRISMAgent/ui/streamlit_app/main.py
```

This will start the Streamlit server and open the interface in your browser at http://localhost:8501.

### Features

- **Agent Configuration**: Create different agent types with specialized capabilities
- **Multi-agent Management**: Create and switch between different agents
- **Tool Integration**: Use tools like code execution, web search, and agent spawning
- **Chat History**: Maintain conversation history with each agent
- **Streaming Responses**: Get real-time feedback as agents respond

### Required Environment Variables

Make sure you have the following environment variables set in your `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `SEARCH_API_KEY`: API key for web search functionality (optional)

See the [main documentation](../../README.md) for more details on configuration options.

## API Interface

The API interface is a RESTful API built with FastAPI that provides programmatic access to PRISMAgent functionality. This is ideal for integrating PRISMAgent with other applications or building custom frontends.

### Running the API

To run the API server:

```bash
# From the project root
uvicorn PRISMAgent.ui.api.fastapi_app:app --reload --port 8000
```

The API will be accessible at http://localhost:8000, with documentation at http://localhost:8000/docs.

### API Endpoints

The API provides the following key endpoints:

- `/agents` - Manage agent creation and configuration
- `/chat` - Send messages and receive responses from agents
- `/tools` - List and manage available tools
- `/memory` - Access and manage agent memory

For detailed API documentation, see the OpenAPI docs at `/docs` when the server is running.

## Best Practices for UI Development

When developing or extending the UIs:

1. Keep UI code separate from business logic
2. Follow the repository's code style guidelines
3. Write unit tests for new functionality
4. Document new features in the appropriate README files
5. Use the factory pattern for creating agents and runners
6. Maintain separation of concerns between UI and domain logic

## Architecture

```
ui/
├── __init__.py          # Package initialization
├── README.md            # This documentation
├── api/                 # FastAPI REST interface
│   ├── __init__.py
│   ├── fastapi_app.py   # Main API entry point
│   ├── routers/         # API route handlers
│   ├── middleware/      # API middleware
│   └── models/          # API request/response models
└── streamlit_app/       # Streamlit web interface
    ├── main.py          # Main Streamlit app
    ├── style.css        # Custom styling
    └── README.md        # Streamlit-specific documentation
```

Each interface is designed to be independent, allowing for flexibility in deployment and development while sharing the core PRISMAgent engine and tools.
