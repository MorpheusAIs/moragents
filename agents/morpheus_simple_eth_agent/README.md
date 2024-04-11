1. Have ollama running on your host with the llama2 model preloaded.
2. Build the Docker container using the included Dockerfile.

3. Run with:
```sh
    $ docker run -d -p 5555:5555 morpheus/simple_eth_agent
```

4. Make a REST call to container:
```sh
    $ curl -X POST -H "Content-Type: application/json" -d '{"NLQ": "what is my balance?"}' http://localhost:5555/process_nlq
```

# TODO, wallet connection to a MetaMask wallet