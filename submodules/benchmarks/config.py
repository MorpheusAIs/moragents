loop_delay = 10 # prevent rate limiting

price_error_tolerance = 0.01 # 1%
mcap_error_tolerance = 0.01 # 1%
coins = [
    {
        "coingecko_id": "bitcoin",
        "name_variations": ["bitcoin", "Bit coin", "btc_expected_to_fail"]
    },
    {
        "coingecko_id": "litecoin",
        "name_variations": ["litecoin", "ltc"]
    },
    {
        "coingecko_id": "ripple",
        "name_variations": ["ripple", "xrp"]
    },
    {
        "coingecko_id": "gecko_id_expected_to_fail",
        "name_variations": ["bitcoin"]
    },
]

price_prompts = [
    "What is the price of {}?",
    "How much does {} cost?",
]

mcap_prompts = [
    "What is the market capitalization of {}?",
    "Whats {}'s market cap?",
]
