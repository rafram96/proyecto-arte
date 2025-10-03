# Guía de Contribución y Extensión

## 🎨 Cómo Añadir Nuevos Pinceles

### Paso 1: Crear la Clase del Pincel

Crea una nueva clase que herede de `Brush` en `extensions.py` o crea tu propio archivo:

```python
from brushes import Brush
import cv2

class MiNuevoPincel(Brush):
    """Descripción de tu pincel."""
    
    def draw(self, canvas, p1, p2, color):
        if p1 is None or p2 is None:
            return
        
        # Tu lógica de dibujo aquí
        cv2.line(canvas, p1, p2, color, self.size)
```

### Paso 2: Registrar el Pincel

En `brushes.py`, añade tu pincel al diccionario `_brushes` de `BrushManager`:

```python
self._brushes = {
    'LINEA': LineBrush,
    'DAB': DabBrush,
    'MI_PINCEL': MiNuevoPincel,  # ← Añadir aquí
}
```

### Paso 3: Añadir a la Configuración

En `config.py`, añade el nombre a `BRUSH_TYPES`:

```python
BRUSH_TYPES = ["LINEA", "DAB", "MI_PINCEL"]
```

¡Listo! Tu nuevo pincel estará disponible presionando 't'.

---

## 🤚 Cómo Añadir Nuevos Gestos

### Paso 1: Crear la Función de Detección

En `gesture_detector.py` o `extensions.py`, añade un método estático:

```python
@staticmethod
def is_mi_gesto(landmarks):
    """
    Detecta mi gesto personalizado.
    
    Args:
        landmarks: Landmarks de MediaPipe
        
    Returns:
        bool: True si se detecta el gesto
    """
    mp_hands = mp.solutions.hands
    
    # Tu lógica de detección aquí
    # Ejemplo: verificar posición de dedos
    
    return condicion_cumplida
```

### Paso 2: Integrar en el Flujo Principal

En `main.py`, dentro del método `process_frame`, añade la detección:

```python
if self.gesture_detector.is_mi_gesto(landmarks):
    # Acción al detectar el gesto
    self.canvas.clear()  # Ejemplo
    print("¡Gesto detectado!")
```

---

## 🎭 Cómo Añadir Nuevos Colores

### En `config.py`:

```python
COLORS = {
    'AZUL': (255, 0, 0),
    'VERDE': (0, 255, 0),
    'ROJO': (0, 0, 255),
    'AMARILLO': (0, 255, 255),
    'MORADO': (255, 0, 255),  # ← Nuevo color
}

COLOR_NAMES = ["AZUL", "VERDE", "ROJO", "AMARILLO", "MORADO"]
```

### En `main.py`, añade el control de teclado:

```python
elif key == ord("5"):  # Nuevo número
    color = self.canvas.set_color(4)  # Índice del nuevo color
    print(f"Color seleccionado: {color}")
```

---

## 📊 Cómo Añadir Exportación de Imágenes

### Paso 1: Crear Método en Canvas

En `canvas.py`:

```python
import datetime

def save_to_file(self, filename=None):
    """Guarda el canvas actual a un archivo."""
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"artwork_{timestamp}.png"
    
    cv2.imwrite(filename, self.image)
    return filename
```

### Paso 2: Añadir Control en Main

En `main.py`, método `process_keyboard_input`:

```python
elif key == ord("g"):  # G de "Guardar"
    filename = self.canvas.save_to_file()
    print(f"Imagen guardada: {filename}")
```

---

## 🎬 Cómo Añadir Sistema de Capas

### Paso 1: Modificar Canvas

En `canvas.py`, añade una lista de capas:

```python
class Canvas:
    def __init__(self, width, height, colors):
        # ... código existente ...
        self.layers = [self.image.copy()]
        self.current_layer = 0
    
    def add_layer(self):
        """Añade una nueva capa."""
        new_layer = np.zeros((self.height, self.width, 3), dtype=np.uint8) + 255
        self.layers.append(new_layer)
        self.current_layer = len(self.layers) - 1
    
    def composite_layers(self, alpha=0.7):
        """Combina todas las capas."""
        result = self.layers[0].copy()
        for i in range(1, len(self.layers)):
            result = cv2.addWeighted(result, 1, self.layers[i], alpha, 0)
        return result
```

---

## 🧪 Cómo Añadir Tests

### En `test_components.py`:

```python
class TestMiNuevoComponente(unittest.TestCase):
    def test_mi_funcionalidad(self):
        """Descripción del test."""
        # Preparar
        componente = MiComponente()
        
        # Ejecutar
        resultado = componente.hacer_algo()
        
        # Verificar
        self.assertEqual(resultado, esperado)
```

Ejecuta los tests:

```bash
python -m unittest test_components.py -v
```

---

## 📝 Mejores Prácticas

### 1. Documentación
- Siempre documenta tus clases y métodos con docstrings
- Usa type hints cuando sea posible
- Comenta código complejo

### 2. Naming Conventions
- Clases: `PascalCase`
- Funciones/métodos: `snake_case`
- Constantes: `UPPER_CASE`
- Variables: `snake_case`

### 3. Principios SOLID
- **S**ingle Responsibility: Una clase, una responsabilidad
- **O**pen/Closed: Abierto a extensión, cerrado a modificación
- **L**iskov Substitution: Las subclases deben ser intercambiables
- **I**nterface Segregation: Interfaces específicas mejor que generales
- **D**ependency Inversion: Depender de abstracciones, no de concreciones

### 4. Testing
- Escribe tests para nuevas funcionalidades
- Asegúrate de que todos los tests pasen antes de commit
- Aim para >80% code coverage

---

## 🐛 Debugging

### Ver valores de landmarks:

```python
def debug_landmarks(landmarks):
    for idx, landmark in enumerate(landmarks):
        print(f"Landmark {idx}: x={landmark.x:.3f}, y={landmark.y:.3f}, z={landmark.z:.3f}")
```

### Ver estado del canvas:

```python
def debug_canvas(canvas):
    for color_name in canvas.color_names:
        stroke_count = len(canvas.strokes[color_name])
        print(f"{color_name}: {stroke_count} strokes")
```

---

## 🔧 Configuración Recomendada

### VSCode settings.json:

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.unittestEnabled": true
}
```

---

## 📚 Recursos Adicionales

- [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html)
- [OpenCV Documentation](https://docs.opencv.org/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

## 💡 Ideas para Futuras Extensiones

- [ ] Sistema de deshacer/rehacer (Undo/Redo)
- [ ] Paleta de colores personalizable
- [ ] Filtros artísticos (sepia, vintage, neón)
- [ ] Grabación de sesiones en video
- [ ] Modo colaborativo (múltiples manos)
- [ ] Reconocimiento de formas (círculos, cuadrados)
- [ ] Interfaz gráfica con botones virtuales
- [ ] Exportar a diferentes formatos (SVG, PDF)
- [ ] Sistema de plugins dinámicos
- [ ] Integración con IA para autocompletar dibujos

---

## 🤝 ¿Preguntas?

Si tienes dudas sobre cómo extender el sistema, revisa:
1. El código en `extensions.py` con ejemplos completos
2. La arquitectura en `ARCHITECTURE.md`
3. Los tests en `test_components.py`

¡Happy coding! 🎨✨
