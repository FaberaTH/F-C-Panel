#include <Joystick.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <string.h>
#include <stdio.h>

// ==============================
// Painel FS2024 - Arduino Leonardo
// ==============================
// Objetivo:
// - 4 botoes momentaneos (FUEL PUMP, PITOT, W/LT TST, FIRE TST)
// - 6 chaves de 2 posicoes (BATT, GENE, A/COL, HORN, AVIONICS, ENG.START)
// - Chaves geram 2 eventos separados: ON e OFF
// - Display LCD 1602 I2C para frequencia (ACT/STBY)
//
// Hardware esperado:
// - Entradas com INPUT_PULLUP
// - Botao/chave fecha para GND quando acionado
// - LCD 1602 com modulo I2C (PCF8574), endereco 0x27
//
// Observacao importante (Leonardo):
// - I2C usa SDA/SCL. Evite usar D2 e D3 para botoes/chaves.
//
// Se alguma chave ficar invertida, altere o array SWITCH_ON_IS_LOW.

constexpr uint8_t DEBOUNCE_MS = 25;
constexpr uint16_t PULSE_MS = 60;
constexpr uint32_t SERIAL_BAUD = 115200;

constexpr uint8_t LCD_COLUMNS = 16;
constexpr uint8_t LCD_ROWS = 2;
constexpr uint8_t LCD_I2C_ADDRESS = 0x27;

LiquidCrystal_I2C lcd(LCD_I2C_ADDRESS, LCD_COLUMNS, LCD_ROWS);

// Modo de auto-teste sem hardware:
// 0 = desativado (modo normal)
// 1 = ativado (cicla botoes automaticamente para teste no joy.cpl)
constexpr bool SELF_TEST_NO_HARDWARE = false;
constexpr uint16_t SELF_TEST_STEP_MS = 350;

// ---------- Entradas fisicas ----------
// Ajuste os pinos conforme sua montagem.

constexpr uint8_t MOMENTARY_COUNT = 4;
const uint8_t momentaryPins[MOMENTARY_COUNT] = {
  4,  // FUEL PUMP
  5,  // PITOT
  6,  // W/LT TST
  7   // FIRE TST
};

constexpr uint8_t TOGGLE_COUNT = 6;
const uint8_t togglePins[TOGGLE_COUNT] = {
  8,   // BATT
  9,   // GENE
  10,  // A/COL
  11,  // HORN
  12,  // AVIONICS
  A0   // ENG.START
};

// true  -> considera ON quando pino estiver LOW
// false -> considera ON quando pino estiver HIGH
const bool SWITCH_ON_IS_LOW[TOGGLE_COUNT] = {
  true,  // BATT
  true,  // GENE
  true,  // A/COL
  true,  // HORN
  true,  // AVIONICS
  true   // ENG.START
};

// ---------- Mapeamento de botoes virtuais HID ----------
// Botoes momentaneos: 0..3
constexpr uint8_t BTN_FUEL_PUMP = 0;
constexpr uint8_t BTN_PITOT = 1;
constexpr uint8_t BTN_WLT_TST = 2;
constexpr uint8_t BTN_FIRE_TST = 3;

// Chaves com eventos ON/OFF (2 botoes por chave):
// BATT ON=4  OFF=5
// GENE ON=6  OFF=7
// A/COL ON=8 OFF=9
// HORN ON=10 OFF=11
// AVIONICS ON=12 OFF=13
// ENG.START ON=14 OFF=15
constexpr uint8_t TOGGLE_EVENT_BASE = 4;

constexpr uint8_t TOTAL_BUTTONS = TOGGLE_EVENT_BASE + (TOGGLE_COUNT * 2);

Joystick_ Joystick(
  JOYSTICK_DEFAULT_REPORT_ID,
  JOYSTICK_TYPE_JOYSTICK,
  TOTAL_BUTTONS,
  0,
  false, false, false,
  false, false, false,
  false, false,
  false, false, false
);

struct DebouncedInput {
  uint8_t pin;
  bool stableState;
  bool lastRaw;
  unsigned long lastTransitionMs;
};

DebouncedInput momentaryInputs[MOMENTARY_COUNT];
DebouncedInput toggleInputs[TOGGLE_COUNT];

bool pulseActive[TOTAL_BUTTONS] = {false};
unsigned long pulseReleaseAt[TOTAL_BUTTONS] = {0};

uint8_t selfTestCurrentButton = 0;
unsigned long selfTestLastStepMs = 0;

char activeFreq[10] = "124.850";
char standbyFreq[10] = "121.700";
bool lcdNeedsRefresh = true;

char serialLineBuffer[32];
uint8_t serialLineLength = 0;

static inline void copyFreqText(char *dst, const char *src, size_t dstLen) {
  size_t i = 0;

  while (i < (dstLen - 1) && src[i] != '\0') {
    char c = src[i];
    // Aceita somente formato simples de frequencia.
    bool allowed = (c >= '0' && c <= '9') || c == '.';
    if (!allowed) {
      break;
    }
    dst[i] = c;
    i++;
  }

  dst[i] = '\0';
}

static inline void writeLcdLine(uint8_t row, const char *text) {
  lcd.setCursor(0, row);

  uint8_t i = 0;
  while (i < LCD_COLUMNS && text[i] != '\0') {
    lcd.print(text[i]);
    i++;
  }

  while (i < LCD_COLUMNS) {
    lcd.print(' ');
    i++;
  }
}

static inline void refreshLcdIfNeeded() {
  if (!lcdNeedsRefresh) {
    return;
  }

  char line0[17];
  char line1[17];
  snprintf(line0, sizeof(line0), "ACT %s", activeFreq);
  snprintf(line1, sizeof(line1), "STBY %s", standbyFreq);

  writeLcdLine(0, line0);
  writeLcdLine(1, line1);
  lcdNeedsRefresh = false;
}

static inline void processSerialCommand(const char *line) {
  // Protocolo simples via Serial USB:
  // ACT:124.850
  // STBY:121.700
  if (strncmp(line, "ACT:", 4) == 0) {
    copyFreqText(activeFreq, line + 4, sizeof(activeFreq));
    lcdNeedsRefresh = true;
    return;
  }

  if (strncmp(line, "STBY:", 5) == 0) {
    copyFreqText(standbyFreq, line + 5, sizeof(standbyFreq));
    lcdNeedsRefresh = true;
  }
}

static inline void pollSerialCommands() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();

    if (c == '\r') {
      continue;
    }

    if (c == '\n') {
      serialLineBuffer[serialLineLength] = '\0';
      processSerialCommand(serialLineBuffer);
      serialLineLength = 0;
      continue;
    }

    if (serialLineLength < (sizeof(serialLineBuffer) - 1)) {
      serialLineBuffer[serialLineLength++] = c;
    }
  }
}

static inline void beginInput(DebouncedInput &in, uint8_t pin) {
  in.pin = pin;
  pinMode(pin, INPUT_PULLUP);
  bool raw = digitalRead(pin);
  in.stableState = raw;
  in.lastRaw = raw;
  in.lastTransitionMs = millis();
}

// Retorna true quando estado estavel mudou.
static inline bool updateDebounce(DebouncedInput &in, unsigned long nowMs) {
  bool raw = digitalRead(in.pin);

  if (raw != in.lastRaw) {
    in.lastRaw = raw;
    in.lastTransitionMs = nowMs;
  }

  if ((nowMs - in.lastTransitionMs) >= DEBOUNCE_MS && in.stableState != in.lastRaw) {
    in.stableState = in.lastRaw;
    return true;
  }

  return false;
}

static inline void triggerPulse(uint8_t virtualButton, unsigned long nowMs) {
  Joystick.setButton(virtualButton, 1);
  pulseActive[virtualButton] = true;
  pulseReleaseAt[virtualButton] = nowMs + PULSE_MS;
}

static inline void updatePulses(unsigned long nowMs) {
  for (uint8_t i = 0; i < TOTAL_BUTTONS; i++) {
    if (pulseActive[i] && (long)(nowMs - pulseReleaseAt[i]) >= 0) {
      Joystick.setButton(i, 0);
      pulseActive[i] = false;
    }
  }
}

static inline bool pinStateMeansOn(uint8_t toggleIndex, bool stablePinState) {
  if (SWITCH_ON_IS_LOW[toggleIndex]) {
    return stablePinState == LOW;
  }
  return stablePinState == HIGH;
}

static inline void runSelfTest(unsigned long nowMs) {
  if ((nowMs - selfTestLastStepMs) < SELF_TEST_STEP_MS) {
    updatePulses(nowMs);
    return;
  }

  selfTestLastStepMs = nowMs;
  triggerPulse(selfTestCurrentButton, nowMs);
  selfTestCurrentButton++;

  if (selfTestCurrentButton >= TOTAL_BUTTONS) {
    selfTestCurrentButton = 0;
  }

  updatePulses(nowMs);
}

void setup() {
  Serial.begin(SERIAL_BAUD);

  lcd.init();
  lcd.backlight();
  lcd.clear();
  refreshLcdIfNeeded();

  for (uint8_t i = 0; i < MOMENTARY_COUNT; i++) {
    beginInput(momentaryInputs[i], momentaryPins[i]);
  }

  for (uint8_t i = 0; i < TOGGLE_COUNT; i++) {
    beginInput(toggleInputs[i], togglePins[i]);
  }

  Joystick.begin();

  // Garante estado inicial dos botoes momentaneos em OFF.
  for (uint8_t i = 0; i < MOMENTARY_COUNT; i++) {
    Joystick.setButton(i, 0);
  }

  // Garante estado inicial dos botoes de evento em OFF.
  for (uint8_t i = TOGGLE_EVENT_BASE; i < TOTAL_BUTTONS; i++) {
    Joystick.setButton(i, 0);
  }
}

void loop() {
  unsigned long nowMs = millis();

  pollSerialCommands();
  refreshLcdIfNeeded();

  if (SELF_TEST_NO_HARDWARE) {
    runSelfTest(nowMs);
    return;
  }

  // Botoes momentaneos: estado pressionado enquanto mantido.
  for (uint8_t i = 0; i < MOMENTARY_COUNT; i++) {
    bool changed = updateDebounce(momentaryInputs[i], nowMs);
    if (changed) {
      bool pressed = (momentaryInputs[i].stableState == LOW);
      Joystick.setButton(i, pressed ? 1 : 0);
    }
  }

  // Chaves: gera pulso em botoes separados para ON e OFF.
  for (uint8_t i = 0; i < TOGGLE_COUNT; i++) {
    bool changed = updateDebounce(toggleInputs[i], nowMs);
    if (changed) {
      bool isOn = pinStateMeansOn(i, toggleInputs[i].stableState);
      uint8_t onButton = TOGGLE_EVENT_BASE + (i * 2);
      uint8_t offButton = onButton + 1;

      if (isOn) {
        triggerPulse(onButton, nowMs);
      } else {
        triggerPulse(offButton, nowMs);
      }
    }
  }

  updatePulses(nowMs);
}
