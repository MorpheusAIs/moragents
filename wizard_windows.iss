[Setup]
AppName=MORagents
AppVersion=0.0.8
DefaultDirName={commonpf}\MORagents
OutputDir=.\MORagentsWindowsInstaller
OutputBaseFilename=MORagentsSetup
WizardStyle=modern

[Messages]
WelcomeLabel1=Welcome to the MORagents Setup Wizard
WelcomeLabel2=This will install MORagents on your computer. Please click Next to continue.

[Files]
Source: "dist\MORagents\MORagents.exe"; DestDir: "{app}"
Source: "dist\MORagents\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs
Source: "images\moragents.ico"; DestDir: "{app}"
Source: "LICENSE"; DestDir: "{app}"; Flags: isreadme
Source: "{tmp}\DockerDesktopInstaller.exe"; DestDir: "{tmp}"; Flags: external deleteafterinstall
Source: "{tmp}\OllamaSetup.exe"; DestDir: "{tmp}"; Flags: external deleteafterinstall
Source: "runtime_setup_windows.py"; DestDir: "{app}"

[Icons]
Name: "{commondesktop}\MORagents"; Filename: "{app}\MORagents.exe"; IconFilename: "{app}\moragents.ico"

[Run]
Filename: "{tmp}\DockerDesktopInstaller.exe"; Parameters: "install"; StatusMsg: "Installing Docker Desktop..."; Flags: waituntilterminated
Filename: "{tmp}\OllamaSetup.exe"; StatusMsg: "Installing Ollama..."; Flags: waituntilterminated
Filename: "{app}\LICENSE"; Description: "View License Agreement"; Flags: postinstall shellexec skipifsilent
Filename: "{app}\MORagents.exe"; Description: "Launch MORagents"; Flags: postinstall nowait skipifsilent unchecked
Filename: "cmd.exe"; Parameters: "/c ollama pull llama3 && ollama pull nomic-embed-text"; StatusMsg: "Pulling Ollama models..."; Flags: runhidden waituntilterminated


[Code]
var
  EULAAccepted: Boolean;
  DownloadPage: TDownloadWizardPage;
  EULAPage: TOutputMsgWizardPage;

procedure InitializeWizard;
begin
  EULAPage := CreateOutputMsgPage(wpWelcome, 
    'License Agreement', 'Please read the following License Agreement carefully',
    'By continuing, you acknowledge that you have read and agreed to the License. ' +
    'The full license text can be found at: ' +
    'https://github.com/MorpheusAIs/moragents/blob/778b0aba68ae873d7bb355f2ed4419389369e042/LICENSE' + #13#10 + #13#10 +
    'Do you accept the terms of the License agreement?');

  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), nil);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  if CurPageID = EULAPage.ID then
  begin
    EULAAccepted := True;
  end
  else if CurPageID = wpReady then
  begin
    if not EULAAccepted then
    begin
      MsgBox('You must accept the License Agreement to continue.', mbError, MB_OK);
      Result := False;
      Exit;
    end;

    DownloadPage.Clear;
    DownloadPage.Add('https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe', 'DockerDesktopInstaller.exe', '');
    DownloadPage.Add('https://ollama.com/download/OllamaSetup.exe', 'OllamaSetup.exe', '');
    DownloadPage.Show;
    try
      try
        DownloadPage.Download;
        Result := True;
      except
        if DownloadPage.AbortedByUser then
          Log('Aborted by user.')
        else
          SuppressibleMsgBox(AddPeriod(GetExceptionMessage), mbCriticalError, MB_OK, IDOK);
        Result := False;
      end;
    finally
      DownloadPage.Hide;
    end;
  end;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
  
  { Skip EULA page if already accepted }
  if (PageID = EULAPage.ID) and EULAAccepted then
    Result := True;
end;