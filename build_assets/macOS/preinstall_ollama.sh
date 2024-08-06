#!/bin/bash

curl -L https://github.com/jmorganca/ollama/releases/download/v0.1.46/ollama-darwin -o ollama

chmod +x ollama

sudo mv ollama /usr/local/bin/
