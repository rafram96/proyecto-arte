import threading
import time
import numpy as np

try:
    import sounddevice as sd
    import speech_recognition as sr
except Exception:
    sd = None
    sr = None


class VoiceListener:
    """Escucha continua con wake-word ('Damichi') y callback para comandos."""
    def __init__(self, callback=None, wake_word='Damichi', sample_rate=16000):
        self.callback = callback
        self.wake_word = wake_word.lower()
        self.sample_rate = sample_rate
        self.duration = 2.8  # duración por bloque de escucha pasiva
        self._running = False
        self._thread = None
        self._r = sr.Recognizer() if sr else None
        self._sd_available = sd is not None
        self._sr_available = sr is not None
        self._last_error = None
        self._mic_available = None

    def _rms(self, arr):
        a = arr.astype('float32') / 32768.0
        return float(np.sqrt((a * a).mean()))

    def _record(self, dur):
        return sd.rec(int(dur * self.sample_rate),
                      samplerate=self.sample_rate,
                      channels=1,
                      dtype='int16')

    def _numpy_to_audio_data(self, arr):
        if not self._r:
            return None
        return sr.AudioData(arr.tobytes(), sample_rate=self.sample_rate, sample_width=2)

    def _run(self):
        if not self._sd_available or not self._sr_available:
            while self._running:
                time.sleep(0.5)
            return

        print("[VoiceListener] escuchando pasivamente...")
        while self._running:
            try:
                rec = self._record(self.duration)
                sd.wait()
                rec = rec.flatten()
                rms = self._rms(rec)
                if rms < 0.015:  # calibrado con tus valores típicos
                    continue

                audio = self._numpy_to_audio_data(rec)
                text = self._r.recognize_google(audio, language='es-ES').lower()
                print(f"[Reconocido] {text} (rms={rms:.3f})")

                if self.wake_word in text:
                    print("[VoiceListener] Wake word detectada → modo activo")
                    cmd_rec = self._record(3.0)
                    sd.wait()
                    cmd_audio = self._numpy_to_audio_data(cmd_rec.flatten())
                    cmd = self._r.recognize_google(cmd_audio, language='es-ES').strip()
                    print(f"[Comando] {cmd}")
                    if callable(self.callback):
                        self.callback(cmd)
            except sr.UnknownValueError:
                continue
            except Exception as e:
                self._last_error = str(e)
                time.sleep(0.3)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print("[VoiceListener] iniciado")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        print("[VoiceListener] detenido")

    def is_running(self):
        return self._running

    @property
    def mic_available(self):
        if self._mic_available is None and sd:
            try:
                info = sd.query_devices(sd.default.device[0])
                self._mic_available = True
                print(f"[Mic] {info['name']}")
            except Exception:
                self._mic_available = False
        return self._mic_available

    @property
    def last_error(self):
        return self._last_error
