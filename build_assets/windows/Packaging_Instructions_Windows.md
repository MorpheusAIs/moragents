## Distribution

For Windows:
```shell
> pyinstaller --windowed --name="MORagents" --add-data "resources;resources" --icon=".\images\moragents.ico" main.py
> pyinstaller --name="MORagents" --add-data "resources;resources" --icon=".\images\moragents.ico" main.py
```

Windows Inno Setup for Wizard:

1) Install Inno Setup
2) In the GUI, enter the text found in [wizard_windows.iss](../../wizard_windows.iss) and compile
