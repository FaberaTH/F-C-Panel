# Instalacao do Configurador em outros computadores (Windows)

Este aplicativo e opcional. O painel HID continua funcionando sem ele.

## Opcao A - Rodar com Python

1. Instalar Python 3.11+ no computador.
2. Abrir terminal na pasta do app.
3. Executar:

   pip install -r requirements.txt
   python app.py

## Opcao B - Gerar executavel (.exe)

No computador de build:

1. Abrir terminal na pasta `software/bridge-msfs`.
2. Executar:

   build_exe.bat

3. O arquivo final fica em:

   dist/PainelFS2024-Configurator.exe

## Distribuicao para outros PCs

1. Copiar o arquivo `PainelFS2024-Configurator.exe` para o outro computador.
2. Executar normalmente (nao precisa instalar Python nesse PC).
3. Conectar o Arduino e selecionar a porta COM correta dentro do app.

## Observacoes

- O Windows pode mostrar aviso de SmartScreen em builds locais sem assinatura digital.
- O app salva perfis no arquivo `profiles.json` na mesma pasta onde ele roda.
- Baud padrao do firmware atual: 115200.
