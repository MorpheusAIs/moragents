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

            if func_name == "search_dex_pairs":
                result = await tools.search_dex_pairs(args["query"])
                return AgentResponse.success(content=self._format_dex_pairs_response(result))

            else:
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

    def _format_dex_pairs_response(self, pairs: List[Dict[str, Any]]) -> str:
        """Format DEX pairs data into a readable string."""
        if not pairs:
            return "No DEX pairs found matching your search."

        # Limit to top 10 pairs for readability
        pairs = pairs[:10]

        formatted = f"# Found {len(pairs)} popular DEX Trading Pairs\n\n"

        for pair in pairs:
            # Basic pair info
            base_token = pair.get("baseToken", {})
            quote_token = pair.get("quoteToken", {})

            formatted += f"## {base_token.get('symbol', '')} / {quote_token.get('symbol', '')} on {pair.get('dexId', '').title()}\n"
            formatted += f"Chain: {pair.get('chainId', '').upper()}\n\n"

            # Price information
            if pair.get("priceUsd"):
                formatted += f"Price: ${float(pair['priceUsd']):.4f}\n"

                # Add 24h price change if available
                price_change = pair.get("priceChange", {}).get("h24")
                if price_change is not None:
                    change_symbol = "📈" if float(price_change) > 0 else "📉"
                    formatted += f"24h Change: {change_symbol} {price_change:.2f}%\n"

            # Volume and liquidity
            volume = pair.get("volume", {})
            if volume.get("h24"):
                formatted += f"24h Volume: ${float(volume['h24']):,.2f}\n"

            liquidity = pair.get("liquidity", {})
            if liquidity.get("usd"):
                formatted += f"Liquidity: ${float(liquidity['usd']):,.2f}\n"

            # Transaction counts
            txns = pair.get("txns", {}).get("h24", {})
            if txns:
                buys = txns.get("buys", 0)
                sells = txns.get("sells", 0)
                formatted += f"24h Transactions: {buys + sells} (🟢 {buys} buys, 🔴 {sells} sells)\n"

            # Add links
            formatted += "\n**Links**: "
            link_parts = []

            # Add DexScreener link first
            link_parts.append(f"[DexScreener]({pair.get('url', '')})")

            # Add website and social links
            info = pair.get("info", {})
            for website in info.get("websites", []):
                label = website.get("label", "Website")
                link_parts.append(f"[{label}]({website.get('url')})")

            for social in info.get("socials", []):
                social_type = social.get("type", "").title()
                link_parts.append(f"[{social_type}]({social.get('url')})")

            formatted += " • ".join(link_parts) + "\n\n"
            formatted += "\n---\n\n"

        return formatted
