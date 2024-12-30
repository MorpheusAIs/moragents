import logging
from typing import Any, Dict, Optional, List

from src.agents.agent_core.agent import AgentCore
from src.models.core import ChatRequest, AgentResponse
from langchain.schema import HumanMessage, SystemMessage
from .config import Config
from .client import RugcheckClient

logger = logging.getLogger(__name__)


class RugcheckAgent(AgentCore):
    """Agent for analyzing token safety and trends using the Rugcheck API."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        super().__init__(config, llm, embeddings)
        self.tools_provided = Config.tools
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)
        self.api_base_url = "https://api.rugcheck.xyz/v1"

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for token analysis."""
        try:
            messages = [
                SystemMessage(
                    content=(
                        "You are an agent that can analyze tokens for safety and view trending tokens. "
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
                mint = args.get("mint")
                if not mint:
                    return AgentResponse.error(error_message="Please provide a token mint address")

                try:
                    report = await self._fetch_token_report(mint)

                    # Format a user-friendly response
                    risks = "\n".join(
                        [
                            f"- {risk['name']}: {risk['description']} (Score: {risk['score']})"
                            for risk in report.get("risks", [])
                        ]
                    )

                    content = (
                        f"Token Analysis Report for {mint}\n"
                        f"Name: {report.get('tokenMeta', {}).get('name')}\n"
                        f"Symbol: {report.get('tokenMeta', {}).get('symbol')}\n"
                        f"Overall Score: {report.get('score')}\n"
                        f"\nRisk Factors:\n{risks}\n"
                        f"\nTotal Market Liquidity: {report.get('totalMarketLiquidity')} USD"
                    )

                    return AgentResponse.success(content=content)

                except Exception as e:
                    return AgentResponse.error(error_message=f"Failed to get token report: {str(e)}")

            elif func_name == "get_most_viewed":
                try:
                    viewed_tokens = await self._fetch_most_viewed()
                    content = "Most Viewed Tokens (Past 24h):\n"
                    tokens_list = list(viewed_tokens.values()) if isinstance(viewed_tokens, dict) else viewed_tokens
                    for token in tokens_list[:10]:  # Top 10
                        content += (
                            f"\n- {token['metadata']['name']} ({token['metadata']['symbol']})\n"
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
                    for token in tokens_list[:10]:  # Top 10
                        content += f"\n- Mint: {token['mint']}\n  Upvotes: {token['up_count']}, Total Votes: {token['vote_count']}"
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
