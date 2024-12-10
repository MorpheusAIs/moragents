import json
import re

import requests
from adapters.base_adapter import BaseAdapter

url = "http://127.0.0.1:8080/data_agent/"

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "http://localhost:3333",
    "Referer": "http://localhost:3333/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}


def ask_data_agent(prompt: str):
    payload = {"prompt": {"role": "user", "content": prompt}}

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    result_content = response.json()["content"]
    return result_content


def extract_agent_usd_value(content: str):
    match = re.search(r"\$\d+(?:,\d{3})*(?:\.\d{1,8})?", content)  # 8 usd digits should be plenty
    if match:
        price_str = match.group(0).replace("$", "").replace(",", "")
        return float(price_str)
    raise ValueError("Could not extract a price from the agent response")


def compare_usd_values(
    agent_value: float,
    adapter: BaseAdapter,
    coingecko_id: str,
    name_variation: str,
    benchmark_value: float,
    error_tolerance: float,
    failures: list,
):
    difference = abs(agent_value - benchmark_value)
    percent_difference = (difference / benchmark_value) * 100
    result_value = f"${benchmark_value:.8f}, {percent_difference:.2f}% off"
    if percent_difference <= error_tolerance * 100:
        result_message = f"PASS {adapter.name}. {result_value}"
    else:
        result_message = f"FAIL {adapter.name}. {result_value}"
        failure_message = f"FAIL {adapter.name}. {result_value}. {coingecko_id}. {name_variation}"  # so we have more information to summarize failures at the end
        failures.append(result_message)
    return result_message
