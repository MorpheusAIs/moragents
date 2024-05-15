![morpheus ecosystem](images/morpheus-ecosystem@3x_green.png)
# MORagents

## Morpheus Install for Local Web3 Agent Interaction

![Fetcher UI](images/FetcherUI.png)
---

## For Early Developers

This README will guide you on building a Docker container for agent execution as well as a desktop UI app.
Soon there will be a pre-built single file install for the UI.

### Features
#### Current: 
- Fetch price, market cap, and TVL of coins and tokens supported on CoinGecko

#### Pending:
- Web interface
- Wallet integrations for your existing wallets in-browser
- Web3 swap agents
- Chat with local files agent (general purpose)

### Install
Before the single-click app is ready, you will need to build the app locally.

#### macOS
1. Ensure you have Python, Pip, tcl-tk, [Docker Desktop](https://www.docker.com/products/docker-desktop/), and Git installed. Note: please install python version 3.10.0+, older versions will produce outdated versions of tkinter when running the requirements install.


2. Clone Repo
```shell
 $ git clone https://github.com/LachsBagel/moragents.git
 $ cd  moragents
```

3. Build Docker Image for Local Agent Execution

```shell
For ARM (M1, M2, M3) 
    $ docker build -t morpheus/price_fetcher_agent -f agents/morpheus_price_agent/agent/Dockerfile-apple .

For Intel (x86_64)
    $ docker build -t morpheus/price_fetcher_agent -f Dockerfile agents/morpheus_price_agent/agent
```


4. Install Deps for UI, Recommended to use virtualenv
```shell
 $ python3 -m venv .venv
 $ . .venv/bin/activate
 $ pip install -r requirements.txt
```

5. Build App for Local Installation
```shell
 $  pyinstaller --windowed --runtime-hook runtime_hook.py --name="MORagents" --icon="moragents.icns" main.py
```
    # If you have issues, try
    python -m PyInstaller --windowed --runtime-hook runtime_hook.py --name="MORagents" --icon="moragents.icns" main.py

6. Install Application 
```shell
  $ cp dist/MORagents.app /Applications
```

7. Open the ```MORagents``` app on your Mac, Docker needs to be running before opening MORagents

#### Windows
*Coming soon*

#### Linux
*Coming soon*
