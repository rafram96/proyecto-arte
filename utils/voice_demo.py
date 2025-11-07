"""
Prueba rápida para voice_listener + voice_feedback.

Ejecución recomendada desde la raíz del proyecto:

    python -m utils.voice_demo

El script intentará importar `utils.voice_listener` y `utils.voice_feedback`, arrancará el listener
(y reproducirá confirmaciones por TTS). Pulsa Ctrl-C para terminar.
"""

import time
import sys
import os

# Permitir ejecución como módulo desde la raíz del repo
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from utils.voice_listener import VoiceListener
    from utils.voice_feedback import VoiceFeedback
    HAS_UTILS = True
except Exception as e:
    print("No se pudieron importar las utilidades de voz (voice_listener/voice_feedback).", e)
    HAS_UTILS = False


def main():
    print("Voice demo inicializando...")

    if not HAS_UTILS:
        print("")
        print("Asegúrate de ejecutar desde la raíz del repositorio con: python -m utils.voice_demo")
        print("Y de haber instalado dependencias opcionales (SpeechRecognition, pyttsx3, pyaudio).")
        return

    vf = VoiceFeedback()

    def callback(text):
        # callback simple que se imprime y devuelve una confirmación para TTS
        print(f"[CALLBACK] Comando reconocido: '{text}'")
        # construir respuesta corta para TTS
        # evitar respuestas largas para no bloquear demasiado
        reply = f"Confirmado: {text}"
        return reply

    vl = VoiceListener(command_callback=callback, feedback=vf, language='es-ES', wake_word='lumi', active_timeout=5.0)

    # Probar y mostrar diagnóstico del micrófono antes de arrancar
    try:
        # El probe está disponible en la clase; lo llamamos para mostrar estado
        try:
            vl._probe_microphone()
        except Exception:
            pass
        if not getattr(vl, 'mic_available', False):
            print("\n[Diagnostics] El micrófono parece no estar accesible.")
            err = getattr(vl, 'mic_error', None)
            if err:
                print(f"  - Error detectado: {err}")
            print("  - Comprueba: configuración de privacidad del micrófono, el botón físico/mute, y permisos del antivirus.")
            print("  - También puedes ver la lista de dispositivos detectados más arriba (si la hay).\n")

    except Exception:
        pass

    print("Arrancando listener. Di 'Lumi' seguido de un comando (ej. 'color morado').")
    print("Presiona Ctrl-C para detener.")

    try:
        vl.start()
        # Hilo en background. Mantener el main vivo y mostrar estado cada segundo.
        while True:
            state = getattr(vl, 'state', 'passive')
            sys.stdout.write(f"\rEstado listener: {state}    ")
            sys.stdout.flush()
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nDeteniendo listener...")
    finally:
        try:
            vl.stop()
        except Exception:
            pass
        print("Demo finalizada.")


if __name__ == '__main__':
    main()
