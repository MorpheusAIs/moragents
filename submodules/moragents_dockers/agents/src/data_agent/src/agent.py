import json
from data_agent.src import tools


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
                )
            }
        ]
        messages.extend(message)
        result = self.llm.create_chat_completion(
            messages=messages,
            tools=self.tools_provided,
            tool_choice="auto"
        )
        if "tool_calls" in result["choices"][0]["message"].keys():
            func = result["choices"][0]["message"]["tool_calls"][0]['function']
            if func["name"] == 'get_price':
                args = json.loads(func["arguments"])
                return tools.get_coin_price_tool(args['coin_name']), "assistant"
            elif func["name"] == 'get_floor_price':
                args = json.loads(func["arguments"])
                return tools.get_nft_floor_price_tool(args['nft_name']), "assistant"
            elif func["name"] == 'get_fdv':
                args = json.loads(func["arguments"])
                return tools.get_fully_diluted_valuation_tool(args['coin_name']), "assistant"
            elif func["name"] == 'get_tvl':
                args = json.loads(func["arguments"])
                return tools.get_protocol_total_value_locked_tool(args['protocol_name']), "assistant"
            elif func["name"] == 'get_market_cap':
                args = json.loads(func["arguments"])
                return tools.get_coin_market_cap_tool(args['coin_name']), "assistant"
        return result["choices"][0]["message"]['content'], "assistant"

    def generate_response(self, prompt):
        response, role = self.get_response([prompt])
        return response, role

    def chat(self, request):
        try:
            data = request.get_json()
            if 'prompt' in data:
                prompt = data['prompt']
                response, role = self.generate_response(prompt)
                return {"role": role, "content": response}
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            return {"Error": str(e)}, 500
