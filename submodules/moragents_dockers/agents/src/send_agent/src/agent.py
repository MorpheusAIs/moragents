import asyncio
import json
import os
import logging
import traceback

from .config import Config

os.environ["ALCHEMY_API_KEY"] = Config.ALCHEMY_API_KEY

from autotx import AutoTx, LlamaClient
from autotx.AutoTx import Config as AutoTxConfig, CustomModel
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.wallets.smart_wallet import SmartWallet
from autotx.agents.SendTokensAgent import SendTokensAgent
from autotx.eth_address import ETHAddress
from web3 import Web3, HTTPProvider
from flask import jsonify

messages = []

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


def chat(request, llm):
    try:
        data = request.get_json()
        if "prompt" in data:
            prompt = data["prompt"]
            network = NetworkInfo.from_chain_id(data["chain_id"])
            w3 = Web3(HTTPProvider(network.get_subsidized_rpc_url()))
            wallet = SmartWallet(w3, ETHAddress(data["wallet_address"]))
            messages.append({"role": "user", "content": prompt})
            custom_model = CustomModel(client=LlamaClient, arguments={"llm": llm})
            autotx_config = AutoTxConfig(
                Config.VERBOSE, Config.LLM_CONFIG, None, custom_model=custom_model
            )
            autotx = AutoTx(w3, wallet, network, [SendTokensAgent()], autotx_config)
            result = autotx.run(prompt, True, summary_method="reflection_with_llm")
            transactions = asyncio.run(
                result.intents[0].build_transactions(w3, network, ETHAddress(data["wallet_address"]))
            )

            transaction_params = {
                "from": transactions[0].params["from"],
                "to": transactions[0].params["to"],
                "data": transactions[0].params["data"],
                "value": transactions[0].params["value"],
            }
            logging.info("Transaction to be executed in the frontend: ")
            logging.info(transaction_params)

            try:
                summary = json.loads(result.summary)
                if "content" in summary:
                    message = {"role": "assistant", "content": summary["content"]}
                    messages.append(message)
                    return jsonify(message)
            except:
                messages.append({"role": "assistant", "content": result.summary})
                return jsonify(result.summary)
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        logging.error("Exception occurred: %s", e)
        traceback.print_exc()
        return jsonify({"Error": str(e)}), 500


def get_messages():
    global messages
    return jsonify({"messages": messages})


def clear_messages():
    global messages
    messages = []
    return jsonify({"response": "successfully cleared message history"})
