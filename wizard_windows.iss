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
WelcomeLabel1=Welcome to the MORagents Setup Wizard. By proceeding you acknowledge you had read and agreed to the License found at: https://github.com/MorpheusAIs/moragents/blob/778b0aba68ae873d7bb355f2ed4419389369e042/LICENSE
WelcomeLabel2=This will install MORagents on your computer. Please click Next to continue.

[Files]
Source: "dist\MORagents\MORagents.exe"; DestDir: "{app}"
Source: "dist\MORagents\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs
Source: "images\moragents.ico"; DestDir: "{app}"
Source: "resources\Docker Desktop Installer.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{commondesktop}\MORagents"; Filename: "{app}\MORagents.exe"; IconFilename: "{app}\moragents.ico"
[Run]
Filename: "{app}\LICENSE"; Description: "License Agreement"; Flags: postinstall shellexec skipifsilent