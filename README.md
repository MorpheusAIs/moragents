![morpheus ecosystem](images/morpheus-ecosystem@3x_green.png)
# MORagents

## Local Agents Built with the Friendliest of Dev Tooling
Python for AI Agents, JS for UI. Runs in your favorite browser. Made possible by Docker.
Fully Extensible! Add your own agents and have them automatically invoked based on user intent.

**Note:** This repository is meant to act as a sandbox for Smart Agent developers to explore existing agents and to build their own. It is not designed to be a production-ready application or consumer-based product. Please set your expectations accordingly. For additional information about a specific agent, browse to the submodules/moragents_dockers/agents/src/agents/ directory in the repo and view the README file for the agent you are interested in.

![UI 1](images/MORagents-UI.png)

![UI 2](images/gasless-usdc-base-agent.png)

![UI 3](images/dca-strategy-agent.png)

![UI 4](images/image-generator.png)

![UI 5](images/tweet_sizzler.png)

![UI 6](images/real-time-info.png)

![UI 7](images/mor_rewards.png)

![UI 8](images/price-fetcher-realtime-news.png)

![UI 9](images/moragents_chatpdf.png)

---

### Features

#### Generate Images 🏞️
   - "Generate an image of a cryptographically secure doggo"
#### Send Gasless USDC with Coinbase 🚚
   - "Send USDC on Base"
   _- WARNING: Highly experimental. Please backup your wallet file by downloading from wallet selector._
   - [INSTRUCTIONS](submodules/moragents_dockers/agents/src/agents/base_agent/README.md)
#### Dollar Cost Averaging (DCA) with Coinbase
   - "DCA Strategy on Base"
   _- WARNING: Highly experimental. Please backup your wallet file by downloading from wallet selector._
   - [INSTRUCTIONS](submodules/moragents_dockers/agents/src/agents/dca_agent/README.md)
#### Write Sizzling Tweets 🌶No Content Moderation 😅
  - "Write a based tweet about Crypto and AI"
  - [INSTRUCTIONS](submodules/moragents_dockers/agents/src/agents/tweet_sizzler/README.md)
#### Real-time Info 🕸️
  - "Real-time info about Company XYZ"
#### Trending Crypto News
  - "Latest news for USDC"
#### Check MOR rewards 🏆
  - "How many MOR rewards do I have?"
#### Fetch Price, Market Cap, and TVL of coins and tokens supported on CoinGecko 📈
  - "What's the price of ETH?"
  - "What's the market cap of BTC?"
#### Upload a PDF with paperclip icon, then ask questions about the PDF 📄
  - "Can you give me a summary?"
  - "What's the main point of the document?"
#### Ask about popular tokens and summary reports for tokens 🍿
  - "What are the most active tokens on Solana?"

---

## Easy Install
### macOS
>Best performance when >=16GB RAM

#### Steps to Install
1. Download Installer
   1. For Mac on Apple Silicon M1, M2, M3, M4 (arm64)
      1. Download and run MORagents installer [MORagents022-apple.pkg](https://drive.proton.me/urls/YA24T6MMT0#iCrO2BCuVZff)
      > SHA256 3f51ce7cb5a81903f1cc612901c5c63cacc106e83e14c5ca791ddd6b5e71e883 MORagents022-apple.pkg
2. Wait several minutes for background files to download and then your browser should automatically open to http://localhost:3333
    > Note: After installation is complete, the MORagents app icon will bounce for several minutes on your dock, and then stop. This is normal behavior as it's downloading <7GB of files in the background. You can open "Activity Monitor" and in the Network tab see that it's downloading.

#### Future Usage
- Open the "MORagents" app from Mac search bar.
  - For easier access: Right-click MORagents icon on dock -> Options -> Keep in Dock

#### Troubleshooting
- If the app shows connections errors in connecting to agents. Please ensure Docker Desktop is running, then close and reopen **MORagents** from desktop.
- If installation is unsuccessful, run the following in your Terminal and open the MORagents....pkg again
   ```shell
      $ xcode-select --install
   ```
- If you don't already have Docker installed, the installation may fail the first time. Simply run Docker, grant permissions as needed, and ensure you are logged in with a Docker account. Then run the installation a second time and it should work.
---

### Windows (x86_64)
>Best performance when >=16GB RAM

#### Steps
1. Download [MORagentsSetupWindows022.zip](https://drive.proton.me/urls/MGNQ086Y2G#1cVhZOkkY1TU)
    > SHA256 823790f9c2e2a1db7071012ad720e21a446d2fa86a58ac100cff134a107e7a3d MORagentsSetupWindows022.zip
2. Go to downloaded **MORagentsSetupWindows022(.zip)** file and double click to open
3. Double click **MORagentsSetup.exe**
   1. You may need to click "More info" -> "Run anyway"
   2. If that still doesn't work, try temporarily disabling your antivirus and open the .exe again
4. Click and Run **MORagentsSetup.exe**
   1. This will auto-install Docker and Ollama dependencies. Those will ask you for confirmation.
5. Open **MORagents** from Desktop
   1. Wait for Docker engine to start...
   2. If you see any errors or if anything hangs for >10min, please try opening the MORagents app again from the Desktop

#### Troubleshooting
If the app shows connections errors in connecting to agents. Please ensure Docker Desktop is running, then close and reopen **MORagents** from desktop.

---

#### Linux
*Coming soon*

---
# Adding a New Agent

See [Agents README](submodules/moragents_dockers/README.md) section: "Steps to Add a New Agent".

This will allow you to add custom agents which will be automatically invoked based on relevant user queries.

---

### Build it Yourself

#### Build instructions:
1. [macOS](build_assets/macOS/README_MACOS_DEV_BUILD.md)
2. [Windows](build_assets/windows/README_WINDOWS_DEV_BUILD.md)
