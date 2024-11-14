import json
import requests
import logging

from src.agents.token_swap import tools
from src.agents.token_swap.config import Config
from src.models.messages import ChatRequest
from src.stores import agent_manager

logger = logging.getLogger(__name__)


class TokenSwapAgent:
    def __init__(self, config, llm, embeddings):
        self.config = Config.get_instance()
        self.llm = llm
        self.embeddings = embeddings
        self.tools_provided = tools.get_tools()
        self.context = []

    async def set_inch_api_key(self, request):
        try:
            if isinstance(request, dict):
                data = request
            else:
                data = await request.json()
            
            if "inch_api_key" not in data:
                logger.warning("Missing required API credentials")
                return {"error": "Missing 1inch API key"}, 400

            self.config.inch_api_key = data["inch_api_key"]
            logger.info("1inch API key saved successfully")
            
            return {"success": "1inch API key saved successfully"}, 200
            
        except Exception as e:
            logger.error(f"Error setting 1inch API key: {e}")
            return {"error": str(e)}, 500

    def api_request_url(self, method_name, query_params, chain_id):
        """Build 1inch API request URL with parameters"""
        base_url = f"{self.config.APIBASEURL}{chain_id}"
        param_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
        return f"{base_url}{method_name}?{param_string}"

    def check_allowance(self, token_address, wallet_address, chain_id):
        url = self.api_request_url(
            "/approve/allowance",
            {"tokenAddress": token_address, "walletAddress": wallet_address},
            chain_id,
        )
        response = requests.get(url, headers=tools.get_headers())
        data = response.json()
        return data

    def approve_transaction(self, token_address, chain_id, amount=None):
        query_params = (
            {"tokenAddress": token_address, "amount": amount}
            if amount
            else {"tokenAddress": token_address}
        )
        url = self.api_request_url("/approve/transaction", query_params, chain_id)
        response = requests.get(url, headers=tools.get_headers())
        transaction = response.json()
        return transaction

    def build_tx_for_swap(self, swap_params, chain_id):
        """Build swap transaction using stored API key"""
        url = self.api_request_url("/swap", swap_params, chain_id)
        logger.debug(f"Swap request URL: {url}")
        
        response = requests.get(url, headers=tools.get_headers())
        if response.status_code != 200:
            logger.error(f"1inch API error: {response.text}")
            raise ValueError(f"1inch API error: {response.text}")
            
        raw_swap_transaction = response.json()
        return raw_swap_transaction

    def get_response(self, message, chain_id, wallet_address):
        if not self.config.inch_api_key:
            return "Please set your 1inch API key in Settings before making swap requests.", "assistant", None

        system_message = """You are a helpful assistant that processes token swap requests. 
        When a user wants to swap tokens, analyze their request and provide a SINGLE tool call with complete information.
        
        Always return a single 'swap_agent' tool call with all three required parameters:
        - token1: the source token
        - token2: the destination token
        - value: the amount to swap
        
        If any information is missing from the user's request, do not make a tool call. Instead, respond asking for the missing information."""

        messages = [
            {"role": "system", "content": system_message}
        ]
        messages.extend(message)
        
        llm_with_tools = self.llm.bind_tools(self.tools_provided)

        try:
            result = llm_with_tools.invoke(messages)
            
            if not result.tool_calls:
                self.context = []  # Clear context when asking for info
                return "Please specify the tokens you want to swap and the amount.", "assistant", None

            # Get the most complete tool call
            tool_call = max(result.tool_calls, 
                           key=lambda x: sum(1 for v in x.get("args", {}).values() if v))
            
            args = tool_call.get("args", {})
            tok1 = args.get("token1")
            tok2 = args.get("token2")
            value = args.get("value")
            
            if not all([tok1, tok2, value]):
                self.context = []  # Clear context when asking for missing params
                return "Please specify both tokens and the amount you want to swap.", "assistant", None

            try:
                logger.info(f"Processing swap: {tok1} -> {tok2}, amount: {value}")
                res, role = tools.swap_coins(tok1, tok2, value, chain_id, wallet_address)
                if "error" in res:
                    return res["error"], "assistant", None
                return res, role, None
            except (tools.InsufficientFundsError, tools.TokenNotFoundError, tools.SwapNotPossibleError) as e:
                self.context = []
                return str(e), "assistant", None
            
        except Exception as e:
            logger.error("Error in get_response: %s", str(e))
            self.context = []
            return f"Sorry, there was an error processing your request: {str(e)}", "assistant", None

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
            self.context.append(
                {"role": "user", "content": "okay lets start again from scratch"}
            )

        return {"role": "assistant", "content": response}

    def generate_response(self, prompt, chain_id, wallet_address):
        self.context.append(prompt)
        response, role, next_turn_agent = self.get_response(
            self.context, chain_id, wallet_address
        )
        return response, role, next_turn_agent

    def chat(self, chat_request: ChatRequest):
        try:
            if "prompt" in chat_request.dict():
                prompt = chat_request.prompt.dict()
                chain_id = chat_request.chain_id
                wallet_address = chat_request.wallet_address
                
                response, role, next_turn_agent = self.generate_response(
                    prompt, chain_id, wallet_address
                )
                return {
                    "role": role,
                    "content": response,
                    "next_turn_agent": next_turn_agent
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
                return res
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
