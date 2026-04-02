# Bridge MSFS -> Arduino LCD (Opcional)

Este software e opcional e serve somente para facilitar customizacao e envio de frequencias para o LCD.

Importante:

- o painel continua funcionando no jogo sem este software
- botoes e chaves HID continuam nativos no Windows

## Funcionalidades da versao atual

- interface profissional (layout moderno em cards)
- seletor de tema (Sistema / Claro / Escuro)
- conectar/desconectar na porta COM do Arduino
- trocar de porta COM rapidamente (lista atualizavel)
- reconexao automatica da ultima COM usada ao iniciar
- opcao de fechar para bandeja (rodar em segundo plano)
- enviar ACT e STBY para o LCD
- salvar, carregar e excluir perfis de frequencia
- importar e exportar perfis em JSON
- enviar perfil selecionado direto para o LCD
- modo automatico de leitura do MSFS 2024 (SimConnect)
- envio automatico para o LCD somente quando a frequencia muda

## Arquivos

- `app.py`: app desktop (CustomTkinter)
- `requirements.txt`: dependencias Python
- `run_bridge.bat`: atalho para executar no Windows
- `build_exe.bat`: gera executavel `.exe` para distribuicao
- `build_installer.bat`: gera instalador `.exe` (Inno Setup)
- `INSTALACAO_WINDOWS.md`: guia de instalacao em outros PCs
- `profiles.json`: criado automaticamente quando salvar perfis
- `settings.json`: criado automaticamente para lembrar tema/COM/opcoes

Extras de release:

- `installer/PainelFS2024Configurator.iss`: script do instalador
- `.github/workflows/release-bridge.yml`: build automatico de release no GitHub

## Como executar

1. Instale Python 3 no Windows.
2. Abra terminal nesta pasta.
3. Instale dependencia:

	pip install -r requirements.txt

4. Execute:

	python app.py

Ou rode direto:

	run_bridge.bat

## Modo automatico MSFS (novo)

1. Abra o MSFS 2024.
2. Conecte o Arduino na COM correta.
3. No app, marque "Ativar leitura automatica do MSFS".
4. (Opcional) mantenha marcado "Enviar automaticamente para o LCD".

Com isso, ACT/STBY sao atualizadas no app e enviadas ao LCD quando mudarem.

Se o MSFS nao estiver aberto, o app fica em modo de espera e continua funcional no modo manual.

## Branding e icone

Para usar icone personalizado no app e no executavel:

1. Coloque um arquivo `app.ico` em `assets/branding/app.ico`.
2. Rode `build_exe.bat` novamente.

Se o arquivo nao existir, o app continua funcionando normalmente sem icone customizado.

## Build e release

Build local do executavel:

- `build_exe.bat`

Build local do instalador (requer Inno Setup 6):

- `build_installer.bat`

Build automatico no GitHub Releases:

- criar tag no formato `bridge-v1.2.0`
- dar push da tag
- workflow `Build Bridge Executable` gera e anexa o `.exe` na release

## Protocolo Serial usado

Baud rate: 115200

Comandos:

- ACT:124.850
- STBY:121.700

Cada comando termina com `\n`.

## Proximos passos

- criar tela de configuracao de perfis por aeronave
- melhorar validacoes e logs para diagnostico
- criar fallback de leitura para mais radios (COM2/NAV) no auto-sync
