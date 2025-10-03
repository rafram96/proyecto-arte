# Pintura Interactiva con Gestos - Transgresión Digital

Aplicación de pintura artística controlada por gestos de mano, diseñada para explorar el concepto de transgresión en el arte digital.

## 📁 Estructura del Proyecto

```
proyecto/
│
├── main.py              # 🎨 Aplicación principal
├── config.py            # ⚙️ Configuración global
├── gesture_detector.py  # 🤚 Detección de gestos con MediaPipe
├── brushes.py           # 🖌️ Sistema de pinceles
├── canvas.py            # 🖼️ Lienzo digital
├── feedback.py          # 👁️ Retroalimentación visual
├── utils.py             # 🔧 Utilidades y herramientas
├── extensions.py        # ➕ Extensiones y ejemplos
├── test_components.py   # 🧪 Tests unitarios
│
├── README.md            # 📖 Este archivo
├── ARCHITECTURE.md      # 🏗️ Documentación de arquitectura
├── CONTRIBUTING.md      # 🤝 Guía de contribución
├── requirements.txt     # 📦 Dependencias
│
└── french.py            # 📜 Versión original (legacy)
```

## ✨ Características

- **Detección de gestos inteligente**: Usa MediaPipe Hands para detección precisa
- **Múltiples pinceles artísticos**: Línea continua y efecto impresionista (dab)
- **Paleta de colores**: Azul, Verde, Rojo, Amarillo (fácilmente extensible)
- **Retroalimentación visual en tiempo real**: Feedback instantáneo del estado del gesto
- **Arquitectura modular y extensible**: Código organizado por responsabilidades
- **Sistema de tests**: Tests unitarios para componentes críticos
- **Utilidades artísticas**: Filtros, exportación, análisis de trazos
- **Fácil de extender**: Sistema de plugins para nuevos pinceles y gestos

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- Webcam funcional

### Instalación de Dependencias

```bash
# Clonar o descargar el proyecto
cd proyecto

# Instalar dependencias
pip install -r requirements.txt
```

### Dependencias Principales

- `opencv-python`: Procesamiento de imágenes y video
- `mediapipe`: Detección de gestos de mano
- `numpy`: Operaciones numéricas

## 🎮 Uso

### Ejecutar la Aplicación

```bash
python main.py
```

### Controles de Teclado

| Tecla | Acción |
|-------|--------|
| `q` | Salir del programa |
| `c` | Borrar todo el lienzo |
| `1` | Seleccionar color AZUL |
| `2` | Seleccionar color VERDE |
| `3` | Seleccionar color ROJO |
| `4` | Seleccionar color AMARILLO |
| `t` | Cambiar tipo de pincel |
| `s` | Cambiar tamaño de pincel |

### Gesto de Dibujo

Para dibujar:
1. **Extiende SOLO el dedo índice**
2. Mantén los dedos corazón, anular y meñique **flexionados** hacia la palma
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
