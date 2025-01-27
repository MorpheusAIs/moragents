import logging
import re
import urllib.parse
from datetime import datetime, timedelta
from html import unescape

import feedparser
import pytz
from dateutil import parser
from src.agents.news_agent.config import Config

logger = logging.getLogger(__name__)


def clean_html(raw_html):
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    cleantext = unescape(cleantext)
    cleantext = " ".join(cleantext.split())
    return cleantext


def is_within_time_window(published_time, hours=24):
    if not published_time:
        return False
    try:
        pub_date = parser.parse(published_time, fuzzy=True)
        now = datetime.now(pytz.UTC)
        if pub_date.tzinfo is None:
            pub_date = pub_date.replace(tzinfo=pytz.UTC)
        return (now - pub_date) <= timedelta(hours=hours)
    except Exception as e:
        logger.error(f"Error parsing date: {str(e)} for date {published_time}")
        return False


def fetch_rss_feed(feed_url):
    # URL encode the query parameter
    parsed_url = urllib.parse.urlparse(feed_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    if "q" in query_params:
        query_params["q"] = [urllib.parse.quote(q) for q in query_params["q"]]
    encoded_query = urllib.parse.urlencode(query_params, doseq=True)
    encoded_url = urllib.parse.urlunparse(parsed_url._replace(query=encoded_query))

    return feedparser.parse(encoded_url)


def get_tools():
    """Return a list of tools for the agent."""
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
