from typing import Dict, Any, Optional, Union
import logging
from src.agents.agent_core.agent import AgentCore
from src.models.core import ChatRequest, AgentResponse
from langchain.schema import HumanMessage, SystemMessage
from .config import Config, TokenRegistry
from .client import RugcheckClient

logger = logging.getLogger(__name__)


class RugcheckAgent(AgentCore):
    """Agent for analyzing token safety and trends using the Rugcheck API."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        super().__init__(config, llm, embeddings)
        self.tools_provided = Config.tools
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)
        self.api_base_url = "https://api.rugcheck.xyz/v1"
        self.token_registry = TokenRegistry()

    async def _resolve_token_identifier(self, identifier: str) -> Optional[str]:
        """
        Resolve a token identifier (name or mint address) to a mint address.
        Returns None if the identifier cannot be resolved.
        """
        # If it's already a mint address, return it directly
        if self.token_registry.is_valid_mint_address(identifier):
            return identifier

        # Try to resolve token name to mint address
        mint_address = self.token_registry.get_mint_by_name(identifier)
        if mint_address:
            return mint_address

        return None

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for token analysis."""
        try:
            messages = [
                SystemMessage(
                    content=(
                        "You are an agent that can analyze tokens for safety and view trending tokens. "
                        "You can handle both token names (like 'BONK' or 'RAY') and mint addresses. "
                        "When you need to perform an analysis, use the appropriate function call."
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
        """Execute the appropriate Rugcheck API tool based on function name."""
        try:
            if func_name == "get_token_report":
                identifier = args.get("identifier")
                if not identifier:
                    return AgentResponse.error(error_message="Please provide a token name or mint address")

                try:
                    mint_address = await self._resolve_token_identifier(identifier)
                    if not mint_address:
                        return AgentResponse.error(error_message=f"Could not resolve token identifier: {identifier}")

                    report = await self._fetch_token_report(mint_address)
                    token_name = self.token_registry.get_name_by_mint(mint_address) or identifier

                    # Format a user-friendly response
                    risks = "\n".join(
                        [
                            f"- {risk['name']}: {risk['description']} (Score: {risk['score']})"
                            for risk in report.get("risks", [])
                        ]
                    )
                    content = (
                        f"# Token Analysis Report for {token_name}\n\n"
                        f"Mint Address: {mint_address}\n\n"
                        f"- Overall Risk Score: {report.get('score') or 'Unknown'}\n\n"
                        f"## Potential Risks:\n\n"
                        f"{risks}\n\n"
                    )

                    return AgentResponse.success(content=content)

                except Exception as e:
                    return AgentResponse.error(error_message=f"Failed to get token report: {str(e)}")

            # Rest of the _execute_tool implementation remains the same
            elif func_name == "get_most_viewed":
                try:
                    viewed_tokens = await self._fetch_most_viewed()
                    content = "Most Viewed Tokens (Past 24h):\n"
                    tokens_list = list(viewed_tokens.values()) if isinstance(viewed_tokens, dict) else viewed_tokens
                    for token in tokens_list[:10]:
                        mint = token["mint"]
                        token_name = self.token_registry.get_name_by_mint(mint) or token["metadata"]["name"]
                        content += (
                            f"\n- {token_name} ({token['metadata']['symbol']})\n"
                            f"  Mint: {mint}\n"
                            f"  Visits: {token['visits']}, Unique Users: {token['user_visits']}"
                        )
                    return AgentResponse.success(content=content)

                except Exception as e:
                    return AgentResponse.error(error_message=f"Failed to get most viewed tokens: {str(e)}")

            elif func_name == "get_most_voted":
                try:
                    voted_tokens = await self._fetch_most_voted()
                    content = "Most Voted Tokens (Past 24h):\n"
                    tokens_list = list(voted_tokens.values()) if isinstance(voted_tokens, dict) else voted_tokens
                    for token in tokens_list[:10]:
                        mint = token["mint"]
                        token_name = self.token_registry.get_name_by_mint(mint) or mint
                        content += (
                            f"\n- {token_name}\n"
                            f"  Mint: {mint}\n"
                            f"  Upvotes: {token['up_count']}, Total Votes: {token['vote_count']}"
                        )
                    return AgentResponse.success(content=content)

                except Exception as e:
                    return AgentResponse.error(error_message=f"Failed to get most voted tokens: {str(e)}")

            else:
                return AgentResponse.error(error_message=f"Unknown tool function: {func_name}")

        except Exception as e:
            logger.error(f"Error executing tool {func_name}: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def _fetch_token_report(self, mint: str) -> Dict[str, Any]:
        """Fetch token report from Rugcheck API."""
        client = RugcheckClient(self.api_base_url)
        try:
            return await client.get_token_report(mint)
        finally:
            await client.close()

    async def _fetch_most_viewed(self) -> Dict[str, Any]:
        """Fetch most viewed tokens from Rugcheck API."""
        client = RugcheckClient(self.api_base_url)
        try:
            return await client.get_most_viewed()
        finally:
            await client.close()

    async def _fetch_most_voted(self) -> Dict[str, Any]:
        """Fetch most voted tokens from Rugcheck API."""
        client = RugcheckClient(self.api_base_url)
        try:
            return await client.get_most_voted()
        finally:
            await client.close()
