## Distribution

For Windows:
```shell
> pyinstaller --windowed --name="MORagents" --add-data "resources;resources" --icon=".\images\moragents.ico" main.py
> pyinstaller --name="MORagents" --add-data "resources;resources" --icon=".\images\moragents.ico" main.py
```

Windows Inno Setup for Wizard:

1) Install Inno Setup
2) In the GUI, enter this setup and compile
   
```text
[Setup]
AppName=MORagents
AppVersion=0.0.8
DefaultDirName={pf}\MORagents
OutputDir=.\Output
OutputBaseFilename=MORagentsSetup
DiskSpanning=yes
SlicesPerDisk=1
DiskSliceSize=max
[Messages]
WelcomeLabel1=Welcome to the MORagents Setup Wizard
WelcomeLabel2=This will install MORagents on your computer. Please click Next to continue.
[Files]
Source: "moragents\dist\MORagents\Moragents.exe"; DestDir: "{app}"
Source: "moragents\dist\MORagents\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs
Source: "moragents\images\moragents.ico"; DestDir: "{app}"
Source: "Docker Desktop Installer.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
[Icons]
Name: "{commondesktop}\MORagents"; Filename: "{app}\MORagents.exe"; IconFilename: "{app}\images\moragents.ico"
[Run]
Filename: "{tmp}\Docker Desktop Installer.exe"; Description: "Installing Docker Desktop..."; StatusMsg: "Installing Docker Desktop..."
```
