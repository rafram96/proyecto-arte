# 🎨🎵 Proyecto Arte con Música Generativa

**Pintura con gestos de mano + Música en tiempo real con Lyria AI**

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Incluye:**
- `google-genai` - API de Lyria para música generativa
- `pyaudio` - Reproducción de audio en tiempo real
- `opencv-python`, `mediapipe`, `numpy` - Visión por computadora

**Nota PyAudio en Windows:** Si falla, descarga el wheel desde:  
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

### 2. Ejecutar

```bash
python src/main.py
```

**Lo que verás:**
```
✅ Sesión Lyria RealTime conectada
🔊 PyAudio inicializado para reproducción
🎧 Iniciando recepción de audio...
🎵 Reproducción iniciada - esperando trazos del canvas...
```

### 3. ¡Dibuja!

- Usa tu **dedo índice** para dibujar
- Diferentes **colores** = diferentes **instrumentos**
- Diferentes **pinceles** = diferentes **efectos de audio**

## 🎵 Música Generativa en Tiempo Real

El sistema **Lyria** genera música automáticamente basándose en tus trazos:

| Color | Instrumento | Pincel | Efecto |
|-------|-------------|--------|--------|
| 🔵 AZUL | Piano | LINEA | Reverb |
| 🟢 VERDE | Violín | DAB | Delay |
| 🔴 ROJO | Cello | - | - |
| 🟡 AMARILLO | Flauta | - | - |

### Coordenadas → Música

- **X (horizontal)**: Nota musical (izquierda = grave, derecha = aguda)
- **Y (vertical)**: Duración (arriba = corta, abajo = larga)
- **Tamaño de pincel**: Intensidad del sonido

## 📂 Guardado en Tiempo Real

Mientras dibujas, el estado del canvas se guarda automáticamente en:
```
canvas_state.json
```

Este archivo:
- ✅ Se actualiza en **tiempo real** con cada trazo
- ✅ Incluye coordenadas, colores, pinceles y timestamps
- ✅ Se **elimina automáticamente** al cerrar el programa
- ✅ Es usado por Lyria para generar la música

## 🎮 Controles

### Teclado
- `q` - Salir
- `c` - Borrar canvas
- `1-4` - Cambiar color
- `t` - Cambiar tipo de pincel
- `s` - Cambiar tamaño de pincel

### Gestos de Mano
- **Dedo índice extendido** - Dibujar
- **Pinch (índice + pulgar)** - Seleccionar color/pincel en UI

## 📚 Documentación

- **[GUARDADO_TIEMPO_REAL.md](GUARDADO_TIEMPO_REAL.md)** - Sistema de guardado JSON
- **[LYRIA_SETUP.md](LYRIA_SETUP.md)** - Configuración de música generativa
- **[STRUCTURE.md](STRUCTURE.md)** - Estructura del proyecto

## 🧪 Pruebas

```bash
# Probar guardado en tiempo real
python test_realtime_save.py

# Probar sistema Lyria
python test_lyria.py
```

## 🎼 Ejemplo de Uso

1. **Dibuja con AZUL (Piano)** en la parte derecha → Notas agudas de piano
2. **Cambia a VERDE (Violín)** y dibuja arriba → Notas cortas de violín
3. **Usa pincel DAB** → Añade efecto de delay/eco
4. **Dibuja grande** → Sonido más fuerte (fortissimo)

## 🛠️ Requisitos

- Python 3.8+
- Webcam
- OpenCV
- MediaPipe
- Google AI API (Lyria) - **Ya configurado ✅**

## ⚡ API Key

La API key de Google AI (Lyria) ya está integrada en el código. No necesitas configurar nada.

Si quieres usar tu propia key, edita `src/main.py` línea ~210.

## 🎨 Características

- ✅ Detección de gestos de mano con MediaPipe
- ✅ Múltiples colores y pinceles
- ✅ Guardado automático en tiempo real
- ✅ Música generativa con Lyria AI
- ✅ Mapeo inteligente de coordenadas a parámetros musicales
- ✅ Efectos de audio por tipo de pincel
- ✅ Instrumentos de orquesta por color

## 📝 Formato del JSON

```json
{
  "strokes": [
    {
      "x": 320,
      "y": 400,
      "color": "AZUL",
      "brush_type": "LINEA",
      "brush_size": 5,
      "time": 1731012372.12
    }
  ]
}
```

## 🔥 Características Avanzadas

### Threading Asíncrono
- Monitoreo del canvas en hilo separado
- Generación de audio sin bloquear UI
- Cola de eventos musicales eficiente

### Sistema de Efectos
- Reverb para crear espacialidad
- Delay para ecos y repeticiones
- Dinámicas musicales (pp, mf, f, ff)

### Mapeo MIDI Completo
- 88 notas de piano (A0 - C8)
- Conversión automática de coordenadas a MIDI
- Nombres de notas legibles (C4, G#5, etc.)

## 🎯 Próximas Mejoras

- [ ] Más instrumentos
- [ ] Efectos adicionales (chorus, distortion)
- [ ] Grabación de sesiones completas
- [ ] Exportar audio generado
- [ ] Visualizador de forma de onda
- [ ] Modo colaborativo multi-usuario

---

**Creado con ❤️ usando Google Lyria AI y MediaPipe**
