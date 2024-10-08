#!/bin/bash

curl -L https://github.com/ollama/ollama/releases/download/v0.3.6/ollama-darwin -o ollama

chmod +x ollama

sudo mv ollama /usr/local/bin/

nohup /usr/local/bin/ollama serve > /dev/null 2>&1 &
/usr/local/bin/ollama pull llama3.2:3b
/usr/local/bin/ollama pull nomic-embed-text
