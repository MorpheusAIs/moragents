import logging
import re
import pyshorteners
from typing import List, Dict

from src.agents.news_agent.config import Config
from src.agents.news_agent.tools import clean_html, fetch_rss_feed, is_within_time_window
from src.models.core import ChatRequest, AgentResponse
from src.agents.agent_core.agent import AgentCore
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

class NewsAgent(AgentCore):
    """Agent for fetching and analyzing cryptocurrency news."""

    def __init__(self, config, llm, embeddings):
        super().__init__(config, llm, embeddings)
        self.tools_provided = self.get_tools()
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)
        self.url_shortener = pyshorteners.Shortener()
        self.max_news_items = 2  # Hard limit of 2 news items total

    def get_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "fetch_crypto_news",
                    "description": "Fetch and analyze cryptocurrency news for potential price impacts",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "coins": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of cryptocurrency symbols to fetch news for",
                            }
                        },
                        "required": ["coins"],
                    },
                },
            }
        ]

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for news-related queries."""
        try:
            messages = [
                SystemMessage(
                    content=(
                        "You are a news analysis agent that fetches and analyzes cryptocurrency news. "
                        "Ask for clarification if a request is ambiguous."
                    )
                ),
                HumanMessage(content=request.prompt.content),
            ]

            result = self.tool_bound_llm.invoke(messages)
            return await self._handle_llm_response(result)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return AgentResponse.needs_info(
                content="I ran into an issue processing your request. Could you try rephrasing it?"
            )

    def _check_relevance_and_summarize(self, title: str, content: str, coin: str) -> str:
        """Check if news is relevant and generate summary."""
        prompt = Config.RELEVANCE_PROMPT.format(coin=coin, title=title, content=content)
        result = self.llm.invoke(
            input=[{"role": "user", "content": prompt}],
            max_tokens=Config.LLM_MAX_TOKENS,
            temperature=Config.LLM_TEMPERATURE,
        )
        return result.content.strip()

    def _process_rss_feed(self, feed_url: str, coin: str, remaining_slots: int) -> List[Dict]:
        """Process RSS feed and filter relevant articles with strict limits."""
        if remaining_slots <= 0:
            return []

        logger.info(f"Processing RSS feed for {coin}: {feed_url}")
        feed = fetch_rss_feed(feed_url)
        results = []
        
        # Only process up to 3 entries to avoid excessive API calls
        for entry in (feed.entries or [])[:3]:
            if len(results) >= remaining_slots:
                break

            published_time = entry.get("published") or entry.get("updated")
            if not is_within_time_window(published_time):
                continue

            title = clean_html(entry.title)
            content = clean_html(entry.summary)
            result = self._check_relevance_and_summarize(title, content, coin)
            
            if not result.upper().startswith("NOT RELEVANT"):
                results.append({
                    "Title": title,
                    "Summary": result,
                    "Link": entry.link
                })

        logger.info(f"Found {len(results)} relevant articles for {coin}")
        return results

    def _fetch_crypto_news(self, coins: List[str]) -> List[Dict]:
        """Fetch and process news for specified coins with strict limits."""
        logger.info(f"Fetching news for coins: {coins}")
        all_news = []
        remaining_slots = self.max_news_items

        for coin in coins:
            if remaining_slots <= 0:
                break

            logger.info(f"Processing news for {coin}")
            coin_name = Config.CRYPTO_DICT.get(coin.upper(), coin)
            google_news_url = Config.GOOGLE_NEWS_BASE_URL.format(coin_name)
            
            results = self._process_rss_feed(
                google_news_url, 
                coin_name,
                remaining_slots
            )
            
            # Add results while respecting the total limit
            for result in results[:remaining_slots]:
                all_news.append({"Coin": coin, **result})
                remaining_slots -= 1

            if remaining_slots <= 0:
                break

        logger.info(f"Total news items fetched: {len(all_news)}")
        return all_news

    async def _execute_tool(self, func_name: str, args: dict) -> AgentResponse:
        """Execute the appropriate news tool based on function name with enforced limits."""
        try:
            if func_name == "fetch_crypto_news":
                coins = args.get("coins", [])
                if not coins:
                    return AgentResponse.needs_info(
                        content="Could you specify which cryptocurrencies you'd like news about?"
                    )

                news = self._fetch_crypto_news(coins)
                if not news:
                    return AgentResponse.success(
                        content="No relevant news found for the specified cryptocurrencies in the last 24 hours."
                    )

                response = "Here are the latest news items that could impact token prices:\n\n"
                for index, item in enumerate(news, start=1):
                    coin_name = Config.CRYPTO_DICT.get(item["Coin"], item["Coin"])
                    short_url = self.url_shortener.tinyurl.short(item["Link"])
                    response += f"{index}. ***{coin_name} News***:\n"
                    response += f"{item['Title']}\n"
                    response += f"{item['Summary']}\n"
                    response += f"Read more: {short_url}\n\n"

                return AgentResponse.success(content=response)
            else:
                return AgentResponse.needs_info(
                    content="I don't know how to handle that type of request. Could you try asking about cryptocurrency news instead?"
                )

        except Exception as e:
            logger.error(f"Error executing tool {func_name}: {str(e)}", exc_info=True)
            return AgentResponse.needs_info(
                content="I encountered an issue fetching the news. Could you try again?"
            )
