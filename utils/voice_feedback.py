import threading
import subprocess

try:
    import pyttsx3
except Exception:
    pyttsx3 = None


class VoiceFeedback:
    """Pequeño wrapper TTS que usa pyttsx3 si está disponible.

    - speak(text): reproduce texto en background (no bloqueante).
    - stop(): intenta detener el motor.
    Si pyttsx3 no está instalado, se hace un fallback a imprimir el texto.
    """

    def __init__(self):
        self._engine = None
        self._lock = threading.Lock()
        self._backend = 'none'
        if pyttsx3 is not None:
            try:
                self._engine = pyttsx3.init()
                voices = self._engine.getProperty('voices')
                for v in voices:
                    if "spanish" in v.name.lower() or "es" in v.id.lower():
                        try:
                            self._engine.setProperty('voice', v.id)
                        except Exception:
                            pass
                        break
                self._backend = 'pyttsx3'
            except Exception:
                self._engine = None

    def speak(self, text: str):
        if not text:
            return
        if self._engine is None:
            # Intentar fallback en Windows usando PowerShell/System.Speech (si está disponible)
            try:
                esc = text.replace("'", "''")
                cmd = [
                    "powershell",
                    "-Command",
                    f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{esc}')"
                ]

                def _ps_run():
                    try:
                        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except Exception:
                        print("[TTS fallback]", text)

                # indicar backend powershell si se ejecuta
                self._backend = 'powershell'

                t = threading.Thread(target=_ps_run, daemon=True)
                t.start()
                return
            except Exception:
                # último recurso: imprimir
                print("[TTS fallback]", text)
                return

        def _run():
            try:
                with self._lock:
                    self._engine.say(text)
                    self._engine.runAndWait()
            except Exception:
                # no queremos que falle la app por TTS
                pass

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def stop(self):
        if self._engine is None:
            return
        try:
            with self._lock:
                self._engine.stop()
        except Exception:
            pass

    def status(self):
        """Retorna una cadena corta indicando el backend TTS actual: 'pyttsx3', 'powershell' o 'none'."""
        return getattr(self, '_backend', 'none')

    @property
    def available(self):
        return self.status() != 'none'
