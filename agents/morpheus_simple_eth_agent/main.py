from chains_and_agents.morpheus_chain import process_nlq


if __name__ == "__main__":
    NLQ = "I'd like to send 0.01ETH to 0x000000000000000000000000 on arbitrum"  # This can be replaced with an input() or command line arguments (CLI args)

    result = process_nlq(NLQ)

    print(result)
