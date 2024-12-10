import pytest

from submodules.benchmarks.claim_agent_benchmarks.helpers import request_claim
from submodules.moragents_dockers.agents.tests.claim_agent_benchmarks.config import Config


def test_claim_process():
    for i, wallet_data in enumerate(Config.WALLET_ADDRESSES):
        wallet_address = wallet_data["wallet"]

        print(f"Testing for wallet {wallet_address} (Test {i + 1})")

        # Step 1: Request to claim rewards
        response = request_claim(wallet_address)

        # Check if the response contains the expected structure
        assert "role" in response
        assert response["role"] == "claim"
        assert "content" in response
        assert isinstance(response["content"], dict)
        assert "content" in response["content"]
        assert "transactions" in response["content"]["content"]
        assert len(response["content"]["content"]["transactions"]) > 0

        transaction = response["content"]["content"]["transactions"][0]
        assert "pool" in transaction
        assert "transaction" in transaction

        tx_data = transaction["transaction"]
        assert all(key in tx_data for key in ["to", "data", "value", "gas", "chainId"])

        # Additional specific checks
        assert (
            tx_data["to"] == "0x47176B2Af9885dC6C4575d4eFd63895f7Aaa4790"
        ), "Incorrect 'to' address"
        assert tx_data["value"] == "1000000000000000", "Incorrect 'value'"
        assert tx_data["chainId"] == "1", "Incorrect 'chainId'"

        print(f"Step 1 passed for wallet {wallet_address}: Claim process triggered successfully")

        print(f"All steps passed for wallet {wallet_address}")


if __name__ == "__main__":
    pytest.main()
