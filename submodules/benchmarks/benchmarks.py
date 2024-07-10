import time
import argparse
from helpers import ask_data_agent, compare_usd_values, extract_agent_usd_value
from config import coins, price_prompts, mcap_prompts, price_error_tolerance, mcap_error_tolerance
from adapters.coingecko_adapter import CoingeckoAdapter
from adapters.defillama_adapter import DefillamaAdapter

all_adapters = [
    CoingeckoAdapter(),
    DefillamaAdapter(),]

parser = argparse.ArgumentParser(description="Specify the type of prompts to use (price or mcap).")
parser.add_argument('type', choices=['price', 'mcap'], help="Type of prompts to use")
args = parser.parse_args()

benchmark_type = args.type

if benchmark_type == 'price':
    prompts = price_prompts
    error_tolerance = price_error_tolerance
elif benchmark_type == 'mcap':
    prompts = mcap_prompts
    error_tolerance = mcap_error_tolerance

total_checks = 0
failures = []

try:
    print()
    for prompt in prompts:
        for coin in coins:
            coingecko_id = coin["coingecko_id"]
            for name in coin["names"]:
                llm_prompt = prompt.format(name)
                print(f"Checking {coingecko_id}: {llm_prompt}")
                try:
                    agent_response = ask_data_agent(prompt.format(name))
                    agent_usd_value = extract_agent_usd_value(agent_response)
                except:
                    agent_usd_value = None
                for adapter in all_adapters:
                    if benchmark_type == "price" and adapter.has_get_price():
                        try:
                            benchmark_value = adapter.get_price(coingecko_id)
                        except:
                            benchmark_value = None
                    elif benchmark_type == "mcap" and adapter.has_get_marketcap():
                        try:
                            benchmark_value = adapter.get_marketcap(coingecko_id)
                        except:
                            benchmark_value = None
                    result = compare_usd_values(agent_usd_value, coingecko_id, adapter, name, benchmark_value, error_tolerance, failures)
                    print(result)
                    total_checks += 1
                time.sleep(10) # must to be high for coingecko rate limits
                print()
    passed_checks = total_checks - len(failures)
    print()
    print(f"{passed_checks} / {total_checks} Benchmarks passed")

    if len(failures) > 0:
        print("Failures:")
        for failure in failures:
            print(failure)

except Exception as e:
    print(f"Unexpected error: {e}")
    exit(1)