from src.agents.mor_rewards.config import Config
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
        }
    ]
