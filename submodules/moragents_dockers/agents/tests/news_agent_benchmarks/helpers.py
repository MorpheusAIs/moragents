# submodules/benchmarks/news_agent_benchmarks/helpers.py

import logging

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ask_news_agent(article_text: str, url: str) -> dict:
    headers = {"Content-Type": "application/json"}
    payload = {
        "prompt": {
            "role": "user",
            "content": f"Classify if this article is relevant to cryptocurrency price movements: {article_text}",
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")


def extract_classification(response: dict) -> str:
    if not isinstance(response, dict):
        logger.warning(f"Unexpected response type: {type(response)}")
        return "UNKNOWN"

    content = response.get("content")

    if content is None:
        logger.warning("Response content is None")
        return "UNKNOWN"

    if not isinstance(content, str):
        logger.warning(f"Unexpected content type: {type(content)}")
        return "UNKNOWN"

    content = content.upper()

    if "NOT RELEVANT" in content:
        return "NOT RELEVANT"
    elif "RELEVANT" in content:
        return "RELEVANT"
    else:
        logger.warning(f"Could not determine relevance from content: {content}")
        return "NOT RELEVANT"
