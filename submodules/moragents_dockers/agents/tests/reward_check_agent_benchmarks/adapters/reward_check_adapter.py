from submodules.moragents_dockers.agents.src.claim_agent.src.tools import get_current_user_reward


class RewardCheckAdapter:
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return "RewardCheckAdapter"

    def get_rewards(self, wallet_address: str) -> dict:
        pool_0_reward = get_current_user_reward(wallet_address, 0)
        pool_1_reward = get_current_user_reward(wallet_address, 1)
        return {"pool_0_reward": pool_0_reward, "pool_1_reward": pool_1_reward}
