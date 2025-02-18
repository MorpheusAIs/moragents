import logging
from typing import Dict, Any
from src.models.service.agent_core import AgentCore
from src.models.service.chat_models import ChatRequest, AgentResponse
from langchain.schema import HumanMessage, SystemMessage
from .config import Config
from . import tools
from .models import TopTokensResponse, TopHoldersResponse, NftSearchResponse
from src.stores import chat_manager_instance

logger = logging.getLogger(__name__)


class CodexAgent(AgentCore):
    """Agent for interacting with Codex.io API."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        super().__init__(config, llm, embeddings)
        self.tools_provided = Config.tools
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for Codex API interactions."""
        try:
            messages = [
                SystemMessage(
                    content=(
                        "You are an agent that can fetch and analyze token and NFT data "
                        "from Codex.io. You can get trending tokens, analyze token holder "
                        "concentration, and search for NFT collections."
                    )
                ),
                HumanMessage(content=request.prompt.content),
            ]
            chat_history = chat_manager_instance.get_chat_history(request.conversation_id)
            if chat_history:
                messages.append(HumanMessage(content=f"Here is the chat history: {chat_history}"))

            result = self.tool_bound_llm.invoke(messages)
            return await self._handle_llm_response(result)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def _execute_tool(self, func_name: str, args: Dict[str, Any]) -> AgentResponse:
        """Execute the appropriate Codex API tool based on function name."""
        try:
            if func_name == "list_top_tokens":
                top_tokens_response = await tools.list_top_tokens(
                    limit=args.get("limit"),
                    network_filter=args.get("networkFilter"),
                    resolution=args.get("resolution"),
                )
                return AgentResponse.success(
                    content=top_tokens_response.formatted_response,
                    metadata=top_tokens_response.model_dump(),
                    action_type="list_top_tokens",
                )

            elif func_name == "get_top_holders_percent":
                holders_response = await tools.get_top_holders_percent(
                    token_id=args["tokenId"],
                )
                return AgentResponse.success(
                    content=holders_response.formatted_response,
                    metadata=holders_response.model_dump(),
                    action_type="get_top_holders_percent",
                )

            elif func_name == "search_nfts":
                nft_search_response = await tools.search_nfts(
                    search=args["search"],
                    limit=args.get("limit"),
                    network_filter=args.get("networkFilter"),
                    filter_wash_trading=args.get("filterWashTrading"),
                    window=args.get("window"),
                )
                return AgentResponse.success(
                    content=nft_search_response.formatted_response,
                    metadata=nft_search_response.model_dump(),
                    action_type="search_nfts",
                )

            else:
                return AgentResponse.error(error_message=f"Unknown tool: {func_name}")

        except Exception as e:
            logger.error(f"Error executing tool {func_name}: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))
