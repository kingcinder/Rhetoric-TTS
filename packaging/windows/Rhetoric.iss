; Rhetoric Windows installer recipe (Inno Setup). Unsigned build.
; The EULA acceptance lives on the standard Inno license page below,
; the way regular Windows programs do it — no custom blocking popup.
#define AppName "Rhetoric"
#define AppPublisher "Rhetoric"
#ifndef ProductVersion
  #define ProductVersion "1.5.0"
#endif
#ifndef SourceDir
  #define SourceDir "dist\\Rhetoric"
#endif
#ifndef EulaSha256
  #define EulaSha256 ""
#endif

[Setup]
AppId={{C8E0EF20-4C09-4CF8-9F6F-150000000001}
AppName={#AppName}
AppVersion={#ProductVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\Rhetoric
DefaultGroupName=Rhetoric
LicenseFile=..\..\EULA.md
OutputBaseFilename=rhetoric-{#ProductVersion}-windows-unsigned
OutputDir=release_artifacts\windows
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
Compression=lzma
SolidCompression=yes
UninstallDisplayName=Rhetoric
Uninstallable=yes

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Rhetoric"; Filename: "{app}\Rhetoric.exe"
Name: "{commondesktop}\Rhetoric"; Filename: "{app}\Rhetoric.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
// When setup finishes, record the EULA acceptance given on the license
// page in the exact JSON shape the app checks
// (src/the_oracle/eula_acceptance.py): the app reads
// {app}\eula_acceptance.json and compares eula_sha256 with the digest of
// its bundled EULA text. build.ps1 passes that digest in as
// /DEulaSha256. Reaching ssPostInstall means the license was accepted
// (a silent install is a deployment acceptance, the usual convention),
// so the app must not re-gate on its first-run dialog.
procedure CurStepChanged(CurStep: TSetupStep);
var
  Json: String;
begin
  if CurStep = ssPostInstall then
  begin
    if '{#EulaSha256}' <> '' then
    begin
      Json := '{"eula_sha256": "{#EulaSha256}", "accepted_at": "' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', '-', ':') + '"}';
      SaveStringToFile(ExpandConstant('{app}\eula_acceptance.json'), Json, False);
    end;
  end;
end;
