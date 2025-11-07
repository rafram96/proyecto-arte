import threading
import time

try:
    import speech_recognition as sr
except Exception:
    sr = None


class VoiceListener:
    """Listener ligero: si SpeechRecognition no está instalado, actúa como stub para evitar romper la app.

    Constructor:
        callback(text): función que se llamará cuando se reconozca un comando (texto en str)
        wake_word: palabra de activación (no implementada en stub)
        active_timeout: segundos en modo activo (no implementado en stub)
    """

    def __init__(self, callback=None, wake_word='lumi', active_timeout=4.0):
        self.callback = callback
        self.wake_word = wake_word
        self.active_timeout = active_timeout
        self._running = False
        self._thread = None

        # Si SR está disponible, podríamos implementar un listener real.
        self._sr_available = (sr is not None)

    def _run_stub(self):
        # No hace reconocimiento real; sirve para que start()/stop() existan.
        while self._running:
            time.sleep(0.5)

    def start(self):
        if self._running:
            return
        if not self._sr_available:
            # arrancar stub
            self._running = True
            self._thread = threading.Thread(target=self._run_stub, daemon=True)
            self._thread.start()
            return

        # Si speech_recognition está disponible, podríamos arrancar un hilo que capture audio.
        # Para mantener la librería opcional, preferimos no implementar la lógica completa aquí.
        self._running = True
        self._thread = threading.Thread(target=self._run_stub, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=0.5)
            self._thread = None

    def is_running(self):
        return self._running
