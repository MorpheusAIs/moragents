![morpheus ecosystem](images/morpheus-ecosystem@3x_green.png)
# MORagents

## Morpheus Install for Local Web3 Agent Interaction

# TODO update images
![UI 1](images/moragents_chatpdf.png)

![UI 2](images/wallet_integration.png)

![UI 3](images/successful_swap.png)

![UI 4](images/agent_clarify.png)

---
# TODO, give example queries
### Features
- Upload a PDF with paperclip icon, then ask question about PDF:
  - "Can you give me a summary?"
  - "What's the main point of the document?"
- Swap ERC Compatible Tokens
  - "Swap 0.01 ETH for "
  # TODO, verify we can swap for MOR
- Fetch Price, Market Cap, and TVL of coins and tokens supported on CoinGecko
  - "What's the price of ETH?"
  - "What's the market cap of BTC?"
- Check MOR rewards
  - "How many MOR rewards do I have?"
- Write Sizzling Tweets 🌶️ No Content Moderation 😅
  - "Write a based tweet about Crypto and AI"
  
**Works with your favorite wallet extensions in your existing browser**

---

## Install
### macOS
>Assumes minimum 16GB RAM

#### Steps to Install
1. Download Installer
   1. For Mac on Apple Silicon M1/2/3 etc. (arm64) [MORagents010-apple.pkg]() 
      > SHA256   MORagents010-apple.pkg
   2. For Mac on Intel (x86_64) [MORagents010-intel.pkg]()
      > SHA256   MORagents010-intel.pkg
2. Wait several minutes for background files to download and then your browser should automatically open to http://localhost:3333
    > Note: After installation is complete, the MORagents app icon will bounce for several minutes on your dock, and then stop. This is normal behavior as it's downloading a large 9GB file in the background. You can open "Activity Monitor" and in the Network tab see that it's downloading.

#### Future Usage
- Open the "MORagents" app from Mac search bar.
  - For easier access: Right-click MORagents icon on dock -> Options -> Keep in Dock 

#### Troubleshooting
If the app shows connections errors in connecting to agents. Please ensure Docker Desktop is running, then close and reopen **MORagents** from desktop.

---

### Windows (x86_64)
>Assumes minimum 16GB RAM

#### Steps
1. Use Chrome to download [MORagentsSetupWindows010.zip]()
    > SHA256  MORagentsSetupWindows010.zip
2. Go to downloaded **MORagentsSetupWindows010(.zip)** file and double click to open
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

### Build it Yourself

#### Build instructions:
1. [macOS](build_assets/macOS/README_MACOS_DEV_BUILD.md)
2. [Windows](build_assets/windows/README_WINDOWS_DEV_BUILD.md)
