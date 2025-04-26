# PRISMAgent Streamlit UI

This is the web interface for interacting with PRISMAgent, a modular, multi-agent framework with plug-and-play storage, tools, and UIs.

## Features

- **Create and Configure Agents**: Define different agent types with specific tools and capabilities
- **Agent Management**: Create multiple agents and switch between them
- **Chat Interface**: Interact with agents through a familiar chat interface
- **Tool Integration**: Use specialized tools like code execution, web search, and agent spawning
- **Streaming Responses**: Get real-time feedback as agents think and respond
- **Chat History**: Maintain conversation history with each agent

## Quick Start

1. Ensure you have PRISMAgent installed and configured
2. Set the required environment variables (see `.env.example`)
3. Run the Streamlit app:

```bash
cd /path/to/prism_agent
streamlit run src/PRISMAgent/ui/streamlit_app/main.py
```

## Agent Types

The UI supports several preconfigured agent types:

- **Assistant**: General-purpose helpful assistant
- **Coder**: Programming specialist with code execution capabilities
- **Researcher**: Information gathering specialist with web search capabilities
- **Custom**: Define your own agent with a custom system prompt and tools

## Available Tools

- **spawn_agent**: Create specialized sub-agents for specific tasks
- **code_interpreter**: Execute Python code in a sandboxed environment
- **web_search**: Search the web for information
- **fetch_url**: Retrieve content from specific URLs

## Usage Guide

### Creating an Agent

1. Select an agent type from the dropdown in the sidebar
2. Customize the system prompt if desired
3. Select which tools the agent should have access to
4. Configure advanced settings if needed
5. Click "Create/Update Agent"

### Interacting with Agents

1. Type a message in the chat input field
2. The agent will respond, potentially using its available tools
3. Continue the conversation as needed

### Managing Multiple Agents

1. Create multiple agents using the configuration panel
2. Switch between agents using the "Active Agent" dropdown
3. Each agent maintains its own conversation history

### Configuration Options

- **Stream Output**: Enable or disable streaming responses (real-time output)
- **Max Tools Per Run**: Limit the number of tool calls per request
- **Memory Provider**: Select how agent memory is stored

## Environment Variables

Key environment variables for the UI:

- `OPENAI_API_KEY`: Required for LLM functionality
- `SEARCH_API_KEY`: Required for web search tools
- `DEFAULT_MODEL`: The OpenAI model to use (default: gpt-4o)
- `MODEL_TEMPERATURE`: Controls response randomness (default: 0.7)
- `MODEL_MAX_TOKENS`: Maximum tokens in responses (default: 1000)

## Troubleshooting

- **API Key Issues**: Ensure both OpenAI and search API keys are set in your environment
- **Tool Errors**: Check that required dependencies are installed for all tools
- **Memory Issues**: Configure appropriate storage backends based on your needs

## Contributing

See the main PRISMAgent repository for contribution guidelines.
