# API Reference

This section provides detailed documentation for the PRISMAgent API.

## Package Structure

The PRISMAgent package is organized into the following modules:

- **Config**: Configuration models for runtime settings
- **Engine**: Core domain logic for agent management
- **Tools**: OpenAI function tools
- **Storage**: Persistence backends
- **Tasks**: Asynchronous task management
- **Plugins**: Extensibility system
- **UI**: User interfaces

## Module Documentation

Each module is documented separately:

- [Engine](engine.md): Core agent creation and execution logic
- [Tools](tools.md): Function tools for agent capabilities
- [Storage](storage.md): Data persistence interfaces and implementations

## Using the API

Here's a simple example of using the PRISMAgent API:

```python
from PRISMAgent.config.base import BaseSettings
from PRISMAgent.engine.factory import agent_factory
from PRISMAgent.engine.runner import runner_factory
from PRISMAgent.storage.file_backend import FileStorageBackend

# Create configuration
config = BaseSettings(
    api_key="your-openai-api-key",
    model_name="gpt-4",
    max_tokens=1000,
)

# Initialize storage
storage = FileStorageBackend(data_dir="./data")

# Create an agent
agent = agent_factory(
    config=config,
    storage=storage,
    system_prompt="You are a helpful assistant.",
    tools=[],
)

# Create a runner
runner = runner_factory(streaming=True)

# Use the agent
response = await runner.run(
    agent=agent,
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
