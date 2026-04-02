import json
import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pystray
import serial
from PIL import Image, ImageDraw
from serial.tools import list_ports

from msfs_provider import MsfsFrequencyProvider


APP_TITLE = "Painel FS2024 Configurator"
APP_VERSION = "1.3.0"
BAUD_RATE = 115200
DEFAULT_TIMEOUT = 1
PROFILES_FILE = "profiles.json"
SETTINGS_FILE = "settings.json"
MSFS_POLL_MS = 700
FREQ_PATTERN = re.compile(r"^\d{3}\.\d{3}$")


class BridgeApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("980x670")
        self.minsize(980, 670)

        self.serial_conn = None
        self.profiles = {}
        self.settings = {}
        self.msfs_provider = MsfsFrequencyProvider()
        self.msfs_job_id = None
        self.last_sent_pair = (None, None)
        self.tray_icon = None
        self.tray_thread = None
        self.is_hidden_to_tray = False

        self.port_var = tk.StringVar(value="")
        self.connection_var = tk.StringVar(value="Desconectado")
        self.active_var = tk.StringVar(value="124.850")
        self.standby_var = tk.StringVar(value="121.700")
        self.profile_name_var = tk.StringVar(value="")
        self.profile_selected_var = tk.StringVar(value="")
        self.auto_msfs_var = tk.BooleanVar(value=False)
        self.auto_send_lcd_var = tk.BooleanVar(value=True)
        self.msfs_status_var = tk.StringVar(value="MSFS: inativo")
        self.appearance_var = tk.StringVar(value="Sistema")
        self.close_to_tray_var = tk.BooleanVar(value=True)
        self.auto_reconnect_var = tk.BooleanVar(value=True)

        self._build_ui()
        self._load_settings()
        self._load_app_icon()
        self._refresh_ports()
        self._load_profiles()
        self._try_auto_reconnect()
        self._append_log("Aplicativo iniciado.")

    def _build_ui(self) -> None:
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=12)
        header.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Painel FS2024 Configurator",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(14, 0), sticky="w")

        ctk.CTkOptionMenu(
            header,
            variable=self.appearance_var,
            values=["Sistema", "Claro", "Escuro"],
            command=self._set_appearance,
            width=140,
        ).grid(row=0, column=1, padx=(0, 16), pady=(12, 0), sticky="e")

        ctk.CTkLabel(
            header,
            text="Software opcional para customizacao, perfis e sync de frequencia para LCD.",
            text_color=("#4B5563", "#9CA3AF"),
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, padx=16, pady=(4, 14), sticky="w")

        ctk.CTkLabel(
            header,
            text=f"v{APP_VERSION}",
            text_color=("#6B7280", "#9CA3AF"),
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=1, padx=(0, 16), pady=(4, 14), sticky="e")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(2, weight=1)

        self._build_serial_card(content)
        self._build_freq_card(content)
        self._build_auto_card(content)
        self._build_profiles_card(content)
        self._build_log_card(content)

    def _build_serial_card(self, parent: ctk.CTkFrame) -> None:
        frame = ctk.CTkFrame(parent, corner_radius=12)
        frame.grid(row=0, column=0, padx=(0, 8), pady=(0, 8), sticky="nsew")
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Conexao Serial", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=4, padx=14, pady=(12, 10), sticky="w"
        )

        ctk.CTkLabel(frame, text="Porta COM").grid(row=1, column=0, padx=(14, 8), pady=6, sticky="w")
        self.port_menu = ctk.CTkOptionMenu(
            frame,
            variable=self.port_var,
            values=["-"],
            command=self._on_port_selected,
        )
        self.port_menu.grid(row=1, column=1, padx=0, pady=6, sticky="ew")

        ctk.CTkButton(frame, text="Atualizar", width=92, command=self._refresh_ports).grid(
            row=1, column=2, padx=6, pady=6
        )
        ctk.CTkButton(frame, text="Conectar", width=92, command=self._connect).grid(
            row=1, column=3, padx=(0, 14), pady=6
        )

        ctk.CTkButton(frame, text="Desconectar", fg_color="#6B7280", hover_color="#4B5563", command=self._disconnect).grid(
            row=2, column=2, columnspan=2, padx=(6, 14), pady=(0, 12), sticky="ew"
        )

        self.connection_label = ctk.CTkLabel(
            frame,
            textvariable=self.connection_var,
            fg_color="#7F1D1D",
            text_color="#F9FAFB",
            corner_radius=8,
            padx=10,
            pady=5,
        )
        self.connection_label.grid(row=2, column=0, columnspan=2, padx=14, pady=(0, 12), sticky="w")

        ctk.CTkSwitch(
            frame,
            text="Reconectar ultima COM ao iniciar",
            variable=self.auto_reconnect_var,
            command=self._save_settings,
        ).grid(row=3, column=0, columnspan=2, padx=14, pady=(0, 10), sticky="w")

        ctk.CTkSwitch(
            frame,
            text="Fechar para bandeja (segundo plano)",
            variable=self.close_to_tray_var,
            command=self._save_settings,
        ).grid(row=3, column=2, columnspan=2, padx=(6, 14), pady=(0, 10), sticky="w")

    def _build_freq_card(self, parent: ctk.CTkFrame) -> None:
        frame = ctk.CTkFrame(parent, corner_radius=12)
        frame.grid(row=0, column=1, padx=(8, 0), pady=(0, 8), sticky="nsew")
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(frame, text="LCD Frequencias", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=4, padx=14, pady=(12, 10), sticky="w"
        )

        ctk.CTkLabel(frame, text="ACT").grid(row=1, column=0, padx=(14, 8), pady=6, sticky="w")
        ctk.CTkEntry(frame, textvariable=self.active_var, placeholder_text="124.850").grid(
            row=1,
            column=1,
            padx=(0, 14),
            pady=6,
            sticky="ew",
        )

        ctk.CTkLabel(frame, text="STBY").grid(row=1, column=2, padx=(0, 8), pady=6, sticky="w")
        ctk.CTkEntry(frame, textvariable=self.standby_var, placeholder_text="121.700").grid(
            row=1,
            column=3,
            padx=(0, 14),
            pady=6,
            sticky="ew",
        )

        ctk.CTkButton(frame, text="Enviar para LCD", command=lambda: self._send_both(True)).grid(
            row=2, column=0, columnspan=4, padx=14, pady=(4, 12), sticky="ew"
        )

    def _build_auto_card(self, parent: ctk.CTkFrame) -> None:
        frame = ctk.CTkFrame(parent, corner_radius=12)
        frame.grid(row=1, column=0, padx=(0, 8), pady=(0, 8), sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="MSFS Auto Sync", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, padx=14, pady=(12, 6), sticky="w"
        )

        ctk.CTkSwitch(
            frame,
            text="Ativar leitura automatica do MSFS",
            variable=self.auto_msfs_var,
            command=self._toggle_auto_msfs,
        ).grid(row=1, column=0, padx=14, pady=(6, 4), sticky="w")

        ctk.CTkSwitch(
            frame,
            text="Enviar automaticamente para o LCD",
            variable=self.auto_send_lcd_var,
        ).grid(row=2, column=0, padx=14, pady=(4, 4), sticky="w")

        self.msfs_label = ctk.CTkLabel(
            frame,
            textvariable=self.msfs_status_var,
            fg_color="#374151",
            text_color="#F9FAFB",
            corner_radius=8,
            padx=10,
            pady=5,
        )
        self.msfs_label.grid(row=3, column=0, padx=14, pady=(8, 12), sticky="w")

    def _build_profiles_card(self, parent: ctk.CTkFrame) -> None:
        frame = ctk.CTkFrame(parent, corner_radius=12)
        frame.grid(row=1, column=1, padx=(8, 0), pady=(0, 8), sticky="nsew")
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Perfis", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=4, padx=14, pady=(12, 10), sticky="w"
        )

        ctk.CTkLabel(frame, text="Nome").grid(row=1, column=0, padx=(14, 8), pady=6, sticky="w")
        ctk.CTkEntry(frame, textvariable=self.profile_name_var).grid(
            row=1, column=1, columnspan=3, padx=(0, 14), pady=6, sticky="ew"
        )

        ctk.CTkLabel(frame, text="Selecionado").grid(row=2, column=0, padx=(14, 8), pady=6, sticky="w")
        self.profile_menu = ctk.CTkOptionMenu(frame, variable=self.profile_selected_var, values=["-"])
        self.profile_menu.grid(row=2, column=1, columnspan=3, padx=(0, 14), pady=6, sticky="ew")

        ctk.CTkButton(frame, text="Salvar", command=self._save_profile).grid(row=3, column=0, padx=(14, 6), pady=6, sticky="ew")
        ctk.CTkButton(frame, text="Carregar", command=self._load_selected_profile).grid(row=3, column=1, padx=6, pady=6, sticky="ew")
        ctk.CTkButton(frame, text="Excluir", fg_color="#B91C1C", hover_color="#991B1B", command=self._delete_profile).grid(
            row=3, column=2, padx=6, pady=6, sticky="ew"
        )
        ctk.CTkButton(frame, text="Enviar", command=self._load_and_send).grid(row=3, column=3, padx=(6, 14), pady=6, sticky="ew")

        ctk.CTkButton(frame, text="Exportar perfis", command=self._export_profiles).grid(
            row=4, column=0, columnspan=2, padx=(14, 6), pady=(4, 12), sticky="ew"
        )
        ctk.CTkButton(frame, text="Importar perfis", command=self._import_profiles).grid(
            row=4, column=2, columnspan=2, padx=(6, 14), pady=(4, 12), sticky="ew"
        )

    def _build_log_card(self, parent: ctk.CTkFrame) -> None:
        frame = ctk.CTkFrame(parent, corner_radius=12)
        frame.grid(row=2, column=0, columnspan=2, padx=0, pady=(0, 0), sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Log de operacoes", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, padx=14, pady=(12, 8), sticky="w"
        )

        self.log_text = ctk.CTkTextbox(frame, height=190)
        self.log_text.grid(row=1, column=0, padx=14, pady=(0, 12), sticky="nsew")
        self.log_text.configure(state="disabled")

    def _append_log(self, msg: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"- {msg}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    @staticmethod
    def _resource_path(*parts: str) -> str:
        """Get config directory path (uses appdirs for safe PyInstaller one-file support)."""
        try:
            import appdirs
            config_dir = appdirs.user_config_dir("PainelFS2024")
        except ImportError:
            # Fallback to APPDATA if appdirs not available
            config_dir = os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), "PainelFS2024")
        
        # Create directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, *parts)

    def _settings_path(self) -> str:
        return self._resource_path(SETTINGS_FILE)

    def _set_appearance(self, value: str, log_change: bool = True) -> None:
        mapping = {"Sistema": "System", "Claro": "Light", "Escuro": "Dark"}
        mode = mapping.get(value, "System")
        ctk.set_appearance_mode(mode)
        if log_change:
            self._append_log(f"Tema alterado para: {value}")
        self._save_settings()

    def _load_settings(self) -> None:
        self.settings = {
            "last_port": "",
            "appearance": "Sistema",
            "close_to_tray": True,
            "auto_reconnect": True,
        }

        path = self._settings_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as file_obj:
                    data = json.load(file_obj)
                if isinstance(data, dict):
                    self.settings.update(data)
            except Exception:
                pass

        appearance = self.settings.get("appearance", "Sistema")
        if appearance not in ["Sistema", "Claro", "Escuro"]:
            appearance = "Sistema"

        self.appearance_var.set(appearance)
        self.close_to_tray_var.set(bool(self.settings.get("close_to_tray", True)))
        self.auto_reconnect_var.set(bool(self.settings.get("auto_reconnect", True)))
        self._set_appearance(appearance, log_change=False)

    def _save_settings(self) -> None:
        self.settings["last_port"] = self.port_var.get().strip()
        self.settings["appearance"] = self.appearance_var.get().strip() or "Sistema"
        self.settings["close_to_tray"] = bool(self.close_to_tray_var.get())
        self.settings["auto_reconnect"] = bool(self.auto_reconnect_var.get())

        with open(self._settings_path(), "w", encoding="utf-8") as file_obj:
            json.dump(self.settings, file_obj, indent=2, ensure_ascii=False)

    def _on_port_selected(self, value: str) -> None:
        if value and value != "Nenhuma porta":
            self.settings["last_port"] = value
            self._save_settings()

    def _load_app_icon(self) -> None:
        icon_path = self._resource_path("..", "..", "assets", "branding", "app.ico")
        icon_path = os.path.abspath(icon_path)
        if not os.path.exists(icon_path):
            return

        try:
            self.iconbitmap(icon_path)
        except Exception:
            pass

    def _create_tray_image(self) -> Image.Image:
        icon_path = self._resource_path("..", "..", "assets", "branding", "app.ico")
        icon_path = os.path.abspath(icon_path)
        if os.path.exists(icon_path):
            try:
                return Image.open(icon_path)
            except Exception:
                pass

        img = Image.new("RGBA", (64, 64), (19, 31, 52, 255))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((6, 6, 58, 58), radius=12, fill=(35, 60, 96, 255))
        draw.rectangle((15, 18, 49, 46), fill=(38, 105, 145, 255))
        draw.rectangle((19, 24, 45, 28), fill=(145, 255, 214, 255))
        draw.rectangle((19, 34, 45, 38), fill=(145, 255, 214, 255))
        return img

    def _start_tray_icon(self) -> None:
        if self.tray_icon is not None:
            return

        icon_image = self._create_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem("Restaurar", lambda icon, item: self.after(0, self._restore_from_tray)),
            pystray.MenuItem("Sair", lambda icon, item: self.after(0, self._full_shutdown)),
        )

        self.tray_icon = pystray.Icon("painel-fs2024-configurator", icon_image, APP_TITLE, menu)

        def runner() -> None:
            self.tray_icon.run()

        self.tray_thread = threading.Thread(target=runner, daemon=True)
        self.tray_thread.start()

    def _stop_tray_icon(self) -> None:
        if self.tray_icon is not None:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
            self.tray_icon = None

    def _hide_to_tray(self) -> None:
        self.is_hidden_to_tray = True
        self.withdraw()
        self._start_tray_icon()
        self._append_log("Aplicativo minimizado para bandeja do sistema.")

    def _restore_from_tray(self) -> None:
        self.is_hidden_to_tray = False
        self.deiconify()
        self.lift()
        self.focus_force()
        self._stop_tray_icon()
        self._append_log("Aplicativo restaurado da bandeja.")

    def _set_connection_state(self, text: str, connected: bool) -> None:
        self.connection_var.set(text)
        self.connection_label.configure(fg_color="#166534" if connected else "#7F1D1D")

    def _refresh_ports(self) -> None:
        ports = [p.device for p in list_ports.comports()]
        values = ports if ports else ["Nenhuma porta"]
        self.port_menu.configure(values=values)

        remembered = self.settings.get("last_port", "")
        if ports:
            if remembered in ports:
                self.port_var.set(remembered)
            elif self.port_var.get() not in ports:
                self.port_var.set(ports[0])
        else:
            self.port_var.set("Nenhuma porta")

        self._append_log("Lista de portas COM atualizada.")

    def _connect(self, show_feedback: bool = True) -> bool:
        port = self.port_var.get().strip()
        if not port or port == "Nenhuma porta":
            if show_feedback:
                messagebox.showwarning("Porta COM", "Selecione uma porta COM valida.")
            return False

        if self.serial_conn and self.serial_conn.is_open:
            if show_feedback:
                messagebox.showinfo("Serial", "Ja existe conexao ativa.")
            return True

        try:
            self.serial_conn = serial.Serial(port, BAUD_RATE, timeout=DEFAULT_TIMEOUT)
            self._set_connection_state(f"Conectado em {port} @ {BAUD_RATE}", True)
            self._append_log(f"Conectado na porta {port}.")
            self.settings["last_port"] = port
            self._save_settings()
            return True
        except Exception as exc:
            self.serial_conn = None
            self._set_connection_state("Desconectado", False)
            self._append_log(f"Falha ao conectar: {exc}")
            if show_feedback:
                messagebox.showerror("Erro de conexao", str(exc))
            return False

    def _try_auto_reconnect(self) -> None:
        if not self.auto_reconnect_var.get():
            return

        remembered = self.settings.get("last_port", "").strip()
        if not remembered:
            return

        ports = [p.device for p in list_ports.comports()]
        if remembered in ports:
            self.port_var.set(remembered)
            if self._connect(show_feedback=False):
                self._append_log(f"Reconexao automatica ok: {remembered}")

    def _disconnect(self) -> None:
        try:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
                self._append_log("Porta serial desconectada.")
        finally:
            self.serial_conn = None
            self._set_connection_state("Desconectado", False)

    def _send_line(self, text: str) -> None:
        if not (self.serial_conn and self.serial_conn.is_open):
            raise RuntimeError("Conecte primeiro na porta COM do Arduino.")
        self.serial_conn.write((text + "\n").encode("ascii"))

    @staticmethod
    def _is_valid_frequency(text: str) -> bool:
        return bool(FREQ_PATTERN.match(text))

    def _send_both(self, show_feedback: bool) -> None:
        act = self.active_var.get().strip()
        stby = self.standby_var.get().strip()

        if not act or not stby:
            if show_feedback:
                messagebox.showwarning("Frequencias", "Preencha ACT e STBY.")
            return

        if not self._is_valid_frequency(act) or not self._is_valid_frequency(stby):
            if show_feedback:
                messagebox.showwarning("Frequencias", "Formato invalido. Use 000.000")
            return

        try:
            self._send_line(f"ACT:{act}")
            self._send_line(f"STBY:{stby}")
            self.last_sent_pair = (act, stby)
            self._append_log(f"Frequencias enviadas -> ACT {act} | STBY {stby}")
            if show_feedback:
                messagebox.showinfo("LCD", "Frequencias enviadas com sucesso.")
        except Exception as exc:
            self._append_log(f"Erro ao enviar frequencias: {exc}")
            if show_feedback:
                messagebox.showerror("Erro ao enviar", str(exc))

    def _toggle_auto_msfs(self) -> None:
        if self.auto_msfs_var.get():
            self.msfs_status_var.set("MSFS: iniciando...")
            self._append_log("Modo automatico MSFS ativado.")
            self._start_msfs_loop()
        else:
            self._stop_msfs_loop()
            self.msfs_provider.disconnect()
            self.msfs_status_var.set("MSFS: inativo")
            self._append_log("Modo automatico MSFS desativado.")

    def _start_msfs_loop(self) -> None:
        if self.msfs_job_id is None:
            self._msfs_loop()

    def _stop_msfs_loop(self) -> None:
        if self.msfs_job_id is not None:
            self.after_cancel(self.msfs_job_id)
            self.msfs_job_id = None

    def _msfs_loop(self) -> None:
        if not self.auto_msfs_var.get():
            self.msfs_job_id = None
            return

        act, stby = self.msfs_provider.poll_frequencies()

        if self.msfs_provider.connected:
            self.msfs_status_var.set("MSFS: conectado")
            self.msfs_label.configure(fg_color="#166534")
            if act and stby:
                self.active_var.set(act)
                self.standby_var.set(stby)

                if self.auto_send_lcd_var.get():
                    new_pair = (act, stby)
                    if new_pair != self.last_sent_pair:
                        self._send_both(show_feedback=False)
        else:
            self.msfs_status_var.set(f"MSFS: aguardando ({self.msfs_provider.last_error})")
            self.msfs_label.configure(fg_color="#374151")

        self.msfs_job_id = self.after(MSFS_POLL_MS, self._msfs_loop)

    def _profiles_path(self) -> str:
        return self._resource_path(PROFILES_FILE)

    def _load_profiles(self) -> None:
        self.profiles = {}
        path = self._profiles_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as file_obj:
                    data = json.load(file_obj)
                if isinstance(data, dict):
                    self.profiles = data
            except Exception:
                self.profiles = {}

        self._refresh_profile_menu()

    def _write_profiles(self) -> None:
        with open(self._profiles_path(), "w", encoding="utf-8") as file_obj:
            json.dump(self.profiles, file_obj, indent=2, ensure_ascii=False)

    def _refresh_profile_menu(self) -> None:
        names = sorted(self.profiles.keys())
        values = names if names else ["Sem perfis"]
        self.profile_menu.configure(values=values)
        self.profile_selected_var.set(values[0])

    def _save_profile(self) -> None:
        name = self.profile_name_var.get().strip()
        if not name:
            messagebox.showwarning("Perfil", "Informe um nome para o perfil.")
            return

        self.profiles[name] = {"ACT": self.active_var.get().strip(), "STBY": self.standby_var.get().strip()}
        self._write_profiles()
        self._refresh_profile_menu()
        self.profile_selected_var.set(name)
        self._append_log(f"Perfil salvo: {name}")
        messagebox.showinfo("Perfil", f"Perfil '{name}' salvo.")

    def _load_selected_profile(self) -> None:
        name = self.profile_selected_var.get().strip()
        if not name or name == "Sem perfis" or name not in self.profiles:
            messagebox.showwarning("Perfil", "Selecione um perfil valido.")
            return

        data = self.profiles.get(name, {})
        self.active_var.set(data.get("ACT", ""))
        self.standby_var.set(data.get("STBY", ""))
        self.profile_name_var.set(name)
        self._append_log(f"Perfil carregado: {name}")

    def _delete_profile(self) -> None:
        name = self.profile_selected_var.get().strip()
        if not name or name == "Sem perfis" or name not in self.profiles:
            messagebox.showwarning("Perfil", "Selecione um perfil valido.")
            return

        if not messagebox.askyesno("Excluir perfil", f"Excluir perfil '{name}'?"):
            return

        self.profiles.pop(name, None)
        self._write_profiles()
        self._refresh_profile_menu()
        self._append_log(f"Perfil excluido: {name}")

    def _load_and_send(self) -> None:
        self._load_selected_profile()
        self._send_both(show_feedback=True)

    def _export_profiles(self) -> None:
        if not self.profiles:
            messagebox.showwarning("Perfis", "Nao ha perfis para exportar.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Exportar perfis",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
        )
        if not file_path:
            return

        with open(file_path, "w", encoding="utf-8") as file_obj:
            json.dump(self.profiles, file_obj, indent=2, ensure_ascii=False)
        self._append_log(f"Perfis exportados: {file_path}")

    def _import_profiles(self) -> None:
        file_path = filedialog.askopenfilename(title="Importar perfis", filetypes=[("JSON", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file_obj:
                data = json.load(file_obj)
            if not isinstance(data, dict):
                raise ValueError("Arquivo invalido")
        except Exception as exc:
            messagebox.showerror("Importacao", f"Falha ao importar: {exc}")
            return

        self.profiles.update(data)
        self._write_profiles()
        self._refresh_profile_menu()
        self._append_log(f"Perfis importados: {file_path}")

    def _full_shutdown(self) -> None:
        self._save_settings()
        self._stop_msfs_loop()
        self.msfs_provider.disconnect()
        self._disconnect()
        self._stop_tray_icon()
        self.destroy()

    def on_close(self) -> None:
        self._save_settings()
        if self.close_to_tray_var.get():
            self._hide_to_tray()
        else:
            self._full_shutdown()


def main() -> None:
    app = BridgeApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
