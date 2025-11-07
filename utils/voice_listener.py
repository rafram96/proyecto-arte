"""
Voice listener that implements a wake-word ('lumi') passive mode and an active listening window.
Calls a provided callback with the recognized command text and optionally uses a VoiceFeedback instance to speak confirmations.

This implementation uses SpeechRecognition (Google API by default) and is tolerant to missing dependencies.
"""
import threading
import time

try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except Exception:
    sr = None
    _SR_AVAILABLE = False

try:
    import pyaudio
    _PY_AUDIO = True
except Exception:
    pyaudio = None
    _PY_AUDIO = False


class VoiceListener:
    """Listener with passive wake-word and short active listening window.

    Args:
        command_callback(text) -> resp_text: function called with recognized command text; may return a response string to be spoken.
        feedback: optional VoiceFeedback instance (has speak(text)).
        language: language code for recognition (default 'es-ES').
        wake_word: keyword to activate (default 'lumi').
        active_timeout: seconds to wait for the command once wake-word detected (default 5).
    """

    def __init__(self, command_callback, feedback=None, language='es-ES', wake_word='lumi', active_timeout=5.0):
        self.command_callback = command_callback
        self.feedback = feedback
        self.language = language
        self.wake_word = wake_word.lower()
        self.active_timeout = float(active_timeout)
        self._thread = None
        self._stop_ev = threading.Event()
        self.state = 'passive'  # 'passive' or 'active'
        self.mic_available = False
        self.mic_error = None

        if _SR_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                # reduce energy threshold sensitivity to reduce false positives
                self.recognizer.energy_threshold = 300
                self.microphone = None
                try:
                    self.microphone = sr.Microphone()
                except Exception:
                    # system might not provide microphone access
                    self.microphone = None
            except Exception:
                self.recognizer = None
                self.microphone = None
        else:
            self.recognizer = None
            self.microphone = None

    def start(self):
        # antes de arrancar, verificar micro y permisos
        if not _SR_AVAILABLE:
            print("VoiceListener: SpeechRecognition no está disponible; no se iniciará la escucha de voz.")
            return
        if self._thread is not None:
            return

        self._probe_microphone()
        if not self.mic_available:
            # informar y no iniciar el hilo para evitar intentos silenciosos
            msg = f"VoiceListener: micrófono no accesible: {self.mic_error}"
            print(msg)
            return
        self._stop_ev.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_ev.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._thread = None

    def _speak(self, text):
        if self.feedback:
            try:
                self.feedback.speak(text)
            except Exception:
                pass

    def _run(self):
        if not _SR_AVAILABLE or self.recognizer is None or self.microphone is None or not self.mic_available:
            # nothing to do
            return

        # warm-up ambient noise
        with self.microphone as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            except Exception:
                pass

        while not self._stop_ev.is_set():
            try:
                # Passive mode: listen short phrases and check for wake_word
                with self.microphone as source:
                    try:
                        audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                    except Exception:
                        # timeout or other issue, continue
                        continue
                try:
                    text = self.recognizer.recognize_google(audio, language=self.language)
                    if not text:
                        continue
                    text_l = text.strip().lower()
                except Exception:
                    continue

                # check for wake-word
                if self.wake_word in text_l:
                    # enter active listening window
                    self.state = 'active'
                    # immediate feedback
                    try:
                        self._speak('Te escucho')
                    except Exception:
                        pass

                    # listen for command
                    cmd_text = None
                    start_t = time.time()
                    # allow shorter phrase_time_limit, stop early on silence
                    with self.microphone as source:
                        try:
                            audio = self.recognizer.listen(source, timeout=self.active_timeout, phrase_time_limit=self.active_timeout)
                            try:
                                cmd_text = self.recognizer.recognize_google(audio, language=self.language)
                                if cmd_text:
                                    cmd_text = cmd_text.strip().lower()
                            except Exception:
                                cmd_text = None
                        except Exception:
                            cmd_text = None

                    # dispatch command to callback
                    resp = None
                    try:
                        if cmd_text:
                            resp = self.command_callback(cmd_text)
                        else:
                            # no command understood
                            resp = None
                    except Exception:
                        resp = None

                    if resp:
                        try:
                            self._speak(resp)
                        except Exception:
                            pass

                    # return to passive
                    self.state = 'passive'
                # else: continue passive loop
            except Exception:
                # swallow and continue
                time.sleep(0.1)
                continue

    def _probe_microphone(self):
        """Intenta detectar micrófono y permisos. Rellena self.mic_available y self.mic_error.

        Esta función intenta listar dispositivos y hacer un ajuste corto de ruido ambiente para
        validar permisos. No lanza excepciones, solo registra estado.
        """
        self.mic_available = False
        self.mic_error = None

        if not _SR_AVAILABLE:
            self.mic_error = "SpeechRecognition no instalado"
            return

        # intentar listar dispositivos disponibles
        try:
            names = []
            try:
                names = sr.Microphone.list_microphone_names()
            except Exception:
                names = []
            if names:
                print(f"VoiceListener: detectados dispositivos de audio: {len(names)}")
                for i, n in enumerate(names[:10]):
                    print(f"  [{i}] {n}")
            else:
                print("VoiceListener: no se listaron dispositivos de audio (lista vacía)")
        except Exception:
            pass

        # intentar abrir el micrófono y ajustar por ruido ambiente (prueba corta)
        try:
            try:
                mic = sr.Microphone()
            except Exception as e:
                self.mic_error = f"No se pudo acceder al micrófono: {e}"
                return

            # Probar usar el micrófono para ajustar ruido ambiente (corta duración)
            try:
                with mic as source:
                    # tiempo corto para no bloquear demasiado; si el sistema no permite, fallará aquí
                    try:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                        self.microphone = mic
                        self.mic_available = True
                        return
                    except Exception as e:
                        # error al acceder por permisos o bloqueo por antivirus/OS
                        self.mic_error = f"Error al ajustar ruido ambiente: {e}"
                        return
            except Exception as e:
                self.mic_error = f"No se pudo usar el micrófono: {e}"
                return
        except Exception as e:
            # fallback: intentar con pyaudio listando dispositivos
            try:
                if _PY_AUDIO and pyaudio is not None:
                    pa = pyaudio.PyAudio()
                    n = pa.get_device_count()
                    print(f"VoiceListener: PyAudio detectó {n} dispositivos")
                    for i in range(min(n, 10)):
                        info = pa.get_device_info_by_index(i)
                        print(f"  [{i}] {info.get('name')}")
                    pa.terminate()
                self.mic_error = f"Excepción probando micrófono: {e}"
            except Exception:
                self.mic_error = f"Excepción probando micrófono: {e}"
            return
