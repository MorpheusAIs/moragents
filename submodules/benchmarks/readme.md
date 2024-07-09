# Data Agent Benchmarking Tests

## About

- Measures how accurately the data agent responds for price & market cap vs benchmark values from coinecko, defillama, coincap, etc.

- Tests every combination of coins & prompts defined in `config.py` against each of the benchmark adapters.

## Running

## 1. Modify `config.py` with new prompts & coins (if needed)
## 2. Run `pip install -r requirements.txt`
## 2. Run `python benchmarks.py price` for price benchmarks or `python benchmarks.py mcap` for market cap

## Considerations

- The source of truth asset id is the coingecko id. Any new adapters will need some way of translating the coingecko id if they use something else. For example, the coincap doesn't use the same id format as coingecko and will need a translation layer (TODO).

- Disabling coingecko adapter lets us reduce the `time.sleep()` in `benchmarks.py` and run much faster (rate limiting).
