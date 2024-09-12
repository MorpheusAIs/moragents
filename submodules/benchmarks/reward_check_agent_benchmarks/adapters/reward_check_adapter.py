from submodules.moragents_dockers.agents.src.claim_agent.src.tools import get_current_user_reward

class RewardCheckAdapter:
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return "RewardCheckAdapter"

    def get_reward(self, pool_id: int, wallet_address: str) -> float:
        return get_current_user_reward(wallet_address, pool_id)