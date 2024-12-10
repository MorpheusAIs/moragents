# submodules/benchmarks/news_agent_benchmarks/benchmarks.py

import logging

import pytest

from submodules.moragents_dockers.agents.tests.news_agent_benchmarks.config import Config
from submodules.moragents_dockers.agents.tests.news_agent_benchmarks.helpers import (
    ask_news_agent,
    extract_classification,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_news_classification():
    for i, test_case in enumerate(Config.TEST_CASES):
        article_text = test_case["article_text"]
        expected_classification = test_case["expected_classification"]

        logger.info(f"Testing article classification (Test {i + 1})")

        # Ask the news agent to classify the article
        response = ask_news_agent(article_text, Config.LOCAL_AGENT_URL)

        # Extract the classification from the response
        classification = extract_classification(response)

        if classification == "UNKNOWN":
            logger.warning(
                f"Test case {i + 1} resulted in UNKNOWN classification. Response: {response}"
            )
            assert False, f"Test case {i + 1} failed: Could not determine classification"
        else:
            # Check if the classification matches the expected classification
            assert (
                classification == expected_classification
            ), f"Test case {i + 1} failed: Expected {expected_classification}, but got {classification}"

        logger.info(f"Test case {i + 1} passed: Correctly classified as {classification}")

    logger.info("All test cases passed successfully")


if __name__ == "__main__":
    pytest.main()
