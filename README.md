![morpheus ecosystem](images/morpheus-ecosystem@3x_green.png)
# MORagents

## Morpheus Install for Local Web3 Agent Interaction

![UI 1](images/moragents_chatpdf.png)

![UI 2](images/wallet_integration.png)

![UI 3](images/successful_swap.png)

![UI 4](images/agent_clarify.png)

---

### Features
- Chat with local PDF files
- Swap ERC Compatible Tokens
- Fetch Price, Market Cap, and TVL of coins and tokens supported on CoinGecko
- Web interface works in your preferred browser:
  - Chrome
  - Brave 
  
  with your favorite wallet extensions:
    - MetaMask
    - Rainbow
    - Coinbase Wallet
    - WalletConnect

---

## Install
### macOS on M1/2/3 etc. (arm64)
>Assumes minimum 16GB RAM

#### Steps to Install
1. Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   1. Follow default settings, can skip surveys, then leave docker desktop running. You can minimize it.
2. Download and install [MORagents009.pkg](https://drive.proton.me/urls/762Z6QFNH4#68MKubcGeDtf) 
    > SHA256 5200350bba351a40cfac5552476bad1bb67d32ff069a4d9ebc0b3556367673b7  MORagents009.pkg
3. Wait several minutes for background files to download and then your browser should automatically open to http://localhost:3333
    > Note: After installation is complete, the MORagents app icon will bounce for several minutes on your dock, and then stop. This is normal behavior as it's downloading a large 9GB file in the background. You can open "Activity Monitor" and in the Network tab see that it's downloading.

#### Future Usage
- Open the "MORagents" app from Mac search bar.
  - For easier access: Right-click MORagents icon on dock -> Options -> Keep in Dock 

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
If the app shows connections errors in connecting to agents. Please ensure Docker Desktop is running, then close and reopen **MORagents** from desktop.

---

#### Linux
*Coming soon*


---

### Build it Yourself

#### Build instructions:
1. [macOS](build_assets/macOS/README_MACOS_DEV_BUILD.md)
2. [Windows](build_assets/windows/README_WINDOWS_DEV_BUILD.md)
