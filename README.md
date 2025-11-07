# Pintura Interactiva con Gestos - Transgresión Digital# Pintura Interactiva con Gestos - Transgresión Digital



Aplicación de pintura artística controlada por gestos de mano, diseñada para explorar el concepto de transgresión en el arte digital.Aplicación de pintura artística controlada por gestos de mano, diseñada para explorar el concepto de transgresión en el arte digital.



## 🚀 Inicio Rápido## 📁 Estructura del Proyecto



### Windows```

```bashproyecto/

start.bat│

```├── main.py              # 🎨 Aplicación principal

├── config.py            # ⚙️ Configuración global

### Manual├── gesture_detector.py  # 🤚 Detección de gestos con MediaPipe

```bash├── brushes.py           # 🖌️ Sistema de pinceles

# Ejecutar aplicación├── canvas.py            # 🖼️ Lienzo digital

python src/main.py├── feedback.py          # 👁️ Retroalimentación visual

├── utils.py             # 🔧 Utilidades y herramientas

# Verificar sistema├── extensions.py        # ➕ Extensiones y ejemplos

python scripts/demo.py├── test_components.py   # 🧪 Tests unitarios

│

# Ejecutar tests├── README.md            # 📖 Este archivo

python -m pytest tests/ -v├── ARCHITECTURE.md      # 🏗️ Documentación de arquitectura

```├── CONTRIBUTING.md      # 🤝 Guía de contribución

├── requirements.txt     # 📦 Dependencias

## 📦 Instalación│

└── french.py            # 📜 Versión original (legacy)

```bash```

pip install -r requirements.txt

```## ✨ Características



## 📁 Estructura del Proyecto- **Detección de gestos inteligente**: Usa MediaPipe Hands para detección precisa

- **Múltiples pinceles artísticos**: Línea continua y efecto impresionista (dab)

```- **Paleta de colores**: Azul, Verde, Rojo, Amarillo (fácilmente extensible)

proyecto/- **Retroalimentación visual en tiempo real**: Feedback instantáneo del estado del gesto

├── src/                    # Código fuente- **Arquitectura modular y extensible**: Código organizado por responsabilidades

│   ├── core/              # Componentes principales- **Sistema de tests**: Tests unitarios para componentes críticos

│   │   ├── config.py      # Configuración- **Utilidades artísticas**: Filtros, exportación, análisis de trazos

│   │   ├── gesture_detector.py- **Fácil de extender**: Sistema de plugins para nuevos pinceles y gestos

│   │   ├── brushes.py

│   │   ├── canvas.py## 🚀 Instalación

│   │   └── feedback.py

│   ├── utils/             # Utilidades### Requisitos Previos

│   │   ├── utils.py       # Herramientas

│   │   └── extensions.py  # Extensiones- Python 3.8 o superior

│   └── main.py            # Aplicación principal- Webcam funcional

│

├── tests/                 # Tests unitarios### Instalación de Dependencias

│   └── test_components.py

│```bash

├── scripts/               # Scripts auxiliares# Clonar o descargar el proyecto

│   └── demo.py           # Demostracióncd proyecto

│

├── docs/                  # Documentación# Instalar dependencias

│   ├── README.md         # Guía completapip install -r requirements.txt

│   ├── ARCHITECTURE.md   # Arquitectura```

│   ├── CONTRIBUTING.md   # Contribución

│   └── PROJECT_SUMMARY.md### Dependencias Principales

│

├── legacy/                # Código original- `opencv-python`: Procesamiento de imágenes y video

│   └── french.py- `mediapipe`: Detección de gestos de mano

│- `numpy`: Operaciones numéricas

├── requirements.txt       # Dependencias

└── start.bat             # Inicio rápido## 🎮 Uso

```

### Ejecutar la Aplicación

## 🎮 Controles

```bash

### Tecladopython main.py

- `q` - Salir```

- `c` - Borrar lienzo

- `1,2,3,4` - Cambiar color### Controles de Teclado

- `t` - Cambiar tipo de pincel

- `s` - Cambiar tamaño| Tecla | Acción |

|-------|--------|

### Gestos| `q` | Salir del programa |

- **Dibujar**: Dedo índice extendido, demás dedos flexionados| `c` | Borrar todo el lienzo |

| `1` | Seleccionar color AZUL |

## 📚 Documentación| `2` | Seleccionar color VERDE |

| `3` | Seleccionar color ROJO |

Ver documentación completa en [`docs/README.md`](docs/README.md)| `4` | Seleccionar color AMARILLO |

| `t` | Cambiar tipo de pincel |

## 🎨 Concepto Artístico| `s` | Cambiar tamaño de pincel |



Proyecto que explora la **transgresión digital** como forma de expresión artística contemporánea.### Gesto de Dibujo



## 📄 LicenciaPara dibujar:

1. **Extiende SOLO el dedo índice**

Proyecto académico - Universidad PUCP2. Mantén los dedos corazón, anular y meñique **flexionados** hacia la palma

3. El pulgar puede estar en cualquier posición
4. Observa el feedback visual en la ventana 'Tracking' para ajustar tu mano

💡 **Tip**: Ajusta `FLEXIBILITY_THRESHOLD` en `config.py` si el gesto es muy estricto o laxo.

## 🏗️ Arquitectura

### Componentes Principales

1. **`PaintApp`** (main.py)
   - Orquestador principal de la aplicación
   - Gestiona el bucle principal y coordinación de componentes

2. **`GestureDetector`** (gesture_detector.py)
   - Interfaz con MediaPipe Hands
   - Detección de gestos específicos
   - Extracción de posiciones de landmarks

3. **`BrushManager`** (brushes.py)
   - Gestión de tipos y tamaños de pinceles
   - Patrón Strategy para diferentes algoritmos de dibujo
   - Fácil extensión con nuevos pinceles

4. **`Canvas`** (canvas.py)
   - Representa el lienzo digital
   - Almacena trazos por color y segmento
   - Gestiona el estado del dibujo

5. **`GestureFeedback`** (feedback.py)
   - Retroalimentación visual en tiempo real
   - Dibuja landmarks con código de colores
   - Muestra estado de cada dedo

6. **`Utils`** (utils.py)
   - Exportación de imágenes
   - Filtros artísticos
   - Análisis de trazos
   - Grabación de sesiones

### Principios de Diseño

✅ **SOLID Principles**
- Single Responsibility: Cada clase tiene una responsabilidad clara
- Open/Closed: Abierto a extensión, cerrado a modificación
- Liskov Substitution: Subclases intercambiables (ej: Brushes)
- Interface Segregation: Interfaces específicas
- Dependency Inversion: Dependencias inyectadas

✅ **Design Patterns**
- **Strategy**: Sistema de pinceles intercambiables
- **Facade**: PaintApp simplifica la complejidad
- **Template Method**: Brush como clase base abstracta

✅ **Clean Code**
- Nombres descriptivos
- Funciones pequeñas y enfocadas
- Documentación completa
- Type hints cuando es posible

### Flujo de Ejecución

```
1. Captura de frame (Camera)
   ↓
2. Detección de manos (GestureDetector)
   ↓
3. Identificación de gesto (is_drawing_gesture)
   ↓
4. Extracción de posición (get_index_tip_position)
   ↓
5. Añadir punto al canvas (Canvas.add_point)
   ↓
6. Renderizado con pincel (Canvas.render + Brush)
   ↓
7. Feedback visual (GestureFeedback.draw)
   ↓
8. Mostrar en pantalla (cv2.imshow)
   ↓
9. Procesar entrada de teclado
   ↓
10. Repetir
```

Ver [`ARCHITECTURE.md`](ARCHITECTURE.md) para más detalles.

## 🎨 Concepto Artístico

Este proyecto explora la **transgresión digital** como forma de expresión artística contemporánea, donde:

- El gesto físico se transforma en marca virtual
- Se cuestionan los límites entre lo material y lo digital
- El arte no requiere soporte físico para existir
- La transgresión se manifiesta en el mensaje, no solo en el medio

### Marco Conceptual

Basado en la idea de que la transgresión artística en el espacio digital:

1. **No requiere daño físico** para ser disruptiva
2. **Amplifica el mensaje** a través de la viralidad digital
3. **Redefine el concepto de propiedad** en espacios virtuales
4. **Cuestiona narrativas dominantes** sin intervenir materialidad

> "La transgresión se desplaza del acto material y se centra en lo que representa."

### Referentes Teóricos

- **Michel Foucault, Søren Kierkegaard, Georges Bataille**: Transgresión de límites
- **Yuval Noah Harari**: Ficciones compartidas y orden social
- **Arte transgresor contemporáneo**: Provocación y cuestionamiento de normas

Ver documento conceptual completo para más información.

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
python -m unittest test_components.py -v

# Tests específicos
python -m unittest test_components.TestBrushes -v
python -m unittest test_components.TestCanvas -v
```

### Cobertura de Tests

- ✅ Sistema de pinceles (LineBrush, DabBrush, BrushManager)
- ✅ Canvas (inicialización, add_point, clear, cambio de color)
- ✅ Gestión de trazos (break_stroke, render)

## 🔧 Extensibilidad

### Añadir Nuevo Pincel

```python
# 1. Crear clase en extensions.py
class MiPincel(Brush):
    def draw(self, canvas, p1, p2, color):
        # Tu lógica aquí
        pass

# 2. Registrar en brushes.py
self._brushes['MI_PINCEL'] = MiPincel

# 3. Añadir a config.py
BRUSH_TYPES = ["LINEA", "DAB", "MI_PINCEL"]
```

### Añadir Nuevo Gesto

```python
# En gesture_detector.py o extensions.py
@staticmethod
def is_mi_gesto(landmarks):
    # Lógica de detección
    return condicion_cumplida
```

Ver [`CONTRIBUTING.md`](CONTRIBUTING.md) para guía completa de extensión.

## 📚 Utilidades Incluidas

### Filtros Artísticos (utils.py)

```python
from utils import ArtisticFilters

# Aplicar filtros
vintage_img = ArtisticFilters.apply_vintage(image)
neon_img = ArtisticFilters.apply_neon(image)
sketch_img = ArtisticFilters.apply_sketch(image)
cartoon_img = ArtisticFilters.apply_cartoon(image)
```

### Exportación de Imágenes

```python
from utils import ImageExporter

# Guardar imagen
filepath = ImageExporter.save_png(canvas_image)

# Guardar con metadatos
ImageExporter.save_with_metadata(
    canvas_image,
    metadata={
        'artist': 'Tu nombre',
        'session_duration': 300,
        'colors_used': ['AZUL', 'ROJO']
    }
)
```

### Análisis de Trazos

```python
from utils import StrokeAnalyzer

# Obtener estadísticas
stats = StrokeAnalyzer.get_session_stats(canvas.strokes)
print(f"Longitud total: {stats['total_length_px']} px")
print(f"Distribución de colores: {stats['color_distribution']}")
```

## 🚀 Mejoras Futuras

- [ ] Sistema de capas con transparencia
- [ ] Más tipos de pinceles (spray, caligrafía, glitch, neón, acuarela)
- [ ] Gestos adicionales (borrar, deshacer, guardar)
- [ ] Interfaz gráfica con botones virtuales activados por gestos
- [ ] Filtros artísticos en tiempo real
- [ ] Grabación de sesiones en video
- [ ] Exportación a múltiples formatos (SVG, PDF)
- [ ] Modo colaborativo (múltiples manos)
- [ ] Integración con IA para sugerencias artísticas
- [ ] Galería de obras guardadas
- [ ] Sistema de plugins dinámicos

## 📖 Documentación Adicional

- [`ARCHITECTURE.md`](ARCHITECTURE.md) - Arquitectura detallada del sistema
- [`CONTRIBUTING.md`](CONTRIBUTING.md) - Guía para contribuir y extender
- [`extensions.py`](extensions.py) - Ejemplos de pinceles y gestos avanzados
- [`utils.py`](utils.py) - Utilidades y herramientas auxiliares

## 🐛 Resolución de Problemas

### La cámara no se detecta

```python
# En main.py, cambiar el índice de la cámara
self.cap = cv2.VideoCapture(1)  # Probar con 1, 2, etc.
```

### El gesto no se detecta correctamente

```python
# En config.py, ajustar el umbral de flexibilidad
FLEXIBILITY_THRESHOLD = 0.03  # Aumentar para menos estricto
FLEXIBILITY_THRESHOLD = 0.01  # Disminuir para más estricto
```

### Rendimiento bajo

```python
# En config.py, reducir resolución
PAINT_WINDOW_WIDTH = 960
PAINT_WINDOW_HEIGHT = 540
```

## 👥 Autores

Proyecto académico - Universidad PUCP
- Concepto artístico: Transgresión Digital
- Desarrollo: Sistema modular de pintura con gestos

## 📄 Licencia

Proyecto educativo - Arte Digital y Nuevos Medios

---

**¡Happy painting!** 🎨✨

Para preguntas o sugerencias, revisa la documentación en `CONTRIBUTING.md`

## 🎙️ Control por voz — "Lumi"

Se ha añadido soporte opcional de control por voz mediante la palabra clave "Lumi".

- Modo pasivo: el sistema escucha en segundo plano solo para la palabra clave "Lumi".
- Modo activo: al detectar "Lumi" el sistema responde "Te escucho" y escucha 1–5 segundos para captar el comando.
- Comandos soportados (ejemplos):
   - "Lumi" → activación
   - "Color morado" / "Color azul" / "Color rojo" → cambia el color
   - "Modo borrador" / "Borrador" → activa el borrador
   - "Grosor fino/medio/grande" → cambia el tamaño del pincel
   - "Limpiar" → borra el lienzo
   - "Salir" → cierra la aplicación

Confirmación: el sistema reproduce una confirmación hablada (local, mediante pyttsx3) y muestra una notificación visual breve en el lienzo (ej. "Color morado activado").

Dependencias para voz (recomendadas):

```bash
pip install SpeechRecognition pyttsx3
# En Windows, PyAudio suele instalarse mejor con pipwin:
pip install pipwin
pipwin install pyaudio
```

Privacidad: por defecto la librería `SpeechRecognition` usa la API de Google (requiere Internet) para reconocimiento. Si prefieres un flujo totalmente offline podemos migrar a VOSK/PocketSphinx — dímelo y lo integro.

Configuración y notas:
- El módulo de voz es totalmente opcional: si faltan dependencias la aplicación funcionará igual sin voz.
- Puedes ajustar el idioma en `utils/voice_listener.py` pasando otro código (p. ej. `en-US`).
