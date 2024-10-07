import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SearchAgent:
    def __init__(self, config, llm, llm_ollama, embeddings, flask_app):
        self.llm = llm
        self.flask_app = flask_app
        self.config = config
        self.last_search_term = None

    def perform_search(self, search_term=None):
        # State management for search regeneration purposes
        if search_term is not None:
            self.last_search_term = search_term
        elif self.last_search_term is None:
            logger.warning("No search term available for web search")
            return "Web search failed. Please provide a search term."
        else:
            search_term = self.last_search_term

        logger.info(f"Performing web search for: {search_term}")

        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        # Initialize the webdriver
        driver = webdriver.Chrome(options=chrome_options)

        try:
            # Navigate to Google
            driver.get("https://www.google.com")

            # Find the search box and enter the search term
            search_box = driver.find_element(By.NAME, "q")
            search_box.send_keys(search_term)
            search_box.send_keys(Keys.RETURN)

            # Wait for the results to load
            time.sleep(2)

            # Get the page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Find the search results
            search_results = soup.find_all("div", class_="g")

            # Process and format the results
            formatted_results = []
            for result in search_results[:5]:  # Limit to top 5 results
                result_text = result.get_text(strip=True)
                formatted_results.append(f"Result:\n{result_text}")

            return "\n\n".join(formatted_results)

        except Exception as e:
            logger.error(f"Error performing web search: {str(e)}")
            return f"Error performing web search: {str(e)}"

        finally:
            # Close the browser
            driver.quit()

    def chat(self, request):
        try:
            data = request.get_json()
            logger.info(f"Received chat request: {data}")
            if "prompt" in data:
                prompt = data["prompt"]
                action = data.get("action", "search")
                logger.debug(f"Extracted prompt: {prompt}, action: {action}")

                if action == "search":
                    logger.info(
                        f"Performing web search for prompt: {prompt['content']}"
                    )
                    search_results = self.perform_search(prompt["content"])
                    logger.info(f"Search results: {search_results}")
                    return {"role": "assistant", "content": search_results}
                else:
                    logger.error(f"Invalid action received: {action}")
                    return {"error": "Invalid action"}, 400
            else:
                logger.error("Missing 'prompt' in chat request data")
                return {"error": "Missing parameters"}, 400
        except Exception as e:
            logger.exception(f"Unexpected error in chat method: {str(e)}")
            return {"Error": str(e)}, 500
