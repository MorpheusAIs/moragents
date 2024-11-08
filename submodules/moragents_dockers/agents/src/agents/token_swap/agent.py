import json
import logging

import requests
from src.agents.token_swap import tools
from src.agents.token_swap.config import Config
from src.models.messages import ChatRequest
from src.stores import agent_manager

logger = logging.getLogger(__name__)


class TokenSwapAgent:
    def __init__(self, config, llm, embeddings):
        self.config = config
        self.llm = llm
        self.embeddings = embeddings
        self.tools_provided = tools.get_tools()
        self.context = []

    def api_request_url(self, method_name, query_params, chain_id):
        base_url = Config.APIBASEURL + str(chain_id)
        return f"{base_url}{method_name}?{'&'.join([f'{key}={value}' for key, value in query_params.items()])}"

    def check_allowance(self, token_address, wallet_address, chain_id):
        url = self.api_request_url(
            "/approve/allowance",
            {"tokenAddress": token_address, "walletAddress": wallet_address},
            chain_id,
        )
        response = requests.get(url, headers=Config.HEADERS)
        data = response.json()
        return data

    def approve_transaction(self, token_address, chain_id, amount=None):
        query_params = (
            {"tokenAddress": token_address, "amount": amount}
            if amount
            else {"tokenAddress": token_address}
        )
        url = self.api_request_url("/approve/transaction", query_params, chain_id)
        response = requests.get(url, headers=Config.HEADERS)
        transaction = response.json()
        return transaction

    def build_tx_for_swap(self, swap_params, chain_id):
        url = self.api_request_url("/swap", swap_params, chain_id)
        swap_transaction = requests.get(url, headers=Config.HEADERS).json()
        return swap_transaction

    def get_response(self, message, chain_id, wallet_address):
        system_prompt = (
            "Don't make assumptions about the value of the arguments for the function "
            "they should always be supplied by the user and do not alter the value of the arguments. "
            "Don't make assumptions about what values to plug into functions. Ask for clarification if a user "
            "request is ambiguous. you only need the value of token1 we dont need the value of token2. After "
            "starting from scratch do not assume the name of token1 or token2"
        )

        messages = [
            {"role": "system", "content": system_prompt},
        ]
        messages.extend(message)

        logger.info("Sending request to LLM with %d messages", len(messages))

        llm_with_tools = self.llm.bind_tools(self.tools_provided)

        try:
            result = llm_with_tools.invoke(messages)
            logger.info("Received response from LLM: %s", result)

            if result.tool_calls:
                tool_call = result.tool_calls[0]
                logger.info("Selected tool: %s", tool_call)
                func_name = tool_call.get("name")
                args = tool_call.get("args")
                logger.info("LLM suggested using tool: %s", func_name)

                if func_name == "swap_agent":
                    tok1 = args["token1"]
                    tok2 = args["token2"]
                    value = args["value"]
                    try:
                        res, role = tools.swap_coins(
                            tok1, tok2, float(value), chain_id, wallet_address
                        )
                    except (
                        tools.InsufficientFundsError,
                        tools.TokenNotFoundError,
                        tools.SwapNotPossibleError,
                    ) as e:
                        self.context = []
                        return str(e), "assistant", None
                    return res, role, None
            else:
                logger.info("LLM provided a direct response without using tools")
                return result.content, "assistant", "crypto swap agent"
        except Exception as e:
            logger.error(f"Error in get_response: {str(e)}")
            return f"An error occurred: {str(e)}", "assistant", None

    def get_status(self, flag, tx_hash, tx_type):
        response = ""

        if flag == "cancelled":
            response = f"The {tx_type} transaction has been cancelled."
        elif flag == "success":
            response = f"The {tx_type} transaction was successful."
        elif flag == "failed":
            response = f"The {tx_type} transaction has failed."
        elif flag == "initiated":
            response = f"Transaction has been sent, please wait for it to be confirmed."

        if tx_hash:
            response = response + f" The transaction hash is {tx_hash}."

        if flag == "success" and tx_type == "approve":
            response = response + " Please proceed with the swap transaction."
        elif flag != "initiated":
            response = response + " Is there anything else I can help you with?"

        if flag != "initiated":
            self.context = []
            self.context.append({"role": "assistant", "content": response})
            self.context.append({"role": "user", "content": "okay lets start again from scratch"})

        return {"role": "assistant", "content": response}

    def generate_response(self, prompt, chain_id, wallet_address):
        self.context.append(prompt)
        response, role, next_turn_agent = self.get_response(self.context, chain_id, wallet_address)
        return response, role, next_turn_agent

    def chat(self, request: ChatRequest):
        data = request.dict()
        try:
            if "prompt" in data:
                prompt = data["prompt"]
                wallet_address = data["wallet_address"]
                chain_id = data["chain_id"]
                response, role, next_turn_agent = self.generate_response(
                    prompt, chain_id, wallet_address
                )
                return {
                    "role": role,
                    "content": response,
                    "next_turn_agent": next_turn_agent,
                }
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            return {"Error": str(e)}, 500

    def tx_status(self, data):
        try:
            if "status" in data:
                prompt = data["status"]
                tx_hash = data.get("tx_hash", "")
                tx_type = data.get("tx_type", "")
                response = self.get_status(prompt, tx_hash, tx_type)
                return response
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            return {"Error": str(e)}, 500

    def get_allowance(self, request_data):
        try:
            if "tokenAddress" in request_data:
                token = request_data["tokenAddress"]
                wallet_address = request_data["walletAddress"]
                chain_id = request_data["chain_id"]
                res = self.check_allowance(token, wallet_address, chain_id)
                return {"response": res}
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            return {"Error": str(e)}, 500

    def approve(self, request_data):
        try:
            if "tokenAddress" in request_data:
                token = request_data["tokenAddress"]
                chain_id = request_data["chain_id"]
                amount = request_data["amount"]
                res = self.approve_transaction(token, chain_id, amount)
                return {"response": res}
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            return {"Error": str(e)}, 500

    def swap(self, request_data):
        try:
            if "src" in request_data:
                token1 = request_data["src"]
                token2 = request_data["dst"]
                wallet_address = request_data["walletAddress"]
                amount = request_data["amount"]
                slippage = request_data["slippage"]
                chain_id = request_data["chain_id"]
                swap_params = {
                    "src": token1,
                    "dst": token2,
                    "amount": amount,
                    "from": wallet_address,
                    "slippage": slippage,
                    "disableEstimate": False,
                    "allowPartialFill": False,
                }
                swap_transaction = self.build_tx_for_swap(swap_params, chain_id)
                return swap_transaction
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            return {"Error": str(e)}, 500
