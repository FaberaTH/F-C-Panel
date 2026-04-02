# Painel FS2024 com Arduino Leonardo + LCD 1602 I2C

Este projeto transforma o Arduino Leonardo em um dispositivo USB HID (joystick) reconhecido nativamente pelo Windows e pelo Microsoft Flight Simulator 2024, com display LCD 16x2 I2C para frequencias.

## Estrutura do repositorio

- `firmware/arduino/PainelFS2024/PainelFS2024.ino`: firmware principal do Arduino
- `docs/GUIA_COMPLETO_PAINEL.txt`: guia completo de montagem e testes
- `software/bridge-msfs/`: base para o software de ponte MSFS -> LCD
- `scripts/`: scripts auxiliares futuros
- `assets/`: imagens e recursos do projeto
- `archive/legacy/`: arquivos antigos preservados

Para gravar na placa, abra no Arduino IDE:

- `firmware/arduino/PainelFS2024/PainelFS2024.ino`

## 1) O que o firmware faz

- Le 4 botoes momentaneos (FUEL PUMP, PITOT, W/LT TST, FIRE TST)
- Le 6 chaves ON/OFF (BATT, GENE, A/COL, HORN, AVIONICS, ENG.START)
- Cada chave gera dois eventos HID (ON e OFF)
- Mostra frequencia ativa e standby no LCD 1602 I2C

## 2) Bibliotecas necessarias

Instale no Arduino IDE:

- Joystick Library (MHeironimus)
- LiquidCrystal I2C (biblioteca compativel com `LiquidCrystal_I2C`)

## 3) Pinagem do projeto (Leonardo)

Observacao importante:
- No Leonardo, I2C usa SDA/SCL. Para evitar conflito com o display, os botoes/chaves nao usam D2/D3.

Botoes momentaneos:

- D4: FUEL PUMP
- D5: PITOT
- D6: W/LT TST
- D7: FIRE TST

Chaves ON/OFF:

- D8: BATT
- D9: GENE
- D10: A/COL
- D11: HORN
- D12: AVIONICS
- A0: ENG.START

Todos os pinos de entrada usam INPUT_PULLUP e devem fechar para GND ao acionar.

## 4) Ligacao do LCD 1602 I2C (PCF8574)

LCD -> Arduino Leonardo:

- VCC -> 5V
- GND -> GND
- SDA -> SDA
- SCL -> SCL

Padrao de endereco no sketch:

- 0x27

Se o seu modulo vier em outro endereco (ex.: 0x3F), altere `LCD_I2C_ADDRESS` no arquivo do firmware.

## 5) Mapeamento HID (16 botoes virtuais)

Botoes momentaneos:

- Botao 1 (interno 0): FUEL PUMP
- Botao 2 (interno 1): PITOT
- Botao 3 (interno 2): W/LT TST
- Botao 4 (interno 3): FIRE TST

Eventos das chaves:

- Botao 5 (interno 4): BATT ON
- Botao 6 (interno 5): BATT OFF
- Botao 7 (interno 6): GENE ON
- Botao 8 (interno 7): GENE OFF
- Botao 9 (interno 8): A/COL ON
- Botao 10 (interno 9): A/COL OFF
- Botao 11 (interno 10): HORN ON
- Botao 12 (interno 11): HORN OFF
- Botao 13 (interno 12): AVIONICS ON
- Botao 14 (interno 13): AVIONICS OFF
- Botao 15 (interno 14): ENG.START ON
- Botao 16 (interno 15): ENG.START OFF

## 6) Protocolo serial para atualizar frequencia no LCD

O sketch aceita comandos na Serial USB a 115200 baud.

Comandos:

- `ACT:124.850`
- `STBY:121.700`

Cada comando deve terminar com quebra de linha (`\n`).

Com isso, um software no PC pode ler dados do MSFS e enviar as frequencias para o display.

## 7) Tabela visual de montagem

| Componente | Tipo | Pino Arduino | Botao virtual |
| --- | --- | --- | --- |
| FUEL PUMP | Botao | D4 | 1 |
| PITOT | Botao | D5 | 2 |
| W/LT TST | Botao | D6 | 3 |
| FIRE TST | Botao | D7 | 4 |
| BATT | Chave ON/OFF | D8 | 5 / 6 |
| GENE | Chave ON/OFF | D9 | 7 / 8 |
| A/COL | Chave ON/OFF | D10 | 9 / 10 |
| HORN | Chave ON/OFF | D11 | 11 / 12 |
| AVIONICS | Chave ON/OFF | D12 | 13 / 14 |
| ENG.START | Chave ON/OFF | A0 | 15 / 16 |

## 8) Checklist extra de bancada

- [ ] Leonardo reconhecido no Windows
- [ ] joy.cpl mostra dispositivo OK
- [ ] Barramento GND comum pronto
- [ ] Botoes em D4, D5, D6, D7
- [ ] Chaves em D8, D9, D10, D11, D12 e A0
- [ ] LCD ligado em 5V/GND/SDA/SCL
- [ ] Nenhum pino de sinal ligado em 5V por engano
- [ ] Teste de botoes/chaves no joy.cpl concluido
- [ ] Teste de comandos serial `ACT:` e `STBY:` concluido
