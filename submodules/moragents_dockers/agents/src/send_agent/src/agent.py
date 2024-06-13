import os
import logging
from .config import Config

os.environ["ALCHEMY_API_KEY"] = Config.ALCHEMY_API_KEY

from autotx import AutoTx
from autotx.AutoTx import Config as AutoTxConfig
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.wallets.smart_wallet import SmartWallet
from autotx.agents.SendTokensAgent import SendTokensAgent
from autotx.utils.ethereum.eth_address import ETHAddress
from web3 import Web3, HTTPProvider
from flask import jsonify

available_agents = [SendTokensAgent()]
autotx_config = AutoTxConfig(Config.VERBOSE, Config.LLM_CONFIG, None)

messages = []


def chat(request, llm):
    try:
        data = request.get_json()
        if "prompt" in data:
            prompt = data["prompt"]
            network = NetworkInfo.from_chain_id(data["chain_id"])
            rpc_url = network.get_subsidized_rpc_url()
            w3 = Web3(HTTPProvider(rpc_url))
            wallet = SmartWallet(w3, ETHAddress(data["wallet_address"]))
            messages.append({"role": "user", "content": prompt})
            autotx = AutoTx(w3, wallet, network, available_agents, autotx_config)
            result = autotx.run(prompt, True, "reflection_with_llm")
            logging.info(result.transactions)
            messages.append({"role": "assistant", "content": result.summary})
            return jsonify({"role": "assistant", "content": result.summary})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500


def get_messages():
    global messages
    return jsonify({"messages": messages})


def clear_messages():
    global messages
    messages = []
    return jsonify({"response": "successfully cleared message history"})
