## Distribution

For Mac:
```sh
$ pyinstaller --windowed --runtime-hook runtime_hook.py --add-data "resources:resources" --name="MORagents" --icon="moragents.icns" main.py
```

For Windows:
```shell
> pyinstaller --runtime-hook runtime_hook_windows.py --name="MORagentsWindows" --add-data "resources;resources" --icon="./moragents.ico" main.py
```

Windows Inno Setup for Wizard:
```text
[Setup]
AppName=MOR Agent
AppVersion=1.0
DefaultDirName={pf}\MOR Agent
OutputDir=.\Output
OutputBaseFilename=MORAgentSetup
DiskSpanning=yes
SlicesPerDisk=1
DiskSliceSize=max

[Messages]
WelcomeLabel1=Welcome to the MOR Agent Setup Wizard
WelcomeLabel2=This will install MOR Agent on your computer. Please click Next to continue.

[Files]
Source: "moragents\dist\MORagentsWindows\MoragentsWindows.exe"; DestDir: "{app}"
Source: "moragents\dist\MORagentsWindows\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs
Source: "moragents\moragents.ico"; DestDir: "{app}"
Source: "Docker Desktop Installer.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{commondesktop}\MOR Agent"; Filename: "{app}\MORagentsWindows.exe"; IconFilename: "{app}\moragents.ico"

[Run]
Filename: "{tmp}\Docker Desktop Installer.exe"; Description: "Installing Docker Desktop..."; StatusMsg: "Installing Docker Desktop..."
```




# Code signing
```sh
codesign --deep --force --verbose --sign "Developer ID Application: YourDeveloperName" MORagents.app
```

## Verify
```sh
codesign --verify --verbose=4 MORagents.app

codesign -dv --verbose=4 MORagents.app
```

---

# TODO
auto-install docker when "No such file or directory: '/usr/local/bin/docker'"
auto-remove containers
