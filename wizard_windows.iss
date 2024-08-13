[Setup]
AppName=MORagents
AppVersion=0.0.9
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
Source: "LICENSE.md"; DestDir: "{app}"; Flags: isreadme
Source: "{tmp}\DockerDesktopInstaller.exe"; DestDir: "{tmp}"; Flags: external deleteafterinstall
Source: "{tmp}\OllamaSetup.exe"; DestDir: "{tmp}"; Flags: external deleteafterinstall
Source: "runtime_setup_windows.py"; DestDir: "{app}"

[Icons]
Name: "{commondesktop}\MORagents"; Filename: "{app}\MORagents.exe"; IconFilename: "{app}\moragents.ico"

[Run]
Filename: "{tmp}\DockerDesktopInstaller.exe"; Parameters: "install"; StatusMsg: "Installing Docker Desktop..."; Flags: waituntilterminated
Filename: "{tmp}\OllamaSetup.exe"; StatusMsg: "Installing Ollama..."; Flags: waituntilterminated
Filename: "{app}\LICENSE.md"; Description: "View License Agreement"; Flags: postinstall shellexec skipifsilent
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
    'By continuing, you acknowledge that you have read and agreed to the License. '
    + 'The full license text can be found below:'
    + #13#10
    + 'MIT License'
    + #13#10
    + 'Copyright (c) 2024 Liquid Tensor LLC'
    + #13#10
    + 'Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”),
 to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: '

    + ''
    + 'The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.'
    + ''

    + 'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
    PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'
    + #13#10
    + 'Do you accept the terms of the License agreement?');

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
