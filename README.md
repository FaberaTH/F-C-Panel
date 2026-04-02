# Painel FS2024 - Arduino Leonardo + LCD 1602 I2C

Projeto de painel fisico para Microsoft Flight Simulator 2024 com:

- 4 botoes momentaneos
- 6 chaves ON/OFF com eventos separados
- display LCD 16x2 I2C para frequencias ativa e standby
- reconhecimento nativo no Windows como HID (sem app obrigatorio para jogar)

## Status

- Firmware HID: pronto
- LCD 1602 I2C: integrado
- Documentacao de montagem: pronta
- Software de bridge MSFS -> Serial: estrutura criada

## Estrutura do repositorio

- `firmware/arduino/PainelFS2024/PainelFS2024.ino` -> firmware principal
- `docs/GUIA_COMPLETO_PAINEL.txt` -> guia completo de montagem e teste
- `software/bridge-msfs/` -> software opcional de integracao com o simulador
- `assets/` -> imagens e arquivos visuais
- `scripts/` -> scripts auxiliares
- `archive/legacy/` -> historico de arquivos antigos

## Comeco rapido

1. Abra no Arduino IDE o arquivo `firmware/arduino/PainelFS2024/PainelFS2024.ino`.
2. Instale as bibliotecas:
	- Joystick Library (MHeironimus)
	- LiquidCrystal I2C (compativel com `LiquidCrystal_I2C`)
3. Selecione a placa Arduino Leonardo e faca upload.
4. Abra `joy.cpl` no Windows para validar os botoes HID.
5. Ligue o LCD em 5V/GND/SDA/SCL.

## Sketch correto para upload no Arduino IDE

Use sempre este arquivo para a versao mais atual do firmware:

- `firmware/arduino/PainelFS2024/PainelFS2024.ino`

Nao use o arquivo legado em `archive/legacy/`.

## Hardware e pinagem (Leonardo)

Observacao importante:
- D2 e D3 nao sao usados para botoes/chaves, pois o projeto usa I2C no LCD.

Entradas:

- D4: FUEL PUMP
- D5: PITOT
- D6: W/LT TST
- D7: FIRE TST
- D8: BATT
- D9: GENE
- D10: A/COL
- D11: HORN
- D12: AVIONICS
- A0: ENG.START

LCD 1602 I2C (PCF8574):

- VCC -> 5V
- GND -> GND
- SDA -> SDA
- SCL -> SCL

Endereco padrao no firmware: `0x27`.

## Protocolo para frequencia no LCD

Serial USB em 115200 baud.

Comandos aceitos:

- `ACT:124.850`
- `STBY:121.700`

Cada comando deve terminar com `\n`.

## Mapeamento HID

O painel expõe 16 botoes virtuais no Windows:

- 1 a 4: botoes momentaneos
- 5 a 16: eventos ON/OFF das 6 chaves

Detalhamento completo em `docs/GUIA_COMPLETO_PAINEL.txt`.

## Publicacao no GitHub

Texto sugerido para About e topics em `docs/GITHUB_PUBLICACAO.md`.

Distribuicao do software opcional em outros computadores:

- guia em `software/bridge-msfs/INSTALACAO_WINDOWS.md`
- build de executavel em `software/bridge-msfs/build_exe.bat`
- build de instalador em `software/bridge-msfs/build_installer.bat`
- release automatica em `.github/workflows/release-bridge.yml`

## Roadmap

- Bridge MSFS -> Serial para atualizar frequencias automaticamente
- Perfis por aeronave
- Ferramenta de diagnostico de entradas
- Expansao para mais displays e comandos
