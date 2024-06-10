# MORagents

Welcome to the world of Web3 agents! If you're interested in building and using agents locally, this document will guide you through the principles and 
current projects underway.

### Principles:
1. **Agents cannot execute decisions**: Agents should not be given private keys or allowed to make transactions on their own. They can only construct transaction 
payloads for a user's approval. This is due to the limitations of current LLMs in understanding complex transactions and the risk of [gaslighting](https://arxiv.org/abs/2311.04235).
2. **Local installation**: Agents should run on the user's laptop, typically with 8-16 GB of RAM. This allows for faster execution and better performance.
3. **No private keys**: Agents must not have access to private keys or be able to execute transactions independently. User's cryptographic approval is essential for any 
transaction.

### Current Projects:
1. **CliffordAttractor on Discord** - Following Assume 16GB+ RAM:
   1. Developed a [price fetcher agent](submodules/moragents_dockers/agents/src/data_agent) using CoinGecko.
   2. A [web interface](submodules/moragents_dockers/frontend) which is served by the local Docker installation and integrated with Rainbow, enabling the use of MetaMask, WalletConnect, and other 
   EVM-based wallets.
   3. A [swap agent](submodules/moragents_dockers/agents/src/swap_agent) which can iteratively ask users to provide needed details for disambiguation.
   4. (Pending) A general-purpose agent that can ingest arbitrary documents, such as PDFs, for basic document QA and text generation.
2. **PolyWrap**:
   1. Polywrap is rebuilding some of the [AutoTx](https://github.com/polywrap/AutoTx) functionality into this local install using only the local OSS model.
      2. First integration will be for ETH sends.
3. **lachsbagel on Discord** - [this repo](https://github.com/MorpheusAIs/moragents): 
   1. Local Docker install
   2. (pending) Delegator agent to allow automatic delegation of downstream tasks of agents without requiring manual specification by users.
4. **artfuljars on Discord**:
   1. Windows Build (EXE version of .app)
   2. Two installation wizards:
      1. (pending) Windows
      2. (pending) macOS
5. **proprietary and teknium on Discord**
   1. Morph-Caller: an 8B Function Calling Model
      1. [Main HuggingFace Page](https://huggingface.co/Morpheus-Function-Calling/Morph-Caller)
      2. [Quantized Models huggingFace Page](https://huggingface.co/Morpheus-Function-Calling/Morph-Caller-GGUF)
   2. (pending) integration and usage by above agents

### Decentralized Inference:
#### Non-Local Installation Agents for Permission-less Compute
Pending Lumerin's work. Eventually Agent Builders will be able to permission-lessly upload Agent and Model artifacts to a decentralized registry.
These agents will need to be integrated in self-standing applications, and thus are not suitable for the local installation.
The local installation mentioned above may grow into allowing compute providers to download, host, and serve these arbitrary models, however it is unlikely to be the interface from which they are consumed.
1. (pending) [FLock](https://www.flock.io/#/) is working on a decentralized agent which will regularly be updated with most recent docs surrounding the Morpheus system for the following audiences:
   1. Normal user perspective (broad Q/A for those new to Morpheus ecosystem)
   2. Developer perspective wanting to deploy on Morpheus
   3. Perspective of capital contributors


### How to Contribute:
- If you are working on an agent which can provide value through open models and relies on processing public data, please reach out to lachsbagel on Discord (link below)   
  - Otherwise, you are more than welcome to publish your agent to the registry when it goes live pending Lumerin's work and any other necessary pieces which come up to better ensure security and verifiability of models in non-local execution environments.
- If you are working on security and/or verifiability of models and the runtime, please reach out to LachsBagel on the Morpheus Discord.
  - Currently looking at [Hyperbolic.xyz](https://hyperbolic.xyz) and [6079](https://6079-ai.gitbook.io/6079.ai/technology/6079-proof-of-inference-protocol). See more ecosystem members [here](https://mor.org/ecosystem).
  - LachsBagel is also working on a new research concept using a Transformer specific heuristic for model verification. 

### Contact
Join the [Morpheus Discord](https://discord.com/invite/Dc26EFb6JK)

*Last Updated: June 10, 2024*
