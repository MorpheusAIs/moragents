![morpheus ecosystem](images/morpheus-ecosystem@3x_green.png)
# MORagents

## Local Agents Built with the Friendliest of Dev Tooling
Python for AI Agents, JS for UI. Runs in your favorite browser. Made possible by Docker.
Fully Extensible! Add your own agents and have them automatically invoked based on user intent.

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
#### Dollar Cost Averaging (DCA) with Coinbase
   - "DCA Strategy on Base"
   _- WARNING: Highly experimental. Please backup your wallet file by downloading from wallet selector._
#### Write Sizzling Tweets 🌶No Content Moderation 😅
  - "Write a based tweet about Crypto and AI"
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

---

## Easy Install
### macOS
>Best performance when >=16GB RAM

#### Steps to Install
1. Download Installer
   1. For Mac on Apple Silicon M1, M2, M3, M4 (arm64)
      1. Download and run MORagents installer [MORagents021-apple.pkg](https://drive.proton.me/urls/AG19JG17JC#EYS7RDpLVVWK)
      > SHA256 b4e7126410561f986ba116af567e7ac05b9eb59e7f1dcbaca3d7cd85b69a30c4 MORagents021-apple.pkg
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
---

### Windows (x86_64)
>Best performance when >=16GB RAM

#### Steps
1. Download [MORagentsSetupWindows021.zip](https://drive.proton.me/urls/GXAJKN82JG#U4ZDz5eqgQ7Y)
    > SHA256 fc4631c1f1fa260cb9a206d27aa20c70812fffe524cbec421ad267e205d8c5c5 MORagentsSetupWindows021.zip
2. Go to downloaded **MORagentsSetupWindows021(.zip)** file and double click to open
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
