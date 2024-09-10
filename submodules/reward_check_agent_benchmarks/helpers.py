import requests
import json
import re
from web3 import Web3
from config import Config

url = 'http://127.0.0.1:5000/'

headers = {
    'Content-Type': 'application/json',
}

def ask_claim_agent(prompt: str):
    payload = {
        "prompt": {
            "role": "user",
            "content": prompt
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['content']
    else:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

def get_current_user_reward(wallet_address, pool_id):
    web3 = Web3(Web3.HTTPProvider(Config.WEB3RPCURL["1"]))
    distribution_contract = web3.eth.contract(
            address=web3.to_checksum_address(Config.DISTRIBUTION_PROXY_ADDRESS),
            abi=Config.DISTRIBUTION_ABI
    )

    try:
        if not web3.is_connected():
            raise Exception("Unable to connect to Ethereum network")

        reward = distribution_contract.functions.getCurrentUserReward(
            pool_id,
            web3.to_checksum_address(wallet_address)
        ).call()
        formatted_reward = web3.from_wei(reward, 'ether')
        return round(formatted_reward, 4)
    except Exception as e:
        raise Exception(f"Error occurred while fetching the reward: {str(e)}")

def extract_reward_value_from_response(response: str) -> float:
    match = re.search(r'(\d+\.\d+) MOR', response)
    if match:
        return float(match.group(1))
    raise ValueError("Could not extract a reward value from the agent's response")
