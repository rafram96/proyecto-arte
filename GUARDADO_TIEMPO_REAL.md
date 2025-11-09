# Guardado Automático en Tiempo Real

## Descripción

El canvas ahora guarda automáticamente su estado en un archivo JSON **en tiempo real** mientras dibujas. El archivo se actualiza continuamente y se elimina automáticamente cuando cierras el programa.

## Características

✅ **Guardado en tiempo real**: El archivo se actualiza cada vez que añades un punto  
✅ **Sin fechas**: Solo incluye timestamps numéricos (time.time())  
✅ **Incluye tipo de pincel**: Cada punto tiene información del brush_type y brush_size  
✅ **Auto-eliminación**: El archivo se borra automáticamente al cerrar el programa  
✅ **Sin intervención manual**: Todo es automático, no necesitas presionar ninguna tecla  

## Formato del Archivo JSON

El archivo `canvas_state.json` se crea automáticamente con este formato:

```json
{
  "strokes": [
    {
      "x": 20,
      "y": 40,
      "color": "ROJO",
      "brush_type": "LINEA",
      "brush_size": 5,
      "time": 1731012372.12
    },
    {
      "x": 22,
      "y": 41,
      "color": "AMARILLO",
      "brush_type": "DAB",
      "brush_size": 10,
      "time": 1731012372.14
    }
  ]
}
```

## Campos Incluidos

- **x, y**: Coordenadas del punto en píxeles
- **color**: Nombre del color ("AZUL", "VERDE", "ROJO", "AMARILLO")
- **brush_type**: Tipo de pincel ("LINEA", "DAB", "ERASER")
- **brush_size**: Tamaño del pincel en píxeles (ej: 2, 5, 10)
- **time**: Timestamp Unix (número decimal, ej: 1731012372.12)

## Comportamiento

### Al Iniciar el Programa
1. Se crea el archivo `canvas_state.json` vacío
2. El archivo se guarda en el mismo directorio donde ejecutas el programa

### Durante el Dibujo
1. **Cada vez que añades un punto**, el archivo se actualiza automáticamente
2. Puedes abrir el archivo en cualquier momento para ver el estado actual
3. No afecta el rendimiento del programa

### Al Cerrar el Programa
1. El archivo `canvas_state.json` se **elimina automáticamente**
2. No quedan rastros del archivo después de cerrar

## Cuándo se Actualiza el Archivo

El archivo se guarda automáticamente en estos momentos:

- ✏️ Al añadir cada punto (`add_point()`)
- 🛑 Al finalizar un trazo (`end_stroke()`)
- 🗑️ Al limpiar el canvas (`clear()`)
- 🎨 Al iniciar el programa

## Uso Externo del Archivo

Mientras el programa está **ejecutándose**, puedes:

- Leer el archivo `canvas_state.json` desde otro programa
- Procesar los datos en tiempo real
- Crear visualizaciones o análisis en vivo
- Guardar snapshots del estado actual

### Ejemplo de Lectura Externa (Python)

```python
import json
import time

# Leer el estado actual mientras el programa está ejecutándose
with open('canvas_state.json', 'r') as f:
    data = json.load(f)

print(f"Total de puntos: {len(data['strokes'])}")

for point in data['strokes']:
    print(f"Punto en ({point['x']}, {point['y']}) - "
          f"Color: {point['color']}, "
          f"Pincel: {point['brush_type']}")
```

## Modificaciones Realizadas

### `src/core/canvas.py`

**Nuevos imports:**
```python
import json
import time
import os
```

**Constructor modificado:**
```python
def __init__(self, width, height, colors, auto_save_file="canvas_state.json"):
    # ... código existente ...
    self.auto_save_file = auto_save_file
    self._save_to_file()  # Crear archivo vacío al iniciar
```

**Nuevos métodos:**

- `_save_to_file()`: Guarda el estado actual en JSON
- `delete_save_file()`: Elimina el archivo al cerrar

**Métodos modificados:**

- `add_point()`: Añadido `self._save_to_file()` al final
- `end_stroke()`: Añadido `self._save_to_file()` al final
- `clear()`: Añadido `self._save_to_file()` al final

### `src/main.py`

**Método modificado:**
```python
def cleanup(self):
    # Eliminar archivo de guardado automático
    self.canvas.delete_save_file()
    # ... resto del código ...
```

## Prueba

Ejecuta el script de prueba para ver cómo funciona:

```bash
python test_realtime_save.py
```

Este script:
1. Crea un canvas
2. Dibuja varios trazos simulados
3. Muestra el contenido del JSON después de cada trazo
4. Elimina el archivo al finalizar

## Notas Importantes

⚠️ **Rendimiento**: Guardar en cada punto puede ser intensivo. Si notas lag, puedes:
- Reducir la frecuencia de guardado (ej: cada 10 puntos)
- Guardar solo al finalizar cada trazo (quitar guardado de `add_point()`)

⚠️ **Archivo único**: Solo existe un archivo `canvas_state.json` a la vez

⚠️ **No persiste**: El archivo se elimina al cerrar, si necesitas guardarlo debes copiarlo mientras el programa está corriendo

## Personalización

Si quieres cambiar el nombre del archivo, modifica la creación del canvas en `main.py`:

```python
self.canvas = Canvas(PAINT_WINDOW_WIDTH, PAINT_WINDOW_HEIGHT, COLORS, 
                     auto_save_file="mi_archivo_personalizado.json")
```

## Ejemplo de Uso en la Aplicación Real

1. Inicia el programa: `python src/main.py`
2. Comienza a dibujar con gestos de mano
3. Abre `canvas_state.json` en tu editor favorito
4. Observa cómo se actualiza en tiempo real
5. Cierra el programa → el archivo desaparece automáticamente
