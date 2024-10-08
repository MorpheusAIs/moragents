import json
from claim_agent.src import tools
from claim_agent.src.config import Config

class ClaimAgent:
    def __init__(self, agent_info, llm, llm_ollama, embeddings, flask_app):
        self.agent_info = agent_info
        self.llm = llm
        self.tools_provided = tools.get_tools()
        self.conversation_state = {}

    def get_response(self, message, wallet_address):
        if wallet_address not in self.conversation_state:
            self.conversation_state[wallet_address] = {"state": "initial"}

        state = self.conversation_state[wallet_address]["state"]

        if state == "initial":
            rewards = {
                0: tools.get_current_user_reward(wallet_address, 0),
                1: tools.get_current_user_reward(wallet_address, 1)
            }
            available_rewards = {pool: amount for pool, amount in rewards.items() if amount > 0}

            if available_rewards:
                selected_pool = max(available_rewards, key=available_rewards.get)
                self.conversation_state[wallet_address]["available_rewards"] = {selected_pool: available_rewards[selected_pool]}
                self.conversation_state[wallet_address]["receiver_address"] = wallet_address
                self.conversation_state[wallet_address]["state"] = "awaiting_confirmation"
                return f"You have {available_rewards[selected_pool]} MOR rewards available in pool {selected_pool}. Would you like to proceed with claiming these rewards?", "assistant", self.agent_info["name"]
            else:
                return f"No rewards found for your wallet address {wallet_address} in either pool. Claim cannot be processed.", "assistant", None

        elif state == "awaiting_confirmation":
            user_input = message[-1]['content'].lower()
            if any(word in user_input for word in ['yes', 'proceed', 'confirm', 'claim']):
                return self.prepare_transactions(wallet_address)
            else:
                return "Please confirm if you want to proceed with the claim by saying 'yes', 'proceed', 'confirm', or 'claim'.", "assistant", self.agent_info["name"]

        return "I'm sorry, I didn't understand that. Can you please rephrase your request?", "assistant", self.agent_info["name"]

    def prepare_transactions(self, wallet_address):
        available_rewards = self.conversation_state[wallet_address]["available_rewards"]
        receiver_address = self.conversation_state[wallet_address]["receiver_address"]
        transactions = []

        for pool_id in available_rewards.keys():
            try:
                tx_data = tools.prepare_claim_transaction(pool_id, receiver_address)
                transactions.append({"pool": pool_id, "transaction": tx_data})
            except Exception as e:
                return f"Error preparing transaction for pool {pool_id}: {str(e)}", "assistant", None

        self.conversation_state[wallet_address]["transactions"] = transactions
        tx_data_str = json.dumps(transactions, indent=2)
        return f"Transaction data prepared for signing:\n\n{tx_data_str}", "assistant", None

    def chat(self, request):
        try:
            data = request.get_json()
            if 'prompt' in data and 'wallet_address' in data:
                prompt = data['prompt']
                wallet_address = data['wallet_address']
                response, role, next_turn_agent = self.get_response([prompt], wallet_address)
                return {"role": role, "content": response, "next_turn_agent": next_turn_agent}
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            return {"Error": str(e)}, 500
