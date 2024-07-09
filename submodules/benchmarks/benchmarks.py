import time
import argparse
from helpers import ask_data_llm, check_response, extract_agent_usd_value
from config import coins, price_prompts, mcap_prompts, price_error_tolerance, mcap_error_tolerance
from adapters.coingecko_adapter import CoingeckoAdapter
from adapters.defillama_adapter import DefillamaAdapter
from adapters.coincap_adapter import CoincapAdapter

# Define all adapters
all_adapters = [
    CoingeckoAdapter(),
    DefillamaAdapter(),
    CoincapAdapter()
]

# Argument parsing
parser = argparse.ArgumentParser(description="Specify the type of prompts to use (price or mcap).")
parser.add_argument('type', choices=['price', 'mcap'], help="Type of prompts to use")
args = parser.parse_args()

benchmark_type = args.type

# Set prompts based on the specified type
if benchmark_type == 'price':
    prompts = price_prompts
elif benchmark_type == 'mcap':
    prompts = mcap_prompts

try:
    print()
    for prompt in prompts:
        for coin in coins:
            coingecko_id = coin["coingecko_id"]
            for name in coin["names"]:
                llm_prompt = prompt.format(name)
                print(f"Checking {coingecko_id}: {llm_prompt}")
                agent_response = ask_data_llm(prompt.format(name))
                agent_usd_value = extract_agent_usd_value(agent_response)
                for adapter in all_adapters:
                    if benchmark_type == "price" and adapter.has_get_price():
                        benchmark_value = adapter.get_price(coingecko_id)
                        error_tolerance = price_error_tolerance
                    elif benchmark_type == "mcap" and adapter.has_get_marketcap():
                        benchmark_value = adapter.get_marketcap(coingecko_id)
                        error_tolerance = price_error_tolerance
                    check_response(agent_usd_value, coingecko_id, adapter, name, benchmark_value, error_tolerance)
                time.sleep(10) # must to be high for coingecko rate limits
                print()
except Exception as e:
    print(f"Unexpected error: {e}")
    exit(1)