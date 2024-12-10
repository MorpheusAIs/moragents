import re

import requests
from web3 import Web3

from submodules.benchmarks.reward_check_agent_benchmarks.config import Config

url = "http://127.0.0.1:5000/"

headers = {
    "Content-Type": "application/json",
}


def ask_claim_agent(prompt: str, wallet_address: str):
    payload = {
        "prompt": {"role": "user", "content": prompt},
        "wallet_address": wallet_address,  # Adding the wallet address in the payload
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["content"]
    else:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")


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


def extract_reward_value_from_response(response: str) -> dict:
    # Regex to extract rewards for both pools; adjusted to be more flexible
    matches = re.findall(
        r"Capital Providers Pool \(Pool 0\):\s*([\d.]+)\s*MOR.*?Code Providers Pool \(Pool 1\):\s*([\d.]+)\s*MOR",
        response,
        re.DOTALL,
    )

    rewards = {}
    if matches:
        # Assuming the first match group corresponds to pool 0 and the second to pool 1
        rewards["pool_0_reward"] = float(matches[0][0])
        rewards["pool_1_reward"] = float(matches[0][1])

    return rewards
