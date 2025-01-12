import logging
from src.agents.crypto_data import tools
from src.models.core import ChatRequest, AgentResponse
from src.agents.agent_core.agent import AgentCore
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class CryptoDataAgent(AgentCore):
    """Agent for handling cryptocurrency-related queries and data retrieval."""

    def __init__(self, config, llm, embeddings):
        super().__init__(config, llm, embeddings)
        self.tools_provided = tools.get_tools()
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for crypto-related queries."""
        try:
            messages = [
                SystemMessage(
                    content=(
                        "Don't make assumptions about function arguments - "
                        "they should always be supplied by the user. "
                        "Ask for clarification if a request is ambiguous."
                    )
                ),
                HumanMessage(content=request.prompt.content),
            ]

            result = self.tool_bound_llm.invoke(messages)
            return await self._handle_llm_response(result)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def _execute_tool(self, func_name: str, args: dict) -> AgentResponse:
        """Execute the appropriate crypto tool based on function name."""
        try:
            metadata = {}

            if func_name == "get_price":
                if "coin_name" not in args:
                    return AgentResponse.needs_info(content="Please provide the name of the coin to get its price")
                content = tools.get_coin_price_tool(args["coin_name"])
                trading_symbol = tools.get_tradingview_symbol(tools.get_coingecko_id(args["coin_name"]))
                if trading_symbol:
                    metadata["coinId"] = trading_symbol
            elif func_name == "get_floor_price":
                if "nft_name" not in args:
                    return AgentResponse.needs_info(
                        content="Please provide the name of the NFT collection to get its floor price"
                    )
                content = tools.get_nft_floor_price_tool(args["nft_name"])
            elif func_name == "get_fdv":
                if "coin_name" not in args:
                    return AgentResponse.needs_info(
                        content="Please provide the name of the coin to get its fully diluted valuation"
                    )
                content = tools.get_fully_diluted_valuation_tool(args["coin_name"])
            elif func_name == "get_tvl":
                if "protocol_name" not in args:
                    return AgentResponse.needs_info(
                        content="Please provide the name of the protocol to get its total value locked"
                    )
                content = tools.get_protocol_total_value_locked_tool(args["protocol_name"])
            elif func_name == "get_market_cap":
                if "coin_name" not in args:
                    return AgentResponse.needs_info(content="Please provide the name of the coin to get its market cap")
                content = tools.get_coin_market_cap_tool(args["coin_name"])
            else:
                return AgentResponse.needs_info(
                    content=f"I don't know how to handle that type of request. Could you try asking about cryptocurrency news instead?"
                )

            if "error" in content.lower() or "not found" in content.lower():
                return AgentResponse.needs_info(content=content)

            return AgentResponse.success(content=content, metadata=metadata)

        except Exception as e:
            logger.error(f"Error executing tool {func_name}: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))
