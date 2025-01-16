# Creating a New Agent

This guide walks through the process of creating and configuring a new agent using the provided creation script and making necessary modifications for it to work properly.

## Quick Start

1. Run the agent creation script:

```bash
./create_new_agent.sh
```

2. When prompted, enter your agent name (must start with a letter and can only contain letters, numbers, underscores, and hyphens)

The script will create a new directory structure for your agent with the following files:

```
your_agent_name/
├── __init__.py
├── agent.py
├── config.py
└── tools/
    └── tools.py
```

## Required Modifications

After creating your agent, you'll need to make the following modifications to get it working:

### 1. Configure Agent in src/config.py

Add your agent's configuration to the main config file:

```python
from src.agents.your_agent_name.config import Config as YourAgentConfig

class Config:
    # ... existing config ...

    AGENT_CONFIGS = {
        # ... existing agents ...
        "your_agent_name": YourAgentConfig,
    }
```

### 2. Implement Agent Logic

Modify `your_agent_name/agent.py`:

1. Update the class name and docstring:

```python
class YourAgentNameAgent(AgentCore):
    """Agent for handling specific operations related to your agent's purpose."""
```

2. Add your tools to the `tools_provided` list in `__init__`:

```python
def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
    super().__init__(config, llm, embeddings)
    self.tools_provided = [
        # Add your tool functions here
    ]
    self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)
```

3. Implement custom request processing in `_process_request`:

```python
async def _process_request(self, request: ChatRequest) -> AgentResponse:
    try:
        messages = [
            SystemMessage(content="Your custom system prompt here"),
            HumanMessage(content=request.prompt.content),
        ]

        result = self.tool_bound_llm.invoke(messages)
        return await self._handle_llm_response(result)
    except Exception as e:
        self.logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return AgentResponse.error(error_message=str(e))
```

4. Implement tool execution in `_execute_tool`:

```python
async def _execute_tool(self, func_name: str, args: Dict[str, Any]) -> AgentResponse:
    """Execute the appropriate tool based on function name."""
    tool_map = {
        # Map your tool names to their implementation functions
        "your_tool_name": self._your_tool_implementation,
    }

    if func_name not in tool_map:
        return AgentResponse.error(error_message=f"Unknown tool: {func_name}")

    try:
        result = await tool_map[func_name](**args)
        return AgentResponse.success(content=result)
    except Exception as e:
        return AgentResponse.error(error_message=str(e))
```

### 3. Implement Tools

Add your tool implementations in `your_agent_name/tools/tools.py`:

```python
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def your_tool_implementation(arg1: str, arg2: int) -> str:
    """
    Implementation of your custom tool.

    Args:
        arg1: Description of first argument
        arg2: Description of second argument

    Returns:
        str: Result of the tool operation
    """
    try:
        # Your tool implementation here
        result = f"Processed {arg1} with value {arg2}"
        return result
    except Exception as e:
        logger.error(f"Error in tool implementation: {str(e)}", exc_info=True)
        raise
```

### 4. Update Configuration

Modify `your_agent_name/config.py` to include any necessary configuration for your tools:

```python
class Config:
    tools = [
        {
            "name": "your_tool_name",
            "description": "Description of what your tool does",
            "parameters": {
                "type": "object",
                "properties": {
                    "arg1": {
                        "type": "string",
                        "description": "Description of first argument"
                    },
                    "arg2": {
                        "type": "integer",
                        "description": "Description of second argument"
                    }
                },
                "required": ["arg1", "arg2"]
            }
        }
    ]
```

## Error Handling

Your agent inherits from `AgentCore` which provides several error handling mechanisms:

1. The `@handle_exceptions` decorator handles common exceptions:

   - `ValueError` for validation errors (returns as needs_info)
   - Unexpected errors (returns as error)

2. Use `AgentResponse` for structured responses:
   - `AgentResponse.success(content="Success message")`
   - `AgentResponse.error(error_message="Error description")`
   - `AgentResponse.needs_info(message="Additional information needed")`

## Best Practices

1. Always use the logger for debugging and monitoring:

```python
self.logger.info("Processing request")
self.logger.error("Error occurred", exc_info=True)
```

2. Validate inputs early:

```python
if not some_required_value:
    return AgentResponse.needs_info(message="Please provide required value")
```

3. Keep tool implementations modular and focused on a single responsibility

4. Document your code thoroughly, especially tool parameters and expected behavior

5. Use type hints consistently to make the code more maintainable

## Testing

Create tests for your agent in the `tests/agents/your_agent_name/` directory:

1. Test basic agent functionality
2. Test each tool implementation
3. Test error handling
4. Test edge cases and input validation

## Example Usage

```python
from src.agents.your_agent_name.agent import YourAgentNameAgent
from src.models.core import ChatRequest

# Initialize agent
agent = YourAgentNameAgent(config, llm, embeddings)

# Create request
request = ChatRequest(prompt="Your prompt here")

# Process request
response = await agent.chat(request)

# Handle response
if response.error_message:
    print(f"Error: {response.error_message}")
else:
    print(f"Success: {response.content}")
```
