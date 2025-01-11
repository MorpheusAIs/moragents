import logging
from typing import Dict, Any

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from src.models.core import ChatRequest, AgentResponse
from src.agents.agent_core.agent import AgentCore
from langchain.schema import HumanMessage, SystemMessage
from src.agents.realtime_search.config import Config

logger = logging.getLogger(__name__)


class RealtimeSearchAgent(AgentCore):
    """Agent for performing real-time web searches."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        super().__init__(config, llm, embeddings)
        self.last_search_term = None
        self.tools_provided = Config.tools
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for web search queries."""
        try:
            messages = [
                SystemMessage(
                    content=(
                        "You are a real-time web search agent that helps find current information. "
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

    async def _execute_tool(self, func_name: str, args: Dict[str, Any]) -> AgentResponse:
        """Execute the appropriate search tool based on function name."""
        try:
            if func_name == "perform_web_search":
                search_term = args.get("search_term")
                if not search_term:
                    return AgentResponse.needs_info(content="Could you please provide a search term?")

                search_results = self._perform_search_with_web_scraping(search_term)
                if "Error performing web search" in search_results:
                    return AgentResponse.error(error_message=search_results)

                synthesized_answer = self._synthesize_answer(search_term, search_results)
                return AgentResponse.success(content=synthesized_answer)
            else:
                return AgentResponse.error(error_message=f"Unknown tool: {func_name}")

        except Exception as e:
            logger.error(f"Error executing tool {func_name}: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    def _perform_search_with_web_scraping(self, search_term: str) -> str:
        """Perform web search using requests and BeautifulSoup."""
        logger.info(f"Performing web search for: {search_term}")

        try:
            url = Config.SEARCH_URL.format(search_term)
            headers = {"User-Agent": Config.USER_AGENT}
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            search_results = soup.find_all("div", class_="g")

            if not search_results:
                return AgentResponse.needs_info(
                    content="I couldn't find any results for that search. Could you try rephrasing it?"
                )

            formatted_results = []
            for result in search_results[: Config.MAX_SEARCH_RESULTS]:
                result_text = result.get_text(strip=True)
                formatted_results.append(f"Result:\n{result_text}")

            return "\n\n".join(formatted_results)

        except requests.RequestException as e:
            logger.error(f"Error performing web search: {str(e)}")
            logger.info("Attempting fallback to headless browsing")
            return self._perform_search_with_headless_browsing(search_term)

    def _perform_search_with_headless_browsing(self, search_term: str) -> str:
        """Fallback search method using headless Chrome."""
        chrome_options = Options()
        for option in Config.CHROME_OPTIONS:
            chrome_options.add_argument(option)
        driver = webdriver.Chrome(options=chrome_options)

        try:
            driver.get("https://www.google.com")
            search_box = driver.find_element(By.NAME, "q")
            search_box.send_keys(search_term)
            search_box.send_keys(Keys.RETURN)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            search_results = soup.find_all("div", class_="g")

            if not search_results:
                return AgentResponse.needs_info(
                    content="I couldn't find any results. Could you try being more specific?"
                )

            formatted_results = []
            for result in search_results[: Config.MAX_SEARCH_RESULTS]:
                result_text = result.get_text(strip=True)
                formatted_results.append(f"Result:\n{result_text}")

            return "\n\n".join(formatted_results)

        except Exception as e:
            error_msg = f"Error performing headless web search: {str(e)}"
            logger.error(error_msg)
            return error_msg
        finally:
            driver.quit()

    def _synthesize_answer(self, search_term: str, search_results: str) -> str:
        """Synthesize search results into a coherent answer."""
        logger.info("Synthesizing answer from search results")
        messages = [
            {
                "role": "system",
                "content": Config.SYNTHESIS_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"Query: {search_term}\nResults: {search_results}",
            },
        ]

        try:
            result = self.llm.invoke(messages, max_tokens=Config.MAX_TOKENS, temperature=Config.TEMPERATURE)
            if not result.content.strip():
                return AgentResponse.needs_info(
                    content="I found some results but couldn't understand them well. Could you rephrase your question?"
                )
            return result.content.strip()
        except Exception as e:
            logger.error(f"Error synthesizing answer: {str(e)}")
            raise
