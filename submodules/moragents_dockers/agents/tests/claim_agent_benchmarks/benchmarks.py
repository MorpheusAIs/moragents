import pytest
from helpers import confirm_transaction, provide_receiver_address, request_claim

from submodules.moragents_dockers.agents.tests.claim_agent_benchmarks.config import Config


def test_claim_process():
    for i, wallet_data in enumerate(Config.WALLET_ADDRESSES):
        wallet_address = wallet_data["wallet"]
        receiver_address = wallet_data["receiver"]

        print(f"Testing for wallet {wallet_address} (Test {i + 1})")

        # Step 1: Request to claim rewards
        response = request_claim(wallet_address)
        assert "Please provide the receiver address" in response["content"]
        print(f"Step 1 passed for wallet {wallet_address}: Request to claim MOR rewards")

        # Step 2: Provide the receiver address
        response = provide_receiver_address(wallet_address, receiver_address)
        assert "Please confirm if you want to proceed" in response["content"]
        print(f"Step 2 passed for wallet {wallet_address}: Provided receiver address")

        # Step 3: Confirm the transaction
        response = confirm_transaction(wallet_address)
        assert "Transaction data prepared" in response["content"]
        print(f"Step 3 passed for wallet {wallet_address}: Transaction confirmed")


if __name__ == "__main__":
    pytest.main()
