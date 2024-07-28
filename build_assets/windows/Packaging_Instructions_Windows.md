## Distribution

For Windows:
1. Export docker images after building. See [Windows Build](./README_WINDOWS_DEV_BUILD.md)
```shell
  docker save -o moragents_dockers-nginx.tar moragents_dockers-nginx:latest
  docker save -o moragents_dockers-agents.tar moragents_dockers-agents:latest

```

2.
```shell
  pyinstaller --name="MORagents" --icon=".\images\moragents.ico" main.py
```

Windows Inno Setup for Wizard:
1) Install Inno Setup
2) In the GUI, enter the text found in [wizard_windows.iss](../../wizard_windows.iss)
3) Click Build > Compile
4) Hit the Play/Run button on the top
5) Installer is the 
