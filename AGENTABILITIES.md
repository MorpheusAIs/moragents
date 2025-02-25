# MORagents
Welcome to the world of Web3 agents! If you're interested in building and using agents, this document will guide you through the principles and
current projects underway.

### Principles:
1. **Agents Need Guardrails When Executing Decisions**: Agents should not be given all private key information or be allowed to enforce their own policy non-deterministically.
This is due to the limitations of current LLMs in understanding complex transactions and the risk of [gaslighting](https://arxiv.org/abs/2311.04235). 

### Current Projects:
1. **lachsbagel on Discord** - [this repo](https://github.com/MorpheusAIs/moragents):
   1. Architecture
   2. [HideNSeek](https://github.com/MorpheusAIs/HideNSeek): An algorithm for verifying and fingerprinting which model a compute provider is actually running
      1. Link to Paper [Hide and Seek: Fingerprinting Large Language Models with Evolutionary Learning](https://www.arxiv.org/abs/2408.02871)
   3. (pending) A follow-on paper exploring parameter size estimation is in the works.
2. **artfuljars on Discord**:
   1. Windows Build (EXE version of .app)
   2. Two installation wizards:
      1. Windows
      2. macOS
   3. CICD build for Windows
   4. CICD builds for Linux and macOS (apple and intel)
   5. Vulnerability scanning of dependencies and code
3. GenLayer
   1. (pending) [FeedBuzz](https://github.com/yeagerai/feedbuzz-contracts) - AI filtered logging system to surface user demand and failure modes for new functionality
4. **CliffordAttractor on Discord** - Following Assume 16GB+ RAM:
   1. Developed a [price fetcher agent](submodules/moragents_dockers/agents/src/data_agent) using CoinGecko.
   2. A [web interface](submodules/moragents_dockers/frontend) which is served by the local Docker installation and integrated with Rainbow, enabling the use of MetaMask, WalletConnect, and other
   EVM-based wallets.
   3. (NEEDS REFACTORING DUE TO 1INCH CHANGE) [Swap agent](submodules/moragents_dockers/agents/src/swap_agent) which can iteratively ask users to provide needed details for disambiguation.
   4. [General-purpose agent](https://github.com/MorpheusAIs/moragents/pull/34) that can ingest arbitrary documents, such as PDFs, for basic document QA and text generation.
   5. [Local delegating agent](https://github.com/MorpheusAIs/moragents/pull/45) which can maintain user's persona/interests as well as coordinating to task agents and tools.
5. **Dan Y.**
   1. [X/Twitter Posting Agent](https://github.com/MorpheusAIs/moragents/pull/57) - An agent which generates spicy tweets with an X integration for one-click posting.
   2. Real-time search agent
   3. Replaced llama 3.1 and functionary with llama 3.2 to massively increase speed 10X and reduce install footprint 6X
   5. Inter-agent Delegator which can coordinate between local and decentralized agents
   6. Coinbase DCA and Gasless USDC Agents
   7. Trending tokens and rugcheck agents
   8. Improved UI with multi-wallet connect
   9. (pending) Agent forge to allow devs to publish their custom agents to the Morpheus/Lumerin Agent Registry
6. **Niveshi**
   1. [MOR Rewards agent](https://github.com/MorpheusAIs/moragents/tree/main/submodules/moragents_dockers/agents/src/reward_agent/src). Lets you see how many MOR tokens are claimable for your wallet
   2. (being debugged) Cryto Live News Agent


### Decentralized Inference:
#### Non-Local Installation Agents for Permission-less Compute
Pending Lumerin's work. Eventually Agent Builders will be able to permission-lessly upload Agent and Model artifacts to a decentralized registry.

### How to Contribute:
- If you are working on an agent which can provide value through open models and relies on processing public data, please reach out to lachsbagel on Discord (link below)
  - Otherwise, you are more than welcome to publish your agent to the registry when it goes live pending Lumerin's work and any other necessary pieces which come up to better ensure security and verifiability of models in non-local execution environments.
- If you are working on security and/or verifiability of models and the runtime, please reach out to LachsBagel on the Morpheus Discord.
  - Currently looking at [Hyperbolic.xyz](https://hyperbolic.xyz) and [6079](https://docs.6079.ai/technology/6079-proof-of-inference-protocol). See more ecosystem members [here](https://mor.org/ecosystem).
  - LachsBagel is also working on a new algorithm, named [HideNSeek](https://github.com/MorpheusAIs/HideNSeek), which uses a Transformer specific heuristic for model verification
  - [6079](https://6079.ai/) will help with implementing the plumbing for [HideNSeek](https://github.com/MorpheusAIs/HideNSeek)

### Contact
Join the [Morpheus Discord](https://discord.com/invite/Dc26EFb6JK)

*Last Updated: January 16, 2025*
