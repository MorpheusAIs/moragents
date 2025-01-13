#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to validate agent name
validate_agent_name() {
    if [[ ! $1 =~ ^[a-zA-Z][a-zA-Z0-9_-]*$ ]]; then
        echo -e "${RED}Error: Agent name must start with a letter and can only contain letters, numbers, underscores, and hyphens.${NC}"
        return 1
    fi
    return 0
}

# Function to create agent files
create_agent_files() {
    local agent_name=$1
    local agent_dir="${agent_name}"

    # Create directory
    mkdir -p "${agent_dir}"
    touch "${agent_dir}/__init__.py"

    # Create agent.py
    cat > "${agent_dir}/agent.py" << 'EOL'
import logging
from typing import Any, Dict

from src.agents.agent_core.agent import AgentCore
from src.models.core import ChatRequest, AgentResponse
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

class ${agent_name^}Agent(AgentCore):
    """Agent for handling ${agent_name} operations."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        super().__init__(config, llm, embeddings)
        self.tools_provided = []  # Add your tools here
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request."""
        try:
            messages = [
                SystemMessage(content="You are an agent that can perform various operations."),
                HumanMessage(content=request.prompt.content),
            ]

            result = self.tool_bound_llm.invoke(messages)
            return await self._handle_llm_response(result)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def _execute_tool(self, func_name: str, args: Dict[str, Any]) -> AgentResponse:
        """Execute the appropriate tool based on function name."""
        return AgentResponse.error(error_message=f"Tool {func_name} not implemented yet")
EOL

    # Create config.py
    cat > "${agent_dir}/config.py" << EOL
class Config:
    tools = []  # Add your tool configurations here
EOL

    # Create tools.py
    cat > "${agent_dir}/tools.py" << EOL
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Add your tool implementations here
EOL

    echo -e "${GREEN}Successfully created ${agent_name} agent!${NC}"
    echo -e "Agent location: ${BLUE}${agent_dir}${NC}"
}

# Main script
echo -e "${BLUE}Welcome to the Agent Creation Wizard${NC}"
echo "Please enter a name for your new agent:"
read agent_name

# Validate agent name
if ! validate_agent_name "$agent_name"; then
    exit 1
fi

# Check if agent directory already exists
if [ -d "${agent_name}" ]; then
    echo -e "${RED}Error: An agent with name '${agent_name}' already exists.${NC}"
    exit 1
fi

# Create agent
create_agent_files "$agent_name"