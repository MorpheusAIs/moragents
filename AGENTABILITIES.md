# MORagents

Welcome to the world of Web3 agents! If you're interested in building and using agents locally, this document will guide you through the principles and 
current projects underway.

### Principles:
1. **Agents cannot execute decisions**: Agents should not be given private keys or allowed to make transactions on their own. They can only construct transaction 
payloads for a user's approval. This is due to the limitations of current LLMs in understanding complex transactions and the risk of [gaslighting](https://arxiv.org/abs/2311.04235).
2. **Local installation**: Agents should run on the user's laptop, typically with 8-16 GB of RAM. This allows for faster execution and better performance.
3. **No private keys**: Agents must not have access to private keys or be able to execute transactions independently. User's cryptographic approval is essential for any 
transaction.

### Current Projects (all local):
1. **CliffordAttractor on Discord** - Following Assume 16GB+ RAM:
   1. Developed a [price fetcher agent](https://github.com/cliffordattractor/morpheus-data-agent) using CoinGecko, which is being integrated by LachsBagel.
   2. (Pending) A [web interface](https://github.com/cliffordattractor/morpheus-ui) that will be served by the local Docker installation and integrated with Rainbow, enabling the use of MetaMask, WalletConnect, and other 
   EVM-based wallets.
   3. (Pending) A [swap agent](https://github.com/cliffordattractor/morpheus-swap-agent) which can iteratively ask users to provide needed details for disambiguation.
   4. (Pending) A general-purpose agent that can ingest arbitrary documents, such as PDFs, for basic document QA and text generation.
2. **PolyWrap and FLock** - Assumes 8GB+ of RAM:
   1. FLock is distilling a model from Polywrap's [AutoTx](https://github.com/polywrap/AutoTx), which will allow users with 8 GB of RAM to use Flock's fine-tuned version of 
   AutoTX. 
      2. FLock has provided the codebase [here](https://github.com/nickcom007/AutoTx). This is pending integration by CliffordAttractor
3. **lachsbagel on Discord** - [this repo](https://github.com/LachsBagel/moragents): 
   1. Local Docker install
   2. Transient tkinter-based UI, which will be replaced by a more compelling UI developed by CliffordAttractor
   3. (pending) Delegator agent to allow automatic delegation of downstream tasks of agents without requiring manual specification by users.
4. **artfuljars on Discord**:
   5. Windows Build (EXE version of .app)
   6. Two installation wizards. One each for macOS and Windows (install system dependencies + MORagents app)

### Decentralized Inference:
#### Non-Local Installation Agents for Permission-less Compute
Pending Lumerin's work. Eventually Agent Builders will be able to permission-lessly upload Agent and Model artifacts to a decentralized registry.
These agents will need to be integrated in self-standing applications, and thus are not suitable for the local installation.
The local installation mentioned above may grow into allowing compute providers to download, host, and serve these arbitrary models, however it is unlikely to be the interface from which they are consumed.

### How to Contribute:
- If you are working on an agent which can provide value through open models and relies on processing public data, please reach out to lachsbagel on Discord (link below)   
  - Otherwise, you are more than welcome to publish your agent to the registry when it goes live pending Lumerin's work and any other necessary pieces which come up to better ensure security and verifiability of models in non-local execution environments.
- If you are working on security and/or verifiability of models and the runtime, please reach out to LachsBagel on the Morpheus Discord.
  - Currently looking at [Hyperbolic.xyz](https://hyperbolic.xyz) and [6079](https://6079-ai.gitbook.io/6079.ai/technology/6079-proof-of-inference-protocol). See more ecosystem members [here](https://mor.org/ecosystem).

### Contact
Join the [Morpheus Discord](https://discord.com/invite/Dc26EFb6JK)

*Last Updated: May 7, 2024*