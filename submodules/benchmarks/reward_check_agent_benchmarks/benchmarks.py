from helpers import ask_claim_agent, get_current_user_reward, extract_reward_value_from_response
from submodules.benchmarks.reward_check_agent_benchmarks.config import test_cases, reward_check_prompts


def run_reward_check_tests():
    total_tests = len(test_cases)
    passed_tests = 0

    for i, test_case in enumerate(test_cases, 1):
        pool_id = test_case["pool_id"]
        wallet_address = test_case["wallet_address"]

        # Iterate over each prompt
        for prompt_template in reward_check_prompts:
            prompt = prompt_template.format(wallet_address, pool_id)
            print("-" * 100)
            print(f"Running test case {i}/{total_tests}: {prompt}")

            # Get the agent's response
            agent_response = ask_claim_agent(prompt)
            print(f"Agent response: {agent_response}")

            # Extract the reward value from the agent's response
            agent_reward_value = extract_reward_value_from_response(agent_response)
            print(f"Agent Returned Reward Value: {agent_reward_value}")

            # Get the real reward value from the blockchain
            blockchain_reward_value = float(get_current_user_reward(wallet_address, pool_id))
            print(f"Blockchain Returned Reward Value: {blockchain_reward_value}")

            # Compare the values with a tolerance of 10%
            tolerance = 0.10
            if abs(agent_reward_value - blockchain_reward_value) / blockchain_reward_value <= tolerance:
                print(f"Test case {i} passed.")
                passed_tests += 1
                i += 1
                print("-" * 100)
            else:
                print(f"Test case {i} failed. Agent returned {agent_reward_value}, expected {blockchain_reward_value}.")
                print("-" * 100)
                i += 1

    print(f"\n{passed_tests}/{total_tests} test cases passed.")


if __name__ == "__main__":
    run_reward_check_tests()
