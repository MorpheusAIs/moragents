## Distribution

Run pyinstaller to build tar image. This will be packaged up in the inno setup.
```shell
> pyinstaller --runtime-hook runtime_hook_windows.py --name="MORagentsWindows" --add-data "resources;resources" --icon="./moragents.ico" main.py
```

Windows Inno Setup for Wizard:

1) Install Inno Setup
2) In the GUI, enter this setup and compile
   
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
