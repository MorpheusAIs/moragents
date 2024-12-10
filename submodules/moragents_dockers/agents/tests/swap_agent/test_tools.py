import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src", "swap_agent", "src"))
)
# The above sys/os lines are needed because the agents have identical namings (i.e. agent.py, tools.py)

from unittest.mock import MagicMock, patch

import pytest
from src.swap_agent.src.tools import (
    InsufficientFundsError,
    SwapNotPossibleError,
    TokenNotFoundError,
    convert_to_readable_unit,
    convert_to_smallest_unit,
    eth_to_wei,
    get_quote,
    get_token_balance,
    get_token_decimals,
    search_tokens,
    swap_coins,
    validate_swap,
)
from web3 import Web3


@pytest.fixture
def mock_web3():
    mock = MagicMock(spec=Web3)
    mock.eth = MagicMock()
    mock.eth.get_balance = MagicMock(return_value=1000)
    mock.eth.contract = MagicMock()
    return mock


def test_search_tokens():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"symbol": "ETH", "address": "0x123"}]
        result = search_tokens("ETH", 1)
        assert result[0]["symbol"] == "ETH"


def test_get_token_balance(mock_web3):
    mock_web3.eth.get_balance.return_value = 1000
    balance = get_token_balance(mock_web3, "0x456", "", [])
    assert balance == 1000


def test_eth_to_wei():
    assert eth_to_wei(1) == 10**18


def test_validate_swap(mock_web3):
    with patch("src.swap_agent.src.tools.search_tokens") as mock_search:
        mock_search.side_effect = [
            [{"symbol": "ETH", "address": "0x0000000000000000000000000000000000000000"}],
            [{"symbol": "DAI", "address": "0x123"}],
        ]
        mock_web3.eth.get_balance.return_value = 10**18
        result = validate_swap(mock_web3, "ETH", "DAI", 1, 1, "0x456")
        assert result[1] == "ETH"


def test_get_quote():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"dstAmount": "1000000000000000000"}
        result = get_quote("0x123", "0x456", 10**18, 1)
        assert result["dstAmount"] == "1000000000000000000"


def test_get_token_decimals(mock_web3):
    mock_contract = MagicMock()
    mock_contract.functions.decimals.return_value.call.return_value = 18
    mock_web3.eth.contract.return_value = mock_contract
    assert get_token_decimals(mock_web3, "0x1234567890123456789012345678901234567890") == 18


def test_convert_to_smallest_unit(mock_web3):
    with patch("src.swap_agent.src.tools.get_token_decimals", return_value=18):
        assert convert_to_smallest_unit(mock_web3, 1, "0x123") == 10**18


def test_convert_to_readable_unit(mock_web3):
    with patch("src.swap_agent.src.tools.get_token_decimals", return_value=18):
        assert convert_to_readable_unit(mock_web3, 10**18, "0x123") == 1


def test_swap_coins():
    with patch("src.swap_agent.src.tools.Web3") as mock_web3, patch(
        "src.swap_agent.src.tools.validate_swap"
    ) as mock_validate, patch("src.swap_agent.src.tools.get_quote") as mock_quote:

        mock_web3.return_value = MagicMock()
        mock_validate.return_value = ("0x123", "ETH", "0x456", "DAI")
        mock_quote.return_value = {"dstAmount": "1000000000000000000"}

        result, role = swap_coins("ETH", "DAI", 1, 1, "0x789")
        assert result["src"] == "ETH"
        assert result["dst"] == "DAI"
        assert role == "swap"


def test_swap_coins_insufficient_funds():
    with patch("src.swap_agent.src.tools.Web3") as mock_web3, patch(
        "src.swap_agent.src.tools.validate_swap"
    ) as mock_validate:

        mock_web3.return_value = MagicMock()
        mock_validate.side_effect = InsufficientFundsError("Not enough funds")

        with pytest.raises(InsufficientFundsError):
            swap_coins("ETH", "DAI", 1000, 1, "0x789")


def test_swap_coins_token_not_found():
    with patch("src.swap_agent.src.tools.Web3") as mock_web3, patch(
        "src.swap_agent.src.tools.validate_swap"
    ) as mock_validate:

        mock_web3.return_value = MagicMock()
        mock_validate.side_effect = TokenNotFoundError("Token not found")

        with pytest.raises(TokenNotFoundError):
            swap_coins("UNKNOWN", "DAI", 1, 1, "0x789")


def test_swap_coins_swap_not_possible():
    with patch("src.swap_agent.src.tools.Web3") as mock_web3, patch(
        "src.swap_agent.src.tools.validate_swap"
    ) as mock_validate, patch("src.swap_agent.src.tools.get_quote") as mock_quote:

        mock_web3.return_value = MagicMock()
        mock_validate.return_value = ("0x123", "ETH", "0x456", "DAI")
        mock_quote.return_value = None

        with pytest.raises(SwapNotPossibleError):
            swap_coins("ETH", "DAI", 1, 1, "0x789")
