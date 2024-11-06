import json
import logging

from src.agents.crypto_data import tools
from src.models.messages import ChatRequest

logger = logging.getLogger(__name__)


class CryptoDataAgent:
    def __init__(self, config, llm, embeddings):
        self.config = config
        self.llm = llm
        self.embeddings = embeddings
        self.tools_provided = tools.get_tools()

    def get_response(self, message):
        system_prompt = (
            "Don't make assumptions about the value of the arguments for the function "
            "they should always be supplied by the user and do not alter the value of the arguments. "
            "Don't make assumptions about what values to plug into functions. Ask for clarification if a user "
            "request is ambiguous."
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
                func_name = tool_call.get("name")
                args = tool_call.get("args")
                logger.info("LLM suggested using tool: %s", func_name)

                response_data = {"data": None, "coinId": None}

                if func_name == "get_price":
                    response_data["data"] = tools.get_coin_price_tool(args["coin_name"])
                    response_data["coinId"] = tools.get_tradingview_symbol(
                        tools.get_coingecko_id(args["coin_name"])
                    )
                    return response_data, "assistant"
                elif func_name == "get_floor_price":
                    response_data["data"] = tools.get_nft_floor_price_tool(
                        args["nft_name"]
                    )
                    return response_data, "assistant"
                elif func_name == "get_fdv":
                    response_data["data"] = tools.get_fully_diluted_valuation_tool(
                        args["coin_name"]
                    )
                    return response_data, "assistant"
                elif func_name == "get_tvl":
                    response_data["data"] = tools.get_protocol_total_value_locked_tool(
                        args["protocol_name"]
                    )
                    return response_data, "assistant"
                elif func_name == "get_market_cap":
                    response_data["data"] = tools.get_coin_market_cap_tool(
                        args["coin_name"]
                    )
                    return response_data, "assistant"
            else:
                logger.info("LLM provided a direct response without using tools")
                return {"data": result.content, "coinId": None}, "assistant"
        except Exception as e:
            logger.error(f"Error in get_response: {str(e)}")
            return {"data": f"An error occurred: {str(e)}", "coinId": None}, "assistant"

    def generate_response(self, prompt):
        response, role = self.get_response([prompt])
        return response, role

    def chat(self, request: ChatRequest):
        try:
            data = request.dict()
            if "prompt" in data:
                prompt = data["prompt"]
                logger.info(
                    "Received chat request with prompt: %s",
                    prompt[:50] + "..." if len(prompt) > 50 else prompt,
                )
                response, role = self.generate_response(prompt)
                return {"role": role, "content": response}
            else:
                logger.warning("Received chat request without 'prompt' in data")
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            logger.error("Error in chat method: %s", str(e), exc_info=True)
            return {"Error": str(e)}, 500
