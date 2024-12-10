# Benchmarking & Testing Reward Checking Agent Guide

NOTE: this is made for the router compatible moragents repo

## How to Run the Tests:
1) In the parent directory:
- ```cd submodules/moragents_dockers/agents```

2) ```docker build -t agent .```

2. NOTE:  If you are using Apple Silicon then you may experience problems due to the base image not being build for arm64. We have included a separate Dockerfile in order to deal with this issue, run:

- ```docker build . -t agent -f Dockerfile-apple```

3) To run the agent:

- ```docker run --name agent -p 5000:5000 agent```

4) Check if the agent is up and running on docker or not
5) If it is running, navigate to `submodules/reward_check_agent_benchmarks`
6) run `benchmarks.py`

NOTE: If needed use your own alchemy mainnet RPC instead of the default cloudflare one in `config.py` and please `pip install pytest web3`
