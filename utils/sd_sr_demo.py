"""
Demo: capturar audio con sounddevice y pasar a SpeechRecognition sin PyAudio.

Uso:
    python -m utils.sd_sr_demo

Requisitos:
    pip install sounddevice numpy SpeechRecognition

Nota: SpeechRecognition seguirá usando Google online por defecto para el reconocimiento.
"""
import sys
import time

try:
    import sounddevice as sd
    import numpy as np
    import speech_recognition as sr
except Exception as e:
    print("Dependencias necesarias no disponibles:", e)
    print("Instala: pip install sounddevice numpy SpeechRecognition")
    sys.exit(1)

SAMPLE_RATE = 16000
DURATION = 8.0  # segundos por grabación de prueba


def record_seconds(duration=DURATION, srate=SAMPLE_RATE):
    """Graba `duration` segundos y devuelve un numpy array dtype=int16"""
    print(f"Grabando {duration} s a {srate} Hz... (habla ahora)")
    try:
        rec = sd.rec(int(duration * srate), samplerate=srate, channels=1, dtype='int16')
        sd.wait()
        return rec.flatten()
    except Exception as e:
        print("Error capturando audio:", e)
        raise


def numpy_to_audio_data(np_array, srate=SAMPLE_RATE):
    """Convierte un numpy int16 array a sr.AudioData"""
    if np_array.dtype != np.int16:
        # normalizar y convertir a int16
        np_array = (np_array * 32767).astype(np.int16)
    pcm_bytes = np_array.tobytes()
    return sr.AudioData(pcm_bytes, sample_rate=srate, sample_width=2)


def rms_from_numpy(np_array):
    a = np_array.astype('float32') / 32768.0
    return float(np.sqrt((a * a).mean()))


def main():
    r = sr.Recognizer()

    print("Demo sounddevice -> SpeechRecognition")
    print("Presiona Ctrl-C para salir")
    # Mostrar dispositivos detectados y el dispositivo de entrada por defecto
    try:
        print("\nDispositivos de audio detectados:")
        devs = sd.query_devices()
        for i, d in enumerate(devs):
            # imprimir solo nombre y max_input_channels para no saturar
            print(f"  [{i}] {d['name']} (max_input_channels={d.get('max_input_channels')})")

        default_dev = sd.default.device
        # sd.default.device puede ser un entero o una tupla (input, output)
        input_idx = None
        if isinstance(default_dev, tuple) or isinstance(default_dev, list):
            input_idx = default_dev[0]
        else:
            input_idx = default_dev

        if input_idx is None:
            print("No hay dispositivo de entrada por defecto configurado en sounddevice.")
        else:
            try:
                dinfo = sd.query_devices(int(input_idx))
                print(f"\nDispositivo de entrada por defecto: [{int(input_idx)}] {dinfo['name']}")
            except Exception:
                print(f"\nDispositivo de entrada por defecto: índice {input_idx} (no se pudo obtener nombre)")
    except Exception as e:
        print("No se pudieron listar dispositivos de audio:", e)

    try:
        while True:
            try:
                data = record_seconds()
            except Exception:
                print("Fallo al grabar. Revisa permisos/dispositivo y prueba de nuevo.")
                time.sleep(1.0)
                continue

            rms = rms_from_numpy(data)
            print(f"RMS de la señal: {rms:.6f}")
            if rms < 1e-4:
                print("Señal muy baja (micrófono silenciado o lejos). Verifica volumen/permiso.)")

            # imprimir nombre del dispositivo usado para esta grabación (diagnóstico)
            try:
                dev = sd.default.device
                in_idx = dev[0] if isinstance(dev, (list, tuple)) else dev
                if in_idx is not None:
                    info = sd.query_devices(int(in_idx))
                    print(f"Dispositivo usado para grabación: [{int(in_idx)}] {info['name']}")
            except Exception:
                pass

            audio_data = numpy_to_audio_data(data)

            try:
                text = r.recognize_google(audio_data, language='es-ES')
                print("Reconocido:", text)
            except sr.UnknownValueError:
                print("No se entendió el audio (UnknownValueError)")
            except sr.RequestError as e:
                print("Error con el servicio de reconocimiento (RequestError):", e)

            print("---")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nDemo terminada por usuario")


if __name__ == '__main__':
    main()
