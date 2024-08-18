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
1. **lachsbagel on Discord** - [this repo](https://github.com/MorpheusAIs/moragents): 
   1. Local Docker install
   2. (pending) [HideNSeek](https://github.com/MorpheusAIs/HideNSeek): An algorithm for verifying and fingerprinting which model a compute provider is actually running
      1. Note: this repo will be made public under an MIT license following the publishing of a paper by the same name which is currently in the works
2. **IODmitri, SanatSharma, LachsBagel on GitHhub**
   3. [HideNSeek](https://github.com/MorpheusAIs/HideNSeek): An algorithm for verifying and fingerprinting which model a compute provider is actually running
      4. Link to Paper [Hide and Seek: Fingerprinting Large Language Models with Evolutionary Learning](https://www.arxiv.org/abs/2408.02871)
3. **artfuljars on Discord**:
   1. Windows Build (EXE version of .app)
   2. Two installation wizards:
      1. Windows
      2. (pending) macOS
   3. (pending) CICD builds for Windows, Linux, and macOS
   4. (pending) Vulnerability scanning of dependencies and code
4. GenLayer
   1. (pending) [FeedBuzz](https://github.com/yeagerai/feedbuzz-contracts) - AI filtered logging system to surface user demand and failure modes for new functionality  
5. **CliffordAttractor on Discord** - Following Assume 16GB+ RAM:
   1. Developed a [price fetcher agent](submodules/moragents_dockers/agents/src/data_agent) using CoinGecko.
   2. A [web interface](submodules/moragents_dockers/frontend) which is served by the local Docker installation and integrated with Rainbow, enabling the use of MetaMask, WalletConnect, and other 
   EVM-based wallets.
   3. A [swap agent](submodules/moragents_dockers/agents/src/swap_agent) which can iteratively ask users to provide needed details for disambiguation.
   4. [A general-purpose agent](https://github.com/MorpheusAIs/moragents/pull/34) that can ingest arbitrary documents, such as PDFs, for basic document QA and text generation.
   5. (Pending Integration) [Delegating agent](https://github.com/MorpheusAIs/moragents/pull/45) which can maintain user's persona/interests as well as coordinating to task agents and tools.
6. **Dan Y.**
   1. (pending) X/Twitter Posting Agent - an agent which generates spicy tweets with an X integration for one-click posting.

### Decentralized Inference:
#### Non-Local Installation Agents for Permission-less Compute
Pending Lumerin's work. Eventually Agent Builders will be able to permission-lessly upload Agent and Model artifacts to a decentralized registry.
1. [FLock](https://www.flock.io/#/) has built a decentralized agent, called [Ragchat-Morpheus](https://github.com/FLock-io/ragchat-morpheus) which will regularly be updated with most recent docs surrounding the Morpheus system for the following audiences:
   1. Normal user perspective (broad Q/A for those new to Morpheus ecosystem)
   2. Developer perspective wanting to deploy on Morpheus
   3. Perspective of capital contributors


### How to Contribute:
- If you are working on an agent which can provide value through open models and relies on processing public data, please reach out to lachsbagel on Discord (link below)   
  - Otherwise, you are more than welcome to publish your agent to the registry when it goes live pending Lumerin's work and any other necessary pieces which come up to better ensure security and verifiability of models in non-local execution environments.
- If you are working on security and/or verifiability of models and the runtime, please reach out to LachsBagel on the Morpheus Discord.
  - Currently looking at [Hyperbolic.xyz](https://hyperbolic.xyz) and [6079](https://docs.6079.ai/technology/6079-proof-of-inference-protocol). See more ecosystem members [here](https://mor.org/ecosystem).
  - LachsBagel is also working on a new algorithm, named [HideNSeek](https://github.com/MorpheusAIs/HideNSeek), which uses a Transformer specific heuristic for model verification
  - [6079](https://6079.ai/) will help with implementing the plumbing for [HideNSeek](https://github.com/MorpheusAIs/HideNSeek)

### Contact
Join the [Morpheus Discord](https://discord.com/invite/Dc26EFb6JK)

*Last Updated: August 16, 2024*
