# Data Agent Benchmarking Tests

## About

- Measures how accurately the data agent responds for price & market cap vs benchmark values from coinecko, defillama, etc.

- Generates agent prompts from values defined in `config.py` and validates them against each of the benchmark adapters.

## Running

## 0. Start [ DataAgent Docker Service](../../moragents_dockers/agents/src/data_agent/README.md)
## 1. Modify `config.py` with new prompts, coins & error tolerances
## 2. `cd submodules/benchmarks`
## 3. Run `pip install -r requirements.txt`
## 4. Run `python benchmarks.py price` for price benchmarks
## 5. Run `python benchmarks.py mcap` for market cap benchmarks

## Considerations

- The source of truth asset id is the coingecko id. Any new adapters will need some way of translating the coingecko id if they use something else. For example, the defillama adapter "just works" because they use coingecko ids.

- Disabling coingecko adapter lets us reduce the `time.sleep()` in `benchmarks.py` and run much faster (rate limiting).
