![morpheus ecosystem](images/morpheus-ecosystem@3x_green.png)
# MORagents

## Morpheus Install for Local Web3 Agent Interaction

![Fetcher UI](images/FetcherUI.png)
---

### Features
#### Current: 
- Fetch price, market cap, and TVL of coins and tokens supported on CoinGecko

#### Pending:
- Web interface
- Wallet integrations for your existing wallets in-browser
- Web3 swap agents
- Chat with local files agent (general purpose)

---

### Install
#### macOS M1/2/3 etc. (arm64)
>Assumes minimum 16GB RAM

#### Steps
1. Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   1. Follow default settings, can skip surveys, then leave docker desktop running. You can minimize it.
2. Download [Moragents.zip](https://drive.proton.me/urls/E1KWFPKJ7R#kylZ5O34WMGZ), open ZIP, and copy MORagents.app to your Applications folder 
    > SHA256 506a7fd292b8a4f37d0c9e9fc6810769af3d4e92cd567c1542724f3228328058  MORagents.zip
3. Open **MORagents** app. Give it a few minutes the first time.

### macOS Intel (x86_64)
*coming soon*

---

### Windows (x86_64)
>Assumes minimum 16GB RAM

#### Steps
1. Download [MOR Agent Installer](https://drive.proton.me/urls/CN7HB67ZYM#OcQMLZO8oxC1)
    > SHA256 ae10e62852c2a26608c9d65a719c52e06f33a1c79ecc3ddaf82503910c41ef7c  MOR Agent Installer.zip
2. Go to downloaded **MOR Agent Installer(.zip)** file and click to "Extract All"
3. Open Extracted Folder **MOR Agent Installer**
4. Click and Run **MOR Agent Setup**
   1. This will auto-install Docker Desktop dependency
5. Open **MOR Agent** from Desktop
6. Accept Docker's EULA
   1. Surveys are optional, can skip
7. Wait for Docker engine to start...
8. Open **MOR Agent** App from Desktop
    1. First time install requires some extr time to load agent's image

#### Troubleshooting
If the app shows connections errors to agent fetcher. Please ensure Docker Desktop is running, then close and reopen **MOR Agent** from desktop.

---

#### Linux
*Coming soon*


---

### Build it Yourself

#### Build instructions:
1. [macOS](README_MACOS_DEV_BUILD.md)
2. [Windows](README_WINDOWS_DEV_BUILD.md)


