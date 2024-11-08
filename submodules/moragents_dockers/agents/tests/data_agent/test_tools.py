import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src", "data_agent", "src"))
)
# The above sys/os lines are needed because the agents have identical namings (i.e. agent.py, tools.py)

from unittest.mock import MagicMock, patch

import pytest
from src.data_agent.src.tools import (
    get_coin_market_cap_tool,
    get_coin_price_tool,
    get_coingecko_id,
    get_fdv,
    get_floor_price,
    get_fully_diluted_valuation_tool,
    get_market_cap,
    get_nft_floor_price_tool,
    get_price,
    get_protocol_tvl,
)

# Mock responses
mock_coingecko_search = {"coins": [{"id": "bitcoin"}], "nfts": [{"id": "bored-ape-yacht-club"}]}
mock_price_response = {"bitcoin": {"usd": 50000}}
mock_floor_price_response = {"floor_price": {"usd": 100000}}
mock_fdv_response = {"market_data": {"fully_diluted_valuation": {"usd": 1000000000000}}}
mock_market_cap_response = [{"market_cap": 500000000000}]
mock_tvl_response = {"tvl": 10000000000}


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = {}
        yield mock_get


def test_get_coingecko_id_coin(mock_requests_get):
    mock_requests_get.return_value.json.return_value = mock_coingecko_search
    assert get_coingecko_id("bitcoin", type="coin") == "bitcoin"


def test_get_coingecko_id_nft(mock_requests_get):
    mock_requests_get.return_value.json.return_value = mock_coingecko_search
    assert get_coingecko_id("bored ape", type="nft") == "bored-ape-yacht-club"


def test_get_price(mock_requests_get):
    mock_requests_get.return_value.json.side_effect = [mock_coingecko_search, mock_price_response]
    assert get_price("bitcoin") == 50000


def test_get_floor_price(mock_requests_get):
    mock_requests_get.return_value.json.side_effect = [
        mock_coingecko_search,
        mock_floor_price_response,
    ]
    assert get_floor_price("bored ape") == 100000


def test_get_fdv(mock_requests_get):
    mock_requests_get.return_value.json.side_effect = [mock_coingecko_search, mock_fdv_response]
    assert get_fdv("bitcoin") == 1000000000000


def test_get_market_cap(mock_requests_get):
    mock_requests_get.return_value.json.side_effect = [
        mock_coingecko_search,
        mock_market_cap_response,
    ]
    assert get_market_cap("bitcoin") == 500000000000


def test_get_coin_price_tool(mock_requests_get):
    mock_requests_get.return_value.json.side_effect = [mock_coingecko_search, mock_price_response]
    result = get_coin_price_tool("bitcoin")
    assert "The price of bitcoin is $50,000" in result


def test_get_nft_floor_price_tool(mock_requests_get):
    mock_requests_get.return_value.json.side_effect = [
        mock_coingecko_search,
        mock_floor_price_response,
    ]
    result = get_nft_floor_price_tool("bored ape")
    assert "The floor price of bored ape is $100,000" in result


def test_get_fully_diluted_valuation_tool(mock_requests_get):
    mock_requests_get.return_value.json.side_effect = [mock_coingecko_search, mock_fdv_response]
    result = get_fully_diluted_valuation_tool("bitcoin")
    assert "The fully diluted valuation of bitcoin is $1,000,000,000,000" in result


def test_get_coin_market_cap_tool(mock_requests_get):
    mock_requests_get.return_value.json.side_effect = [
        mock_coingecko_search,
        mock_market_cap_response,
    ]
    result = get_coin_market_cap_tool("bitcoin")
    assert "The market cap of bitcoin is $500,000,000,000" in result
