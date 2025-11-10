# 🎵 Actualización: Sistema de Audio en Tiempo Real

## Mejoras Implementadas

### 1. **Reproducción de Audio Real**
- ✅ Integrado **PyAudio** para reproducción en tiempo real
- ✅ Stream de audio configurado: 24kHz, 16-bit, mono
- ✅ Audio chunks se reproducen automáticamente desde Lyria API

### 2. **Prompts Ponderados Mejorados**
Ahora usamos el formato mixto recomendado por Google:
```python
prompts = [
    {"text": "piano", "weight": 2.0},      # Formato dict
    types.WeightedPrompt(text="orchestral", weight=0.5),  # Formato tipo
    types.WeightedPrompt(text="reverb", weight=1.0)
]
```

### 3. **Configuración Musical Avanzada**
```python
await session.set_music_generation_config(
    config=types.LiveMusicGenerationConfig(
        bpm=120,
        temperature=0.8,
        scale=types.Scale.C_MAJOR_A_MINOR,  # ✨ NUEVO
        music_generation_mode=types.MusicGenerationMode.QUALITY  # ✨ NUEVO
    )
)
```

### 4. **Escala Musical Global**
Lyria usa una escala musical fija para toda la sesión:
- � **Escala Global:** C Major / A Minor

Esto mantiene la coherencia armónica entre todos los instrumentos. La escala se configura una sola vez al inicio y no cambia durante la sesión.

### 5. **Recepción de Audio en Background**
```python
async with asyncio.TaskGroup() as tg:
    # Tarea paralela para recibir audio
    tg.create_task(self._receive_and_play_audio(session))
```
El audio se recibe y reproduce en una tarea separada sin bloquear la actualización de prompts.

### 6. **Mejor Manejo de Errores**
- ✅ Traceback completo en errores
- ✅ Fallback automático a modo simulación
- ✅ Mensajes de debug cada 10 chunks de audio

---

## Instalación

### 1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

Esto instalará:
- `google-genai>=0.2.0` (API de Lyria)
- `pyaudio>=0.2.11` (Reproducción de audio)

### 2. Si PyAudio falla en Windows:
Descargar wheel desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Ejemplo:
```bash
pip install PyAudio-0.2.11-cp310-cp310-win_amd64.whl
```

---

## Cómo Funciona Ahora

### Flujo de Audio:
1. **Dibujas en el canvas** → Se guarda en `canvas_state.json`
2. **Lyria lee el trazo** → Extrae color, pincel, coordenadas
3. **Actualiza prompts** → Instrumento + efecto + dinámica + escala
4. **Lyria genera audio** → Stream continuo de chunks PCM
5. **PyAudio reproduce** → Audio sale por los parlantes en tiempo real

### Ejemplo de Log:
```
✅ Sesión Lyria RealTime conectada
🎧 Iniciando recepción de audio...
🎵 Reproducción iniciada - esperando trazos del canvas...
🎵 [piano   ] C4   | reverb | mezzo-forte  | 0.5s
🔊 Reproduciendo audio... (chunks: 10)
🔊 Reproduciendo audio... (chunks: 20)
🎵 [violin  ] E5   | delay  | forte        | 0.3s
```

---

## Configuración Avanzada

### Cambiar BPM dinámicamente:
```python
# En lyria_realtime.py línea ~100
self.current_bpm = 120  # Cambiar a 140, 90, etc.
```

### Cambiar temperatura (creatividad):
```python
self.current_temperature = 0.8  # 0.0 = predecible, 1.0 = creativo
```

### Cambiar escala global:
```python
# En lyria_realtime.py línea ~103
self.global_scale = types.Scale.C_MAJOR_A_MINOR  # Cambiar aquí
```

Escalas disponibles en Lyria:
- `C_MAJOR_A_MINOR` (por defecto)
- `D_MAJOR_B_MINOR`
- `E_MAJOR_CS_MINOR`
- `F_MAJOR_D_MINOR`
- `G_MAJOR_E_MINOR`
- `A_MAJOR_FS_MINOR`
- `BF_MAJOR_G_MINOR`
- `EF_MAJOR_C_MINOR`

**Nota:** Lyria mantiene una sola escala por sesión para coherencia armónica.

---

## Solución de Problemas

### ❌ No suena nada:
1. Verifica que PyAudio esté instalado: `pip list | grep pyaudio`
2. Revisa la consola: ¿Dice "✅ Audio stream listo"?
3. Verifica que tu API key tenga acceso a Lyria
4. Chequea el volumen del sistema

### ❌ Error 404 en Lyria:
- Tu API key necesita acceso al modelo `lyria-realtime-exp`
- Solicita acceso en: https://ai.google.dev/

### ❌ PyAudio no se instala:
- **Windows**: Descargar wheel precompilado
- **Linux**: `sudo apt-get install portaudio19-dev python3-pyaudio`
- **Mac**: `brew install portaudio && pip install pyaudio`

---

## Próximas Mejoras

- [ ] Control de volumen por intensidad de trazo
- [ ] BPM dinámico basado en velocidad de dibujo
- [ ] Grabar sesión a archivo WAV/MP3
- [ ] Visualizador de espectro en tiempo real
- [ ] Modo "colaborativo" (múltiples usuarios)

---

## Ejemplo de Uso

```python
# En main.py ya está integrado, solo ejecuta:
python src/main.py

# El audio empezará automáticamente cuando dibujes
# Cada color = instrumento diferente
# Cada trazo = nota musical
# ¡Disfruta tu orquesta interactiva! 🎨🎵
```

---

**Fecha:** 2025-11-09  
**Versión:** 2.0  
**Estado:** ✅ Producción  
