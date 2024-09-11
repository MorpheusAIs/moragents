import json
import logging
from data_agent.src import tools

logger = logging.getLogger(__name__)


class DataAgent:
    def __init__(self, config, llm, llm_ollama, embeddings, flask_app):
        self.llm = llm
        self.flask_app = flask_app
        self.config = config
        self.tools_provided = tools.get_tools()

    def get_response(self, message):
        messages = [
            {
                "role": "system",
                "content": (
                    "Don't make assumptions about the value of the arguments for the function "
                    "they should always be supplied by the user and do not alter the value of the arguments. "
                    "Don't make assumptions about what values to plug into functions. Ask for clarification if a user "
                    "request is ambiguous."
                ),
            }
        ]
        messages.extend(message)
        try:
            result = self.llm.create_chat_completion(
                messages=messages, tools=self.tools_provided, tool_choice="auto"
            )

            if not result["choices"]:
                logger.error("No choices in LLM response")
                return (
                    "I'm sorry, but I couldn't generate a response. Please try again.",
                    "assistant",
                )

            choice = result["choices"][0]["message"]

            if "tool_calls" in choice:
                func = choice["tool_calls"][0]["function"]
                args = json.loads(func["arguments"])

                if func["name"] == "get_price":
                    return tools.get_coin_price_tool(args["coin_name"]), "assistant"
                elif func["name"] == "get_floor_price":
                    return tools.get_nft_floor_price_tool(args["nft_name"]), "assistant"
                elif func["name"] == "get_fdv":
                    return (
                        tools.get_fully_diluted_valuation_tool(args["coin_name"]),
                        "assistant",
                    )
                elif func["name"] == "get_tvl":
                    return (
                        tools.get_protocol_total_value_locked_tool(
                            args["protocol_name"]
                        ),
                        "assistant",
                    )
                elif func["name"] == "get_market_cap":
                    return (
                        tools.get_coin_market_cap_tool(args["coin_name"]),
                        "assistant",
                    )

            return (
                choice.get(
                    "content",
                    "I'm sorry, but I couldn't generate a response. Please try again.",
                ),
                "assistant",
            )

        except Exception as e:
            logger.error(f"Error in get_response: {str(e)}")
            return (
                "I'm sorry, but an error occurred while processing your request. Please try again.",
                "assistant",
            )

    def generate_response(self, prompt):
        return self.get_response([prompt])

    def chat(self, request):
        try:
            data = request.get_json()
            if "prompt" in data:
                prompt = data["prompt"]
                response, role = self.generate_response(prompt)
                return {"role": role, "content": response}
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return {
                "role": "assistant",
                "content": "I'm sorry, but an error occurred while processing your request. Please try again.",
            }
