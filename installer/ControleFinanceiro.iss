; Script do Inno Setup para o instalador do Controle Financeiro.
;
; Como gerar o instalador:
;   1. Instale o Inno Setup (https://jrsoftware.org/isinfo.php).
;   2. Gere o executavel primeiro (a partir da raiz do projeto):
;        pyinstaller ControleFinanceiro.spec
;      Isso cria dist\ControleFinanceiro.exe.
;   3. Compile este script (clique direito > Compile, ou via linha de
;      comando: iscc installer\ControleFinanceiro.iss).
;   4. O instalador final fica em installer\output\ControleFinanceiro_Setup.exe.
;
; O instalador nao pede privilegios de administrador: instala na pasta
; do usuario atual (%LocalAppData%\Programs), porque o proprio app
; cria e grava seus dados (data\, reports\, backups\) dentro da pasta
; de instalacao. Cada usuario do Windows tera sua propria instalacao e
; seus proprios perfis - nao ha nada compartilhado entre contas do
; sistema operacional.
;
; O banco de dados e criado automaticamente na primeira execucao (nao
; e responsabilidade do instalador) - por isso o fluxo abaixo abre o
; aplicativo ao final da instalacao.

#define MyAppName "Controle Financeiro"
#define MyAppVersion "1.0"
#define MyAppExeName "ControleFinanceiro.exe"
#define MyAppPublisher "Controle Financeiro"

[Setup]
AppId={{B6E1E9C0-6E9B-4B7D-9C1B-CONTROLEFINANCEIRO}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=ControleFinanceiro_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos adicionais:"

[Files]
Source: "..\dist\ControleFinanceiro.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Pergunta implicitamente via confirmacao padrao do Inno Setup; os dados do
; usuario (data\) NAO sao removidos automaticamente no desinstalador para
; evitar perda acidental de dados financeiros. Remova manualmente a pasta
; de instalacao se quiser apagar tudo, incluindo os bancos de dados.
