# Damichi Interactive Painting and Generative Music: Pintura Interactiva con Gestos - Transgresión Digital



LUMI is an experimental application that combines gesture driven painting, optional voice commands, and real time generative music. The project explores digital transgression: physical movement becomes a virtual mark, and the disruption lives in the idea rather than the material.



## Quick startAplicación de pintura artística controlada por gestos de mano, diseñada para explorar el concepto de transgresión en el arte digital.Aplicación de pintura artística controlada por gestos de mano, diseñada para explorar el concepto de transgresión en el arte digital.



1. Create and activate a Python 3.10+ environment.

2. Install dependencies:

## 🚀 Inicio Rápido## 📁 Estructura del Proyecto

```

pip install -r requirements.txt

```

### Windows```

If PyAudio fails on Windows run `pip install pipwin` followed by `pipwin install pyaudio`, or download the appropriate wheel from the Gohlke archive.

```bashproyecto/

Run the application:

start.bat│

```

python src/main.py```├── main.py              # 🎨 Aplicación principal

```

├── config.py            # ⚙️ Configuración global

On launch the console prints usage instructions and, when text to speech is available, plays the phrase "LUMI ACTIVADO" exactly once.

### Manual├── gesture_detector.py  # 🤚 Detección de gestos con MediaPipe

## Controls

```bash├── brushes.py           # 🖌️ Sistema de pinceles

Keyboard shortcuts:

# Ejecutar aplicación├── canvas.py            # 🖼️ Lienzo digital

| Key | Action |

| --- | --- |python src/main.py├── feedback.py          # 👁️ Retroalimentación visual

| q | Quit |

| c | Clear canvas |├── utils.py             # 🔧 Utilidades y herramientas

| 1-8 | Switch preset colors |

| t | Cycle brush mode (line, dab, eraser) |# Verificar sistema├── extensions.py        # ➕ Extensiones y ejemplos

| s | Cycle brush size |

| v | Toggle voice listener (when dependencies are available) |python scripts/demo.py├── test_components.py   # 🧪 Tests unitarios



Gesture overview:│



1. Drawing gesture: index finger extended, middle finger flexed; other fingers are ignored.# Ejecutar tests├── README.md            # 📖 Este archivo

2. Pinch gesture (index and middle fingertips together) selects UI elements.

3. Hovering the pointer over a UI item for 1.2 seconds confirms the selection.python -m pytest tests/ -v├── ARCHITECTURE.md      # 🏗️ Documentación de arquitectura



The Tracking window shows skeletal feedback, while the painting window overlay displays the current tool, color, size, hover timer, voice diagnostics, and the latest confirmation message.```├── CONTRIBUTING.md      # 🤝 Guía de contribución



## Painting pipeline├── requirements.txt     # 📦 Dependencias



1. `PaintApp` captures webcam frames and forwards them to `GestureDetector`.## 📦 Instalación│

2. `GestureDetector` (MediaPipe Hands) extracts landmarks, evaluates drawing and pinch gestures, and returns a smoothed index tip position.

3. `Canvas` manages stroke objects; `BrushManager` defines how each brush type converts points into marks.└── french.py            # 📜 Versión original (legacy)

4. Active strokes accumulate normalized points; `Canvas.render` redraws all strokes every frame.

5. `GestureFeedback` renders the tracking overlay.```bash```

6. The UI layer handles hover and pinch selection and paints the HUD.

pip install -r requirements.txt

Each frame the canvas serializer updates `canvas_state.json`, which external services (such as the music client) can consume. The file is cleared during shutdown.

```## ✨ Características

## Voice control (optional)



Voice input runs when `sounddevice`, `SpeechRecognition`, and a working microphone are present.

## 📁 Estructura del Proyecto- **Detección de gestos inteligente**: Usa MediaPipe Hands para detección precisa

1. The passive listener records short clips until the wake word "lumi" is detected.

2. The active window records a longer clip (default three seconds) to capture the command.- **Múltiples pinceles artísticos**: Línea continua y efecto impresionista (dab)

3. Recognized text is enqueued and processed on the main thread to keep UI operations thread safe.

4. Supported commands cover colors (for example "color azul"), brush modes ("borrador", "modo linea", "modo punteado"), sizes ("grosor fino", "grosor mediano", "grosor grande"), and global actions ("limpiar", "salir").```- **Paleta de colores**: Azul, Verde, Rojo, Amarillo (fácilmente extensible)

5. `VoiceFeedback` plays spoken confirmations using `pyttsx3` when available, otherwise it falls back to the Windows PowerShell `System.Speech` API. The same message appears on screen for three seconds.

proyecto/- **Retroalimentación visual en tiempo real**: Feedback instantáneo del estado del gesto

Console logs expose listener state changes, RMS levels, passive and active recognition results, and queue processing.

├── src/                    # Código fuente- **Arquitectura modular y extensible**: Código organizado por responsabilidades

## Generative music

│   ├── core/              # Componentes principales- **Sistema de tests**: Tests unitarios para componentes críticos

`utils/lyria_realtime.py` streams music from Google Lyria (`lyria-realtime-exp`). Provide a valid API key through the `GOOGLE_AI_API_KEY` or `LYRIA_API_KEY` environment variable.

│   │   ├── config.py      # Configuración- **Utilidades artísticas**: Filtros, exportación, análisis de trazos

Workflow:

│   │   ├── gesture_detector.py- **Fácil de extender**: Sistema de plugins para nuevos pinceles y gestos

1. The class reads `canvas_state.json` to estimate color energy, stroke density, brush mode, and motion speed.

2. A weighted prompt is assembled that maps colors, brushes, and dynamics to instruments, effects, and velocity.│   │   ├── brushes.py

3. The prompt is sent through a WebSocket session to the Lyria realtime endpoint.# LUMI Interactive Painting and Generative Music

4. PCM24 audio chunks (mono, 24 kHz, 16 bit) arrive and are played immediately via PyAudio. The session reconnects on transient failures and stops gracefully when `stop()` is called.

LUMI is an experimental application that combines gesture driven painting, optional voice commands, and real time generative music. The project explores digital transgression: physical movement becomes a virtual mark, and the disruption lives in the idea rather than the material.

Because Lyria returns fully mixed audio, no additional synthesis is performed on the client, preventing unwanted noise.

## Quick start

## Project structure

1. Create and activate a Python 3.10+ environment.

```2. Install dependencies:

src/

  main.py               # Application loop and UI wiring```

  core/pip install -r requirements.txt

    config.py           # Global constants (window sizes, gesture thresholds, UI layout)```

    gesture_detector.py # MediaPipe wrapper and gesture helpers

    brushes.py          # Brush strategies and managerIf PyAudio fails on Windows run `pip install pipwin` followed by `pipwin install pyaudio`, or grab the wheel from the Gohlke archive.

    canvas.py           # Stroke storage, rendering, and serialization

    feedback.py         # Tracking overlay drawingRun the app:

  utils/

    voice_feedback.py   # Text to speech helper```

    voice_listener.py   # Wake word listener and speech recognitionpython src/main.py

    lyria_realtime.py   # Generative music client```

    extensions.py       # Miscellaneous utilities

legacy/                # Archived experiments and prior versionsOn launch the app prints basic instructions and, when text to speech is available, plays the phrase "LUMI ACTIVADO" once.

requirements.txt       # Dependency list

start.bat              # Windows entry point## Controls

```

Keyboard shortcuts:

## Troubleshooting

| Key | Action |

| Problem | Hint || --- | --- |

| --- | --- || q | Quit |

| Camera fails to open | Use `--camera N`, try different backends in `open_camera`, or close other camera applications. || c | Clear canvas |

| Gesture recognition is jittery | Adjust smoothing and threshold values in `core/config.py`. || 1-8 | Switch preset colors |

| Voice listener unavailable | Install `sounddevice` and `SpeechRecognition`, verify microphone permissions, and check RMS logs. || t | Cycle brush mode (line, dab, eraser) |

| Text to speech silent | Install `pyttsx3` and `pypiwin32`, or enable PowerShell `System.Speech`. || s | Cycle brush size |

| Music not playing | Ensure PyAudio is installed and the Lyria API key is provided; watch the console for authentication errors. || v | Toggle voice listener (if dependencies are available) |



## Roadmap ideasGesture overview:



- Automatic PNG exports at a configurable interval.1. Drawing gesture requires the index finger extended and the middle finger flexed. The ring finger is ignored.

- Additional brush styles (spray, watercolor, neon, glitch).2. A pinch gesture (index plus middle finger tips together) selects UI elements.

- Music tempo and dynamics linked to stroke velocity.3. Hovering the pointer over a UI item for 1.2 seconds confirms the selection.

- Collaborative multi user mode.

- Visual audio metering linked to the Lyria stream.UI state is shown in the Tracking window and the painting window overlay (current tool, color, size, hover countdown, voice/TTS status, and last spoken confirmation).



## License



Academic project (UTEC). Intended for educational and experimental use. Review repository history for authorship details.1. `PaintApp` captures frames from the webcam and forwards them to `GestureDetector`.

2. `GestureDetector` (MediaPipe Hands) yields landmarks, checks drawing and pinch gestures, and provides a smoothed index tip position.
3. `Canvas` keeps the active stroke object; `BrushManager` defines how points are rendered (line, dab, eraser).
4. When a stroke is active, points are normalized and appended; `Canvas.render` paints all strokes onto a base image each frame.
5. `GestureFeedback` draws the skeleton overlay in the tracking window.
6. The UI layer displays color/brush/size boxes, hover timers, and voice diagnostics.

The canvas also emits incremental state snapshots (`canvas_state.json`) that other subsystems (such as the music client) can consume. The file is cleared when the app exits.

## Voice control (optional)

Voice input is enabled when `sounddevice`, `SpeechRecognition`, and a microphone are available. The flow is:

1. Passive listener records short clips until it recognizes the wake word "lumi".
2. An active window records a longer clip (default three seconds) and runs Google Speech Recognition on it.
3. Recognized text is enqueued and processed on the main thread to keep the UI thread safe.
4. Supported commands change colors ("color azul"), modes ("borrador", "modo linea", "modo punteado"), brush sizes ("grosor fino" or similar), and global actions ("limpiar", "salir").
5. `VoiceFeedback` plays confirmations using `pyttsx3` if installed; otherwise it falls back to the Windows PowerShell `System.Speech` interface. The same message appears on screen for three seconds.

Console logs show listener state, recognized text (passive and active), RMS values, and queue processing.

## Generative music

`utils/lyria_realtime.py` connects to Google Lyria (model `lyria-realtime-exp`). It needs a valid API key in the `GOOGLE_AI_API_KEY` or `LYRIA_API_KEY` environment variable.

Workflow:

1. The class reads `canvas_state.json` to derive color intensity, brush mode, stroke density, and motion speed.
2. A weighted prompt is built to describe the desired musical mood (instrument groups, dynamics, effects).
3. The prompt is sent over a WebSocket session to the Lyria realtime endpoint.
4. Incoming PCM24 audio chunks are played through PyAudio (mono, 24 kHz, 16-bit). The stream stops gracefully on errors or when `stop()` is called.

Because the audio arrives already mixed from Lyria, the client does not apply additional synthesis that could introduce noise.

## Project structure

```
src/
  main.py               # Application loop and UI
  core/
    config.py           # Constants (window sizes, gesture thresholds, UI layout)
    gesture_detector.py # MediaPipe wrapper and gesture logic
    brushes.py          # Brush definitions and manager
    canvas.py           # Stroke storage and rendering
    feedback.py         # Tracking window overlay
  utils/
    voice_feedback.py   # Text to speech helper
    voice_listener.py   # Wake word and speech recognition thread
    lyria_realtime.py   # Generative music client
    extensions.py       # Miscellaneous helpers
legacy/                # Archived experiments
requirements.txt       # Dependency list
start.bat              # Convenience launcher for Windows
```

## Troubleshooting

| Problem | Hint |
| --- | --- |
| Camera fails to open | Use `--camera N` or adjust backends in `open_camera`; ensure no other app holds the device. |
| Gesture feels jittery | Tweak `LANDMARK_SMOOTHING_ALPHA` and thresholds in `core/config.py`. |
| No voice recognition | Install `sounddevice` and `SpeechRecognition`, check microphone permissions, and confirm RMS logs are above the threshold. |
| TTS unavailable | Install `pyttsx3` and `pypiwin32`, or enable PowerShell `System.Speech`. |
| Music silent | Provide a valid API key and ensure PyAudio is installed; check logs for authentication errors. |

## Roadmap ideas

- Automatic PNG exports at a configurable interval.
- More brush styles (spray, watercolor, neon).
- BPM and dynamics linked to stroke velocity for the music engine.
- Collaborative mode over the network.
- Visual audio meter synchronized with the Lyria stream.

