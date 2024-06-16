[Setup]
AppName=MORagents
AppVersion=0.0.8
DefaultDirName={commonpf}\MORagents
OutputDir=.\MORagentsWindowsInstaller
OutputBaseFilename=MORagentsSetup
DiskSpanning=yes
SlicesPerDisk=1
DiskSliceSize=max
Compression = none
[Messages]
WelcomeLabel1=Welcome to the MORagents Setup Wizard
WelcomeLabel2=This will install MORagents on your computer. Please click Next to continue.
[Files]
Source: "dist\MORagents\MORagents.exe"; DestDir: "{app}"
Source: "dist\MORagents\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs
Source: "images\moragents.ico"; DestDir: "{app}"
Source: "resources\Docker Desktop Installer.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{commondesktop}\MORagents"; Filename: "{app}\MORagents.exe"; IconFilename: "{app}\moragents.ico"
[Run]
Filename: "{tmp}\Docker Desktop Installer.exe"; Description: "Installing Docker Desktop..."; StatusMsg: "Installing Docker Desktop..."