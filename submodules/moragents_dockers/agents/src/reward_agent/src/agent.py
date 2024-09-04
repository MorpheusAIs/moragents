import json
from reward_agent.src import tools


class RewardAgent:
    def __init__(self, agent_info, llm, llm_ollama, embeddings, flask_app):
        self.agent_info = agent_info
        self.llm = llm
        self.llm_ollama = llm_ollama
        self.embeddings = embeddings
        self.flask_app = flask_app
        self.tools_provided = tools.get_tools()

    def get_response(self, message):
        prompt = [
            {
                "role": "system",
                "content": (
                    "You are a reward checking agent. Your task is to help users check their MOR rewards accrued in either pool 0"
                    "(capital providers pool) or pool 1 (code providers pool). "
                    "You will facilitate the checking of their currently accrued rewards from the pool they mention and for the address they specify to check for. "
                    "Extract the pool ID from the user's message: "
                    "If the user mentions the capital pool, interpret it as pool ID 0. "
                    "If the user mentions the code pool, interpret it as pool ID 1. "
                    "Ask the user for the pool ID and the address they want to check their accrued rewards for. Note that these parameters are mandatory for the user to answer. "
                    "Use the `get_current_user_reward` function to fetch the currently accrued MOR rewards using the pool ID and address provided by the user."
                    "Remember that the value to be passed for pool_id in the `get_current_user_reward` function will be an integer - either 0 or 1 "
                )
            }
        ]
        prompt.extend(message)
        result = self.llm.create_chat_completion(
            messages=prompt,
            tools=self.tools_provided,
            tool_choice="auto",
            temperature=0.01
        )
        if "tool_calls" in result["choices"][0]["message"].keys():
            func = result["choices"][0]["message"]["tool_calls"][0]['function']
            if func["name"] == "get_current_user_reward":
                args = json.loads(func["arguments"])
                try:
                    reward = tools.get_current_user_reward(args['wallet_address'], args['pool_id'])
                    return f"The current reward for wallet {args['wallet_address']} in pool {args['pool_id']} is {reward} MOR", "assistant", None
                except Exception as e:
                    return str(e), "assistant", None
        return result["choices"][0]["message"]['content'], "assistant", "reward agent"

    def chat(self, request):
        try:
            data = request.get_json()
            if 'prompt' in data:
                prompt = data['prompt']
                response, role, next_turn_agent = self.get_response([prompt])

                # Check if we need more information
                if "What is the wallet address?" in response or "What is the pool ID?" in response:
                    next_turn_agent = self.agent_info["name"]  # Continue the conversation
                else:
                    next_turn_agent = None  # End the conversation

                return {"role": role, "content": response, "next_turn_agent": next_turn_agent}
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            return {"Error": str(e)}, 500