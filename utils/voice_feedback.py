"""
Simple wrapper around pyttsx3 for local TTS feedback.
"""

try:
    import pyttsx3
    _TTS_AVAILABLE = True
except Exception:
    pyttsx3 = None
    _TTS_AVAILABLE = False


class VoiceFeedback:
    """Pequeña envoltura para pyttsx3.

    Métodos:
    - speak(text): reproduce texto (bloqueante)
    - stop(): intenta parar el motor
    """

    def __init__(self, voice_rate=180, volume=1.0):
        self.engine = None
        if _TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                try:
                    self.engine.setProperty('rate', voice_rate)
                except Exception:
                    pass
                try:
                    self.engine.setProperty('volume', float(volume))
                except Exception:
                    pass
            except Exception:
                self.engine = None

    def speak(self, text):
        if not self.engine:
            return
        try:
            # pyttsx3 runAndWait es bloqueante; lo usamos porque queremos asegurar confirmación audible
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception:
            pass

    def stop(self):
        if not self.engine:
            return
        try:
            self.engine.stop()
        except Exception:
            pass
