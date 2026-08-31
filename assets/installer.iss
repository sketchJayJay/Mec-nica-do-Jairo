; Inno Setup Script para Oficina Mecânica
; Requer Inno Setup 6+ (ISCC.exe no PATH ou execute pelo Inno Setup GUI)

#define MyAppName "Oficina Mecânica"
#define MyAppVersion "0.5.0"
#define MyAppPublisher "JL Eventos / Jater Jr"
#define MyAppExeName "OficinaMecanica.exe"

[Setup]
AppId={{A37CFA74-2D8C-4B4F-A7B7-INS-OFICINA-0001}}
AppName=Oficina Mecânica
AppVersion=0.5.0
AppPublisher=JL Eventos / Jater Jr
DefaultDirName={{pf}}\Oficina Mecânica
DefaultGroupName=Oficina Mecânica
DisableDirPage=no
DisableProgramGroupPage=no
OutputDir=dist
OutputBaseFilename=OficinaMecanica-Setup-0.5.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=assets\logo.ico

[Languages]
Name: "br"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
; Copia tudo que o PyInstaller gerou (modo one-folder)
Source: "dist\OficinaMecanica\*"; DestDir: "{{app}}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{{group}}\Oficina Mecânica"; Filename: "{{app}}\OficinaMecanica.exe"
Name: "{{commondesktop}}\Oficina Mecânica"; Filename: "{{app}}\OficinaMecanica.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Run]
Filename: "{{app}}\OficinaMecanica.exe"; Description: "Executar Oficina Mecânica agora"; Flags: nowait postinstall skipifsilent
