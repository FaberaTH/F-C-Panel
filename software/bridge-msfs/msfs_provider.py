import time
from typing import Optional, Tuple


class MsfsFrequencyProvider:
    def __init__(self) -> None:
        self._sm = None
        self._aq = None
        self._connected = False
        self._last_connect_attempt = 0.0
        self._connect_retry_seconds = 3.0
        self._last_error = "Nao conectado"

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def last_error(self) -> str:
        return self._last_error

    def disconnect(self) -> None:
        self._sm = None
        self._aq = None
        self._connected = False

    def _try_connect(self) -> None:
        now = time.monotonic()
        if (now - self._last_connect_attempt) < self._connect_retry_seconds:
            return

        self._last_connect_attempt = now

        try:
            # Import local para manter o app funcional mesmo sem a lib instalada.
            from SimConnect import AircraftRequests, SimConnect

            self._sm = SimConnect()
            self._aq = AircraftRequests(self._sm, _time=500)
            self._connected = True
            self._last_error = "OK"
        except FileNotFoundError:
            self.disconnect()
            self._last_error = "❌ Flight Simulator 2024 nao esta rodando"
        except OSError as exc:
            # OSError com "Cannot find" ou similar indica MSFS nao rodando
            if "cannot find" in str(exc).lower() or "not found" in str(exc).lower():
                self.disconnect()
                self._last_error = "❌ Flight Simulator 2024 nao esta rodando"
            else:
                self.disconnect()
                self._last_error = f"Erro de conexao: {str(exc)}"
        except Exception as exc:
            self.disconnect()
            error_str = str(exc)
            # Se menciona dynlib/dll e nao encontrado, eh provavelmente MSFS nao rodando
            if "failed to load" in error_str.lower() or "dynlib" in error_str.lower():
                self._last_error = "❌ Flight Simulator 2024 nao esta rodando"
            else:
                self._last_error = error_str

    @staticmethod
    def _format_frequency(raw_value) -> Optional[str]:
        if raw_value is None:
            return None

        if isinstance(raw_value, str):
            cleaned = raw_value.strip()
            return cleaned if cleaned else None

        try:
            value = float(raw_value)
        except Exception:
            return None

        # Heuristica para cobrir formatos comuns de dados de frequencia.
        if value > 1000000.0:
            value = value / 1000000.0
        elif value > 1000.0:
            value = value / 1000.0

        return f"{value:.3f}"

    def poll_frequencies(self) -> Tuple[Optional[str], Optional[str]]:
        if not self._connected:
            self._try_connect()
            if not self._connected:
                return None, None

        try:
            act_raw = self._aq.get("COM ACTIVE FREQUENCY:1")
            stby_raw = self._aq.get("COM STANDBY FREQUENCY:1")

            act = self._format_frequency(act_raw)
            stby = self._format_frequency(stby_raw)
            self._last_error = "OK"
            return act, stby
        except Exception as exc:
            self.disconnect()
            self._last_error = str(exc)
            return None, None
