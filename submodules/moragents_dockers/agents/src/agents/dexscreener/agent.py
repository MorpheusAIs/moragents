import logging
from typing import Dict, Any, List, Union, Optional
from src.agents.agent_core.agent import AgentCore
from src.models.core import ChatRequest, AgentResponse
from langchain.schema import HumanMessage, SystemMessage
from .config import Config
from . import tools
from .models import TokenProfile, BoostedToken

logger = logging.getLogger(__name__)


class DexScreenerAgent(AgentCore):
    """Agent for interacting with DexScreener Token API."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        super().__init__(config, llm, embeddings)
        self.tools_provided = Config.tools
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for DexScreener API interactions."""
        try:
            messages = [
                SystemMessage(
                    content=(
                        "You are an agent that can fetch and analyze cryptocurrency token data "
                        "from DexScreener. You can get token profiles and information about "
                        "boosted tokens across different chains. When chain_id is not specified, "
                        "you'll get data for all chains. You can filter by specific chains like "
                        "'solana', 'ethereum', or 'bsc'."
                    )
                ),
                HumanMessage(content=request.prompt.content),
            ]

            result = self.tool_bound_llm.invoke(messages)
            return await self._handle_llm_response(result)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def _execute_tool(self, func_name: str, args: Dict[str, Any]) -> AgentResponse:
        """Execute the appropriate DexScreener API tool based on function name."""
        try:
            chain_id = args.get("chain_id")
            result = None

            if func_name == "get_latest_token_profiles":
                result = await tools.get_latest_token_profiles(chain_id)
            elif func_name == "get_latest_boosted_tokens":
                result = await tools.get_latest_boosted_tokens(chain_id)
            elif func_name == "get_top_boosted_tokens":
                result = await tools.get_top_boosted_tokens(chain_id)
            else:
                return AgentResponse.error(error_message=f"Unknown tool: {func_name}")

            return AgentResponse.success(content=self._format_token_response(result, chain_id))

        except Exception as e:
            logger.error(f"Error executing tool {func_name}: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    def _format_token_response(
        self, tokens: List[Union[TokenProfile, BoostedToken]], chain_id: Optional[str] = None
    ) -> str:
        """Format token data into a readable string."""
        if not tokens:
            chain_msg = f" for chain {chain_id}" if chain_id else ""
            return f"No tokens found{chain_msg}."

        # Limit to top 10 tokens
        tokens = tokens[:10]

        formatted = f"# Top {len(tokens)} Tokens"
        if chain_id:
            formatted += f" on {chain_id}"
        formatted += "\n\n"

        for token in tokens:
            logger.info("Token: %s", token)

            # Add icon if available
            if token.get("icon"):
                formatted += f"![Token Icon]({token['icon']})\n\n"

            formatted += f"### `{token['tokenAddress']}`\n\n"

            if token.get("description"):
                formatted += f"{token['description']}\n\n"

            # Format all links in a single line
            links = token.get("links", [])
            if links:
                formatted += "**Links**: "
                link_parts = []

                # Add DexScreener URL first
                link_parts.append(f"[DexScreener]({token['url']})")

                # Add other links
                for link in links:
                    if link.get("url"):
                        label = link.get("type") or link.get("label") or "Link"
                        link_parts.append(f"[{label}]({link['url']})")

                formatted += " • ".join(link_parts) + "\n\n"

            formatted += "\n---\n\n\n"

        return formatted
