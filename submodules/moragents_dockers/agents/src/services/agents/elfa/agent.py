import logging
from typing import Dict, Any
from src.models.service.agent_core import AgentCore
from src.models.service.chat_models import ChatRequest, AgentResponse
from langchain.schema import HumanMessage, SystemMessage
from .config import Config
from . import tools
from .models import MentionsResponse, TopMentionsResponse, TrendingTokensResponse, AccountSmartStatsResponse

logger = logging.getLogger(__name__)


class ElfaAgent(AgentCore):
    """Agent for interacting with Elfa Social API."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        super().__init__(config, llm, embeddings)
        self.tools_provided = Config.tools
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for Elfa API interactions."""
        try:
            messages = [
                SystemMessage(
                    content=(
                        "You are an agent that can fetch and analyze social media data "
                        "from Elfa. You can get trending tokens, mentions, and smart account "
                        "statistics. The data is focused on cryptocurrency and blockchain "
                        "related social media activity."
                    )
                ),
                *request.messages_for_llm,
            ]

            result = self.tool_bound_llm.invoke(messages)
            return await self._handle_llm_response(result)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def _execute_tool(self, func_name: str, args: Dict[str, Any]) -> AgentResponse:
        """Execute the appropriate Elfa API tool based on function name."""
        try:
            if func_name == "get_mentions":
                mentions_response: MentionsResponse = await tools.get_mentions(limit=args.get("limit"))
                return AgentResponse.success(
                    content=self._format_mentions_response(mentions_response),
                    metadata=mentions_response.model_dump(),
                    action_type="get_mentions",
                )

            elif func_name == "get_top_mentions":
                top_mentions_response: TopMentionsResponse = await tools.get_top_mentions(
                    ticker=args["ticker"],
                    time_window=args.get("timeWindow"),
                    include_account_details=args.get("includeAccountDetails"),
                )
                return AgentResponse.success(
                    content=self._format_top_mentions_response(top_mentions_response),
                    metadata=top_mentions_response.model_dump(),
                    action_type="get_top_mentions",
                )

            elif func_name == "search_mentions":
                keywords = args.get("keywords", ["crypto"])
                if isinstance(keywords, str):
                    keywords = [keywords]

                search_mentions_response = await tools.search_mentions(keywords=keywords)
                return AgentResponse.success(
                    content=self._format_mentions_response(search_mentions_response),
                    metadata=search_mentions_response.model_dump(),
                    action_type="search_mentions",
                )

            elif func_name == "get_trending_tokens":
                trending_tokens_response = await tools.get_trending_tokens(
                    time_window=args.get("timeWindow"), min_mentions=args.get("minMentions")
                )
                return AgentResponse.success(
                    content=self._format_trending_tokens_response(trending_tokens_response),
                    metadata=trending_tokens_response.model_dump(),
                    action_type="get_trending_tokens",
                )

            elif func_name == "get_account_smart_stats":
                smart_stats_response = await tools.get_account_smart_stats(args["username"])
                return AgentResponse.success(
                    content=self._format_account_stats_response(smart_stats_response),
                    metadata=smart_stats_response.model_dump(),
                    action_type="get_account_smart_stats",
                )

            else:
                return AgentResponse.error(error_message=f"Unknown tool: {func_name}")

        except Exception as e:
            logger.error(f"Error executing tool {func_name}: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    def _format_mentions_response(self, response: MentionsResponse) -> str:
        """Format mentions data into a readable string."""
        if not response.success:
            return "Failed to get mentions."

        if not response.data:
            return "No mentions found."

        formatted = f"# Latest {len(response.data)} Social Media Mentions\n\n"

        for mention in response.data:
            formatted += f"## @{mention.account.username}\n\n"
            formatted += f"{mention.content}\n\n"

            formatted += "**Metrics**:\n"
            formatted += f"- 👁️ Views: {mention.viewCount:,}\n"
            formatted += f"- 🔄 Reposts: {mention.repostCount:,}\n"
            formatted += f"- 💬 Replies: {mention.replyCount:,}\n"
            formatted += f"- ❤️ Likes: {mention.likeCount:,}\n\n"

            formatted += f"Posted at: {mention.mentionedAt}\n\n"

            if mention.originalUrl:
                formatted += f"[View Original]({mention.originalUrl})\n\n"

            formatted += "---\n\n"

        return formatted

    def _format_top_mentions_response(self, response: TopMentionsResponse) -> str:
        """Format top mentions data into a readable string."""
        if not response.success:
            return "Failed to get top mentions."

        if not response.data.data:
            return "No top mentions found for this ticker."

        formatted = f"# Top Mentions (Total: {response.data.total})\n\n"

        for mention in response.data.data:
            formatted += f"### Post ID: {mention.id}\n\n"
            formatted += f"{mention.content}\n\n"

            formatted += "**Engagement**:\n"
            formatted += f"- 👁️ Views: {mention.metrics.view_count:,}\n"
            formatted += f"- 🔄 Reposts: {mention.metrics.repost_count:,}\n"
            formatted += f"- 💬 Replies: {mention.metrics.reply_count:,}\n"
            formatted += f"- ❤️ Likes: {mention.metrics.like_count:,}\n\n"

            formatted += f"Posted at: {mention.mentioned_at}\n\n"
            formatted += "---\n\n"

        return formatted

    def _format_trending_tokens_response(self, response: TrendingTokensResponse) -> str:
        """Format trending tokens data into a readable string."""
        if not response.success:
            return "Failed to get trending tokens."

        if not response.data.data:
            return "No trending tokens found."

        formatted = "# Trending Tokens\n\n"

        for token in response.data.data:
            formatted += f"## ${token.token}\n\n"
            formatted += f"Current Mentions: {token.current_count:,}\n"
            formatted += f"Previous Period: {token.previous_count:,}\n"

            emoji = "📈" if token.change_percent > 0 else "📉" if token.change_percent < 0 else "➡️"
            formatted += f"Change: {emoji} {token.change_percent:+.2f}%\n\n"
            formatted += "---\n\n"

        return formatted

    def _format_account_stats_response(self, response: AccountSmartStatsResponse) -> str:
        """Format account smart stats into a readable string."""
        if not response.success:
            return "Failed to get account statistics."

        formatted = "# Account Smart Statistics\n\n"

        formatted += "## Engagement Metrics\n\n"
        formatted += f"Smart Following Count: {response.data.smartFollowingCount:,}\n"
        formatted += f"Average Engagement: {response.data.averageEngagement:.2f}\n"
        formatted += f"Follower Engagement Ratio: {response.data.followerEngagementRatio:.2%}\n"

        return formatted
