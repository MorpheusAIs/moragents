# Data Agent Benchmarking Tests

## About

- Measures how accurately the data agent responds for price & market cap vs benchmark values from coinecko, defillama, coincap, etc.

- Generates agent prompts from values defined in `config.py` and validates them against each of the benchmark adapters.

## Running

## 1. `cd submodules/benchmarks`
## 2. Modify `config.py` with new prompts, coins & error tolerances
## 3. Run `pip install -r requirements.txt`
## 4. Run `python benchmarks.py price` for price benchmarks
## 5. Run `python benchmarks.py mcap` for market cap benchmarks

## Considerations

- The source of truth asset id is the coingecko id. Any new adapters will need some way of translating the coingecko id if they use something else. For example, the coincap doesn't use the same id format as coingecko and will need a translation layer (TODO).

- Disabling coingecko adapter lets us reduce the `time.sleep()` in `benchmarks.py` and run much faster (rate limiting).
