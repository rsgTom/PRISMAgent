# Engine API

The Engine module contains the core domain logic for the PRISMAgent framework.

## agent_factory

```python
def agent_factory(
    config: BaseSettings,
    storage: Any,
    system_prompt: str,
    tools: Optional[List[Any]] = None,
    **kwargs
) -> Agent:
    """
    Create and configure an agent.
    
    Args:
        config: The configuration settings for the agent
        storage: The storage backend for the agent
        system_prompt: The system prompt for the agent
        tools: Optional list of function tools for the agent
        **kwargs: Additional keyword arguments
        
    Returns:
        An initialized Agent instance
    """
```

## runner_factory

```python
def runner_factory(
    streaming: bool = False,
    hooks: Optional[List[Hook]] = None,
    **kwargs
) -> Runner:
    """
    Create a runner for executing agents.
    
    Args:
        streaming: Whether to use streaming mode
        hooks: Optional list of hooks to use with the runner
        **kwargs: Additional keyword arguments
        
    Returns:
        A Runner instance (either SyncRunner or StreamingRunner)
    """
```

## hook_factory

```python
def hook_factory(
    hook_type: Type[Hook],
    **kwargs
) -> Hook:
    """
    Create a hook for agent interactions.
    
    Args:
        hook_type: The type of hook to create
        **kwargs: Additional configuration for the hook
        
    Returns:
        An initialized Hook instance
    """
```

## DynamicHandoffHook

```python
class DynamicHandoffHook(Hook):
    """
    A hook that allows dynamic handoff between agents.
    
    Methods:
        register_agent(name: str, agent: Agent) -> None:
            Register an agent with the hook
            
        process_message(message: Dict[str, Any]) -> Optional[Agent]:
            Process a message and determine if handoff is needed
            
        handle_handoff(current_agent: Agent, target_agent: Agent, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            Execute a handoff between agents
    """
```

## Classes

### Agent

The base agent class that interacts with language models.

```python
class Agent:
    """
    Agent class that interacts with language models.
    
    Attributes:
        config: The agent's configuration
        storage: The storage backend
        system_prompt: The system prompt for the agent
        tools: List of function tools
        client: The OpenAI client
        
    Methods:
        generate(messages: List[Dict[str, Any]], stream: bool = False) -> Any:
            Generate a response from the language model
            
        execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
            Execute a tool by name with the provided arguments
    """
```

### Runner

Base class for agent execution.

```python
class Runner:
    """
    Base class for agent execution.
    
    Methods:
        run(agent: Agent, messages: List[Dict[str, Any]], **kwargs) -> Any:
            Run the agent with the provided messages
    """
``` 