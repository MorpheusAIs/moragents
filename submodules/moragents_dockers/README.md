# Moragents 

This repo contains multiple agents and a dapp that enables you to interact with the agents, all running locally and containerized with Docker.



## Dependencies 

* Docker
* Ollama

Pull the required models in ollama

```ollama pull llama3```

```ollama pull nomic-embed-text```


## Installation

Docker compose will build and run two containers.  One will be for the agents, the other will be for the UI. 

```docker-compose up```

or for Apple silicon

```docker-compose -f docker-compose-apple.yml up```

Open in the browser: ```http://localhost:3333/```

Docker build will download the model.  The first time that one of the agents are called, the model will be loaded into memory and this instance will be shared between all agents.

## Agents

### Data Agent

This agent provides real-time pricing and other cryptoasset metrics by pulling data from CoinGecko and DefiLlama APIs.

It currently supports the following metrics:

- current price of coins
- current price of NFT collections
- market cap
- fully diluted valuation
- total value locked

It is possible to ask questions about assets by referring to them either by their name or their ticker symbol.

### Swap Agent
This agent will enable you to perform swaps between cryptoassets. It should be used with the accompanying UI which provides a browser-based front-end to chat with the agent, display quotes and sign transactions.

A typical flow looks like this:

- User requests a swap, e.g "I want to swap ETH for USDC"
- The agent requests any missing information, e.g. in this case the amount is missing
- Once all the information hase been collected, the agent looks up the assets on the current chain, retrieves contract addresses and generates a quote if available.
- The quote is shown to the user, who may either proceed or cancel
- If the user accepts the quote, the swap may proceed.  The back-end will generate transactions which will be sent to the front-end to be signed by the user's wallet.
- If the allowance for the token being sold is too low, an approval transaction will be generated first

### RAG Agent

This agent will answer questions about an uploaded PDF file. 
