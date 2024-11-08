# Morpheus Data Agent
This agent provides real-time pricing and other cryptoasset metrics by pulling data from CoinGecko and DefiLlama APIs.

It currently supports the following metrics:

- current price of coins
- current price of NFT collections
- market cap
- fully diluted valuation
- total value locked

It is possible to ask questions about assets by referring to them either by their name or their ticker symbol.

## Installation

### With Docker
This is the recommended way to run the project in order to avoid dependency hell.  You will need to build then run:

```cd agent```

```docker build -t agent .```

If you are using Apple Silicon then you may experience problems due to the base image not being build for arm64. We have included a separate Dockerfile in order to deal with this issue, run:

```docker build . -t agent -f Dockerfile-apple```

To run:

```docker run --name agent -p 5000:5000 agent```

### Without Docker

```cd agent```

```pip install -r requirements.txt```
```pip install --no-cache-dir -U llama-cpp-python```


## Usage

### With Docker

Docker exposes an API on port 5000 to communicate with the agent.

   ```sh
        url = 'http://127.0.0.1:5000/'
        data = {'prompt': "what is the market cap of dogwifhat"}
        response = requests.post(url, json=data)
        print(response.text)

   ```

A notebook has been provided to run test queries against the API:

```Test Docker.ipynb```

### Without Docker

To use the API run
```python agent.py```

To use an interactive CLI prompt to test the agent run:

```python agent-cli.py```




### Example queries
* what is the price of etherum
* price of eth

* what is the market cap of dogwifhat
* mc of wif

* what is the fully diluted valuation of solana
* fdv sol

* what is the total value locked in sushi
* tvl of pendle

## Notes
This project uses the openhermes-2.5-mistral-7b GGUF model and performs well on a modern laptop using only CPU.

The CoinGecko search API is used to find the asset that is being referenced. In case multiple matching assets are found, the agent will select the one with the largest market cap

When consuming this API as part of a larger agent, care should be taken to ensure that responses do not pass thorugh an LLM that hallucinates the number before the response is sent to the user.
