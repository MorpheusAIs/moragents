from src.agents.mor_claims.config import Config
from web3 import Web3


def get_current_user_reward(wallet_address, pool_id):
    web3 = Web3(Web3.HTTPProvider(Config.WEB3RPCURL["1"]))
    distribution_contract = web3.eth.contract(
        address=web3.to_checksum_address(Config.DISTRIBUTION_PROXY_ADDRESS),
        abi=Config.DISTRIBUTION_ABI,
    )

    try:
        if not web3.is_connected():
            raise Exception("Unable to connect to Ethereum network")

        reward = distribution_contract.functions.getCurrentUserReward(
            pool_id, web3.to_checksum_address(wallet_address)
        ).call()
        formatted_reward = web3.from_wei(reward, "ether")
        return round(formatted_reward, 4)
    except Exception as e:
        raise Exception(f"Error occurred while fetching the reward: {str(e)}")


def prepare_claim_transaction(pool_id, wallet_address):
    try:
        web3 = Web3(Web3.HTTPProvider(Config.WEB3RPCURL["1"]))
        contract = web3.eth.contract(
            address=web3.to_checksum_address(Config.DISTRIBUTION_PROXY_ADDRESS),
            abi=Config.DISTRIBUTION_ABI,
        )
        tx_data = contract.encode_abi(
            fn_name="claim", args=[pool_id, web3.to_checksum_address(wallet_address)]
        )
        mint_fee = web3.to_wei(Config.MINT_FEE, "ether")
        estimated_gas = contract.functions.claim(
            pool_id, web3.to_checksum_address(wallet_address)
        ).estimate_gas({"from": web3.to_checksum_address(wallet_address), "value": mint_fee})
        return {
            "to": Config.DISTRIBUTION_PROXY_ADDRESS,
            "data": tx_data,
            "value": str(mint_fee),
            "gas": str(estimated_gas),
            "chainId": "1",
        }
    except Exception as e:
        raise Exception(f"Failed to prepare claim transaction: {str(e)}")


def get_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "get_current_user_reward",
                "description": "Fetch the token amount of currently accrued MOR rewards for a user address from a specific pool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "wallet_address": {
                            "type": "string",
                            "description": "The wallet address to check rewards for",
                        },
                        "pool_id": {
                            "type": "integer",
                            "description": "The ID of the pool to check rewards from",
                        },
                    },
                    "required": ["wallet_address", "pool_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "prepare_claim_transaction",
                "description": "Prepare a transaction to claim rewards",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pool_id": {
                            "type": "integer",
                            "description": "The ID of the pool to claim from",
                        },
                        "wallet_address": {
                            "type": "string",
                            "description": "The wallet address to claim rewards for",
                        },
                    },
                    "required": ["pool_id", "wallet_address"],
                },
            },
        },
    ]
