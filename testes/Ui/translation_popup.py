import tkinter as tk
from tkinter import scrolledtext, ttk
import queue

from Config.settings import OCR_LANGUAGE_PROFILES
from Ui.region_selector import configure_capture_region


class TranslationPopup:
    def __init__(
        self,
        message_queue,
        stop_event,
        shared_state,
        state_lock,
        title="Tradução em Tempo Real",
    ):
        self.message_queue = message_queue
        self.stop_event = stop_event
        self.shared_state = shared_state
        self.state_lock = state_lock
        self.is_closed = False

        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("980x540")
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        with self.state_lock:
            initial_trigger = self.shared_state["capture_trigger_key"]
            initial_profile = self.shared_state["ocr_profile"]
            initial_bridge = self.shared_state.get("force_english_bridge", False)
            initial_interval = self.shared_state.get("capture_interval", 2)

        container = tk.Frame(self.root, padx=10, pady=10)
        container.pack(fill="both", expand=True)

        controls = tk.Frame(container)
        controls.pack(fill="x", pady=(0, 10))

        self.pause_button = tk.Button(
            controls, text="Pausar", width=12, command=self.toggle_pause
        )
        self.pause_button.pack(side="left", padx=(0, 8))

        tk.Label(controls, text="Tecla captura:").pack(side="left")

        self.trigger_var = tk.StringVar(value=initial_trigger)
        self.trigger_entry = tk.Entry(controls, textvariable=self.trigger_var, width=8)
        self.trigger_entry.pack(side="left", padx=(6, 8))

        self.apply_key_button = tk.Button(
            controls, text="Aplicar tecla", command=self.apply_trigger_key
        )
        self.apply_key_button.pack(side="left", padx=(0, 12))

        tk.Label(controls, text="Perfil OCR:").pack(side="left")

        self.profile_var = tk.StringVar(value=initial_profile)
        self.profile_combo = ttk.Combobox(
            controls,
            textvariable=self.profile_var,
            values=list(OCR_LANGUAGE_PROFILES.keys()),
            state="readonly",
            width=12,
        )
        self.profile_combo.pack(side="left", padx=(6, 8))

        self.apply_profile_button = tk.Button(
            controls, text="Aplicar perfil", command=self.apply_ocr_profile
        )
        self.apply_profile_button.pack(side="left", padx=(0, 12))

        self.bridge_var = tk.BooleanVar(value=initial_bridge)
        self.bridge_check = tk.Checkbutton(
            controls,
            text="Traduzir via inglês",
            variable=self.bridge_var,
            command=self.apply_translation_bridge,
        )
        self.bridge_check.pack(side="left", padx=(0, 12))

        tk.Label(controls, text="Intervalo (s):").pack(side="left")

        self.interval_var = tk.StringVar(value=str(initial_interval))
        self.interval_entry = tk.Entry(
            controls, textvariable=self.interval_var, width=8
        )
        self.interval_entry.pack(side="left", padx=(6, 8))

        self.apply_interval_button = tk.Button(
            controls, text="Aplicar intervalo", command=self.apply_capture_interval
        )
        self.apply_interval_button.pack(side="left", padx=(0, 12))

        self.configure_region_button = tk.Button(
            controls, text="Configurar área", command=self.reconfigure_region
        )
        self.configure_region_button.pack(side="left")

        self.label_detected = tk.Label(
            container, text="Texto Detectado", font=("Arial", 12, "bold")
        )
        self.label_detected.pack(anchor="w", pady=(0, 4))

        self.detected_area = scrolledtext.ScrolledText(
            container, wrap=tk.WORD, font=("Arial", 11), height=6
        )
        self.detected_area.pack(fill="both", expand=True, pady=(0, 10))
        self.detected_area.config(state="disabled")

        self.label_translated = tk.Label(
            container, text="Texto Traduzido", font=("Arial", 12, "bold")
        )
        self.label_translated.pack(anchor="w", pady=(0, 4))

        self.translated_area = scrolledtext.ScrolledText(
            container, wrap=tk.WORD, font=("Arial", 12), height=8
        )
        self.translated_area.pack(fill="both", expand=True)
        self.translated_area.config(state="disabled")

        self.status_label = tk.Label(
            container, text="Aguardando captura...", anchor="w"
        )
        self.status_label.pack(fill="x", pady=(8, 0))

    def _on_close(self):
        self.is_closed = True
        self.stop_event.set()
        self.root.destroy()

    def _set_text(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.config(state="disabled")

    def set_status(self, text):
        self.status_label.config(text=text)

    def apply_trigger_key(self):
        trigger_key = self.trigger_var.get().strip().lower()

        if not trigger_key:
            self.set_status("Informe uma tecla válida.")
            return

        with self.state_lock:
            self.shared_state["capture_trigger_key"] = trigger_key

        self.set_status(f"Tecla de captura atualizada para {trigger_key.upper()}.")

    def apply_ocr_profile(self):
        selected_profile = self.profile_var.get().strip()

        if selected_profile not in OCR_LANGUAGE_PROFILES:
            self.set_status("Perfil OCR inválido.")
            return

        with self.state_lock:
            self.shared_state["ocr_profile"] = selected_profile
            self.shared_state["force_refresh"] = True

        self.set_status(f"Perfil OCR alterado para '{selected_profile}'.")

    def apply_translation_bridge(self):
        bridge_enabled = self.bridge_var.get()

        with self.state_lock:
            self.shared_state["force_english_bridge"] = bridge_enabled
            self.shared_state["force_refresh"] = True

        if bridge_enabled:
            self.set_status("Tradução via inglês ativada.")
        else:
            self.set_status("Tradução via inglês desativada.")

    def apply_capture_interval(self):
        raw_value = self.interval_var.get().strip().replace(",", ".")

        try:
            interval = float(raw_value)

            if interval <= 0:
                self.set_status("O intervalo deve ser maior que zero.")
                return

            if interval < 0.2:
                self.set_status("Use um intervalo maior ou igual a 0.2s.")
                return

            with self.state_lock:
                self.shared_state["capture_interval"] = interval
                self.shared_state["force_refresh"] = True

            self.set_status(f"Intervalo de captura alterado para {interval:.2f}s.")

        except ValueError:
            self.set_status("Informe um número válido para o intervalo.")

    def toggle_pause(self):
        with self.state_lock:
            self.shared_state["paused"] = not self.shared_state["paused"]
            paused = self.shared_state["paused"]

        self.pause_button.config(text="Retomar" if paused else "Pausar")
        self.set_status("Captura pausada." if paused else "Captura retomada.")

    def reconfigure_region(self):
        self.apply_trigger_key()

        with self.state_lock:
            self.shared_state["paused"] = True
            trigger_key = self.shared_state["capture_trigger_key"]

        self.pause_button.config(text="Retomar")
        self.set_status(
            f"Abra a tela desejada e pressione {trigger_key.upper()} para capturar."
        )

        self.root.update_idletasks()
        self.root.withdraw()
        self.root.attributes("-topmost", False)

        try:
            new_region = configure_capture_region(trigger_key=trigger_key)
        finally:
            self.root.deiconify()
            self.root.attributes("-topmost", True)
            self.root.lift()

        with self.state_lock:
            if new_region:
                self.shared_state["capture_region"] = new_region
                self.shared_state["force_refresh"] = True
                self.set_status(f"Nova área aplicada: {new_region}")
            else:
                self.set_status("Configuração cancelada.")

            self.shared_state["paused"] = False

        self.pause_button.config(text="Pausar")

    def poll_queue(self):
        if self.is_closed:
            return

        latest_payload = None

        try:
            while True:
                latest_payload = self.message_queue.get_nowait()
        except queue.Empty:
            pass

        if latest_payload:
            detected_text = latest_payload.get("detected_text", "")
            translated_text = latest_payload.get("translated_text", "")

            self._set_text(self.detected_area, detected_text)
            self._set_text(self.translated_area, translated_text)
            self.status_label.config(text="Atualizado")

        self.root.after(120, self.poll_queue)

    def run(self):
        self.poll_queue()
        self.root.mainloop()
