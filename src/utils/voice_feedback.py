import threading
import pyttsx3

class VoiceFeedback:
    """Control de voz (TTS) con pyttsx3, optimizado para fluidez y voz Sabina."""
    def __init__(self, velocidad=150):
        self._rate = velocidad
        self._voz_id = None
        self._lock = threading.Lock()

        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            for v in voices:
                if "Sabina" in v.name or "ES-MX" in v.id:
                    self._voz_id = v.id
                    break
            if self._voz_id:
                self.engine.setProperty('voice', self._voz_id)
            self.engine.setProperty('rate', self._rate)
            self._backend = 'pyttsx3'
        except Exception:
            self.engine = None
            self._backend = 'none'

    def speak(self, texto):
        """Habla en un hilo aparte."""
        if not texto or not self.engine:
            print("[TTS none]", texto)
            return
        def _run():
            try:
                with self._lock:
                    self.engine.say(texto)
                    self.engine.runAndWait()
            except Exception as e:
                print("[TTS error]", e)
        threading.Thread(target=_run, daemon=True).start()

    def stop(self):
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass

    def status(self):
        return self._backend

    @property
    def available(self):
        return self._backend != 'none'
