# Morpheus Swap Agent

This agent will enable you to perform swaps between cryptoassets. It should be used with the accompanying UI which provides a browser-based front-end to chat with the agent, display quotes and sign transactions.

A typical flow looks like this:

- User requests a swap, e.g "I want to swap ETH for USDC"
- The agent requests any missing information, e.g. in this case the amount is missing
- Once all the information hase been collected, the agent looks up the assets on the current chain, retrieves contract addresses and generates a quote if available.
- The quote is shown to the user, who may either proceed or cancel
- If the user accepts the quote, the swap may proceed.  The back-end will generate transactions which will be sent to the front-end to be signed by the user's wallet.
- If the allowance for the token being sold is too low, an approval transaction will be generated first


Chains supported:
- Ethereum
- Arbitrum
- Optimism
- Polygon
- BSC




## Installation
Each agent is self contained, so cd first into the agent directory

### With Docker
This is the recommended way to run the project in order to avoid dependency hell.  You will need to build then run:


```docker build -t agent .```

If you are using Apple Silicon then you may experience problems due to the base image not being build for arm64. We have included a separate Dockerfile in order to deal with this issue, run:

```docker build . -t agent -f Dockerfile-apple```

To run:

```docker run --name agent -p 5000:5000 agent```

### Without Docker


```pip install -r requirements.txt```
```pip install --no-cache-dir -U llama-cpp-python```


## API Endpoints

Your agent should expose the following endpoints:

### 1. Chat
This is the main endpoint for chatting with the agent.

```http://127.0.0.1:5000/```

The chat API accepts inputs in OpenAI chat completion format - see the example below:


```sh
url = 'http://127.0.0.1:5000/
message={"role":"user","content":"swap 1 eth"}
data = {'prompt':message,'chain_id':56}
response = requests.post(url, json=data)
```

The response will also be in this format.

```sh
response = {"role":"assistant","content":"To proceed with the swap, I need to know which crypto currency you want to
buy in exchange for 1 ETH. Could you please specify the target crypto currency?"}
```

If the agent has enough information (buy token, sell token, amount) it will then look up the token addresses on the current chain.

If the token symbols are valid, it will then check the user has sufficient balance of the sell token.

If there is sufficient balance, the agent will provide a response containing a quote.  This quote is structured with json so that the UI may present the information in a suitable way.


```sh
response = {"role": "swap",
  "content": { "dst": "USDT", "dst_address": "0x55d398326f99059ff775485246999027b3197955", "dst_amount": "3000",
  "src": "ETH", "src_address": "0x2170ed0880ac9a755fd29b2688956bd959f933f8", "src_amount": "1",
  "approve_tx_cb": "/approve",
  "swap_tx_cb": "/swap"
  }
}
  ```

If the user wants to perform a swap based on the quote, the following steps are required:

    1) Check allowance
    2) If allowance < swap amount, send an approve transaction
    3) If allowance >= swap amount, send a swap transaction


### 2. Check Allowance

 ```http://127.0.0.1:5000/allowance```

  ```sh
url='http://127.0.0.1:5000/allowance
      data = {
                "tokenAddress":"token address here",
                "walletAddress":"wallet address here",
                "chain_id":56
              }
      response = requests.post(url, json=data)
      swap_transaction=response.text

  ```
  And then this api will return allowance value either 0 or 1


### 3. Generate Approve TX

```http://127.0.0.1:5000/approve```

```sh
url='http://127.0.0.1:5000/approve
      data = {
                "tokenAddress":"token address here",
                "amount": 10 , #amount to be swapped here
                "chain_id":56
              }
      response = requests.post(url, json=data)
      swap_transaction=response.text

```

### 4. Generate Swap tx

```http://127.0.0.1:5000/swap```

```sh
url='http://127.0.0.1:5000/swap
      data = {
                  "src": token1_address,
                  "dst": token2_address,
                  "amount": amount,
                  "from": walletAddress,
                  "slippage": slippage
              }
      response = requests.post(url, json=data)
      swap_transaction=response.text

```



### 5. Transaction status


```http://127.0.0.1:5000/tx_status```

This endpoint is used to inform the back-end of the status of transactions that have been signed by the user's wallet on the front-end.

Status values:

* "initiated" = tx has been sent to the wallet
* "cancelled" = tx cancelled by user
* "success" = tx successful
* "failed" = tx failed for some other reason, including being rejected by the wallet

Tx_type values:

* "swap"
* "approve"

```
url = 'http://127.0.0.1:5000/tx_status'
data={'status':'success', 'tx_type':'approve'}
response = requests.post(url, json=data)

print(response.text)
```


### 6. Messages

#### Get message history

```http://127.0.0.1:5000/messages```

Conversation history is stored in the backend.

```
url = 'http://127.0.0.1:5000/messages'
response = requests.get(url)

result=response.text
```


```
{"messages":[
  {"content":"swap 1 eth","role":"user"},
  {"content":"To proceed with the swap, I need to know which crypto currency you want to buy in exchange for 1 ETH. Could you please specify the target crypto currency?","role":"assistant"}
])
```

#### Clear message history


```
url = http://127.0.0.1:5000/clear_messages
response = requests.get(url, json=data)
```
