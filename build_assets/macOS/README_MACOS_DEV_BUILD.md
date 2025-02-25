## For Developers

This README will guide you on building a Docker container for agent execution as well as a desktop UI app.
You may instead simply download the [pre-built app](../../README.md)

#### macOS
1. Ensure you have Python, Pip, [Docker Desktop](https://www.docker.com/products/docker-desktop/), and Git installed. Note: please install python version 3.10.0+, older versions will produce outdated versions of tkinter when running the requirements install.


2. Clone Repo
```shell
 $ git clone https://github.com/MorpheusAIs/moragents
 $ cd  moragents
```

3. Build Docker Image for Local Agent Execution

```shell
For ARM (M1, M2, M3)
    $ docker-compose -f submodules/moragents_dockers/docker-compose-apple.yml up

For Intel (x86_64)
    $ docker-compose -f submodules/moragents_dockers/docker-compose.yml up
```


4. Install Deps for UI, Recommended to use virtualenv
```shell
 $ python3 -m venv .venv
 $ . .venv/bin/activate
 $ pip install -r requirements.txt
```

5. Build App for Local Installation
```shell
 $  pyinstaller --windowed --name="MORagents" --icon="images/moragents.icns" --osx-entitlements-file "build_assets/macOS/MORagents.entitlements" main.py
```
    # If you have issues, try
    python -m PyInstaller --windowed --name="MORagents" --icon="images/moragents.icns" --osx-entitlements-file "build_assets/macOS/MORagents.entitlements" main.py

6. Install Application
```shell
  $ cp dist/MORagents.app /Applications
```

7. Open the ```MORagents``` app on your Mac, Docker needs to be running before opening MORagents

--
### Signing, Notarization, and Stapling for Distribution
Instructions are [here](Packaging_Instructions_macOS.md).

--


Windows build instructions can be found [here](../windows/README_WINDOWS_DEV_BUILD.md)
