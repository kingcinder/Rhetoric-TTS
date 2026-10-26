; Unsigned EXPERIMENTAL installer recipe. Windows support is not qualified.
#define AppName "Rhetoric (EXPERIMENTAL)"
#define AppPublisher "Rhetoric"
#ifndef ProductVersion
  #define ProductVersion "1.5.0"
#endif
#ifndef SourceDir
  #define SourceDir "dist\\Rhetoric"
#endif

[Setup]
AppId={{C8E0EF20-4C09-4CF8-9F6F-150000000001}
AppName={#AppName}
AppVersion={#ProductVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\Rhetoric
DefaultGroupName=Rhetoric (EXPERIMENTAL)
OutputBaseFilename=rhetoric-{#ProductVersion}-windows-experimental-unsigned
OutputDir=release_artifacts\windows-experimental
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
Compression=lzma
SolidCompression=yes
UninstallDisplayName=Rhetoric (EXPERIMENTAL)
Uninstallable=yes

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Rhetoric (EXPERIMENTAL)"; Filename: "{app}\Rhetoric.exe"
Name: "{commondesktop}\Rhetoric (EXPERIMENTAL)"; Filename: "{app}\Rhetoric.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function InitializeSetup(): Boolean;
begin
  MsgBox('This unsigned installer is EXPERIMENTAL and Windows is not a supported release target.', mbInformation, MB_OK);
  Result := True;
end;
