![morpheus ecosystem](images/morpheus-ecosystem@3x_green.png)
# MORagents

## Morpheus Install for Local Web3 Agent Interaction


![UI 1](images/wallet_integration.png)

![UI 2](images/successful_swap.png)

![UI 3](images/agent_clarify.png)
---

### Features
#### Current: 
- Fetch price, market cap, and TVL of coins and tokens supported on CoinGecko
- Web interface
- Wallet integrations for your existing wallets in-browser
  - MetaMask
  - Rainbow
  - Coinbase Wallet
  - WalletConnect
- Web3 swap agents

#### Pending:
- Chat with local files agent (general purpose)

---

### Install
#### macOS on M1/2/3 etc. (arm64)
>Assumes minimum 16GB RAM

#### Steps
1. Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   1. Follow default settings, can skip surveys, then leave docker desktop running. You can minimize it.
2. USe Chrome to download [Moragents.zip](https://drive.proton.me/urls/X35VBE3GWW#mtrqT6rAzZbi), open ZIP, and copy MORagents.app to your Applications folder 
    > SHA256 96c2510e4f7a752c613b322be0a107958ee34814415e3e7b950b426298379a7a MORagents.zip
3. Open **MORagents** app. Give it a few minutes the first time, and then it should open your browser. 
   1. If there's an issue, try opening the MORagents app again

### macOS Intel (x86_64)
*coming soon*

---

### Windows (x86_64)
>Assumes minimum 16GB RAM

#### Steps
1. Use Chrome to download [MORagentsWindowsInstaller.zip](https://drive.proton.me/urls/9BE8X1ZMTG#Oh1SfTeklH4W)
    > SHA256 0a5f5e3a288d45854c83994fa4afa4c713019229d99d67f28442fc56a5de1b20 MORagentsWindowsInstaller.zip
2. Go to downloaded **MORagentsWindowsInstaller(.zip)** file and click to "Extract All"
3. Open Extracted Folder **MORagentsWindowsInstaller**
   1. You may need to disable your anti-virus software before proceeding
4. Click and Run **MORagentsSetup.exe**
   1. This will auto-install Docker Desktop dependency
5. Open **MORagents** from Desktop
6. Accept Docker's EULA
   1. Surveys are optional, can skip
7. Wait for Docker engine to start...
8. Open **MORagents** App from Desktop
    1. First time installation requires some extra time to load agent's image
    2. If anything hangs for >10min, please try opening the MORagents app again from the Desktop

#### Troubleshooting
If the app shows connections errors to agent fetcher. Please ensure Docker Desktop is running, then close and reopen **MORagents** from desktop.

---

#### Linux
*Coming soon*


---

### Build it Yourself

#### Build instructions:
1. [macOS](build_assets/macOS/README_MACOS_DEV_BUILD.md)
2. [Windows](build_assets/windows/README_WINDOWS_DEV_BUILD.md)
