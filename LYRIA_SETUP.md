# Configuración de Lyria RealTime Audio

## Requisitos

Para que funcione el sistema de música generativa en tiempo real con Lyria, necesitas:

1. **API Key de Google AI Studio**
2. **Librería para reproducción de audio** (pydub + simpleaudio, o pygame)

## Paso 1: API Key

✅ **La API key ya está configurada en el código**, no necesitas hacer nada.

Si quieres usar tu propia API key:

1. Ve a [Google AI Studio](https://ai.google.dev/)
2. Genera tu API key
3. Edita `src/main.py` línea ~210:
   ```python
   api_key = "TU_API_KEY_AQUI"
   ```

O usa una variable de entorno (opcional):
```powershell
$env:GOOGLE_AI_API_KEY = "TU_API_KEY_AQUI"
```

## Paso 2: Instalar Dependencias

### Para reproducción de audio:

**Opción 1: pydub + simpleaudio (Recomendado)**
```bash
pip install pydub simpleaudio
```

También necesitas ffmpeg:
- **Windows**: Descarga de https://ffmpeg.org/ y añade al PATH
- **Linux**: `sudo apt-get install ffmpeg`
- **Mac**: `brew install ffmpeg`

**Opción 2: pygame**
```bash
pip install pygame
```

**Opción 3: sounddevice**
```bash
pip install sounddevice scipy
```

### Dependencias adicionales:
```bash
pip install requests
```

## Paso 3: Ejecutar el Programa

```bash
python src/main.py
```

Si todo está configurado correctamente, verás:
```
🎵 Lyria RealTime Audio inicializado
   Instrumentos disponibles: ['piano', 'violin', 'cello', 'flute', ...]
   Efectos disponibles: ['reverb', 'delay', 'none']
✅ Lyria RealTime iniciado - monitoreando canvas_state.json
🎵 Sistema de música generativa Lyria activado
```

¡Y listo! El sistema comenzará a generar música automáticamente mientras dibujas. 🎵

## Mapeo de Canvas a Música

### Colores → Instrumentos
- 🔵 **AZUL** → Piano
- 🟢 **VERDE** → Violín
- 🔴 **ROJO** → Cello
- 🟡 **AMARILLO** → Flauta
- ⚫ **NEGRO** → Bajo
- ⚪ **BLANCO** → Arpa
- 🟣 **PÚRPURA** → Oboe
- 🟠 **NARANJA** → Trompeta

### Tipos de Pincel → Efectos
- 📏 **LINEA** → Reverb (espacialidad)
- 🎨 **DAB** → Delay (eco/repetición)
- 🧹 **ERASER** → Sin efecto

### Tamaño de Pincel → Dinámica
- **2px** → Pianissimo (pp - muy suave)
- **5px** → Mezzo-forte (mf - medio)
- **8px** → Forte (f - fuerte)
- **10px+** → Fortissimo (ff - muy fuerte)

### Posición → Parámetros Musicales
- **Eje X (horizontal)** → Nota musical (grave ← → aguda)
  - Izquierda: Notas graves
  - Derecha: Notas agudas
  - Rango completo de piano (88 teclas)

- **Eje Y (vertical)** → Duración de la nota
  - Arriba: Notas cortas/staccato (0.1s)
  - Abajo: Notas largas/sostenidas (2.0s)

## Ejemplo de Uso

1. **Dibuja con AZUL (Piano) en la parte baja derecha**
   - Resultado: Piano con notas agudas y largas

2. **Dibuja con ROJO (Cello) usando pincel DAB**
   - Resultado: Cello con efecto de delay/eco

3. **Dibuja con VERDE (Violín) rápido en la parte superior**
   - Resultado: Violín con notas cortas y rápidas

## Troubleshooting

### "⚠️ Lyria deshabilitado: Define GOOGLE_AI_API_KEY"
- No se encontró la API key
- Configura la variable de entorno como se indica arriba

### "❌ API Error: 401 - Unauthorized"
- API key inválida o expirada
- Verifica tu API key en Google AI Studio

### "❌ API Error: 429 - Too Many Requests"
- Has excedido el límite de requests
- Espera unos minutos o actualiza tu plan

### "Error reproduciendo audio"
- No tienes instalada una librería de audio
- Instala pydub o pygame según las instrucciones

### El audio no se reproduce
- Verifica que tu sistema tenga audio habilitado
- Prueba con otra librería de audio
- Revisa el volumen del sistema

## Desactivar Lyria

Si no quieres usar el sistema de música generativa:

1. **No configures la API key** - El programa funcionará normalmente sin música
2. **O comenta la inicialización** en `main.py`:
   ```python
   # self._init_lyria_audio()
   ```

## Características Avanzadas

### Estadísticas en Tiempo Real

Puedes obtener estadísticas del sistema:
```python
if app.lyria_audio:
    stats = app.lyria_audio.get_stats()
    print(stats)
```

Output:
```python
{
    'running': True,
    'processed_strokes': 150,
    'pending_events': 5,
    'instruments': 8,
    'effects': 3
}
```

### Personalizar Instrumentos

Edita `src/utils/lyria_realtime.py`:
```python
COLOR_TO_INSTRUMENT = {
    "AZUL": "guitar",      # Cambiar piano por guitarra
    "VERDE": "saxophone",  # Cambiar violín por saxofón
    # ...
}
```

### Ajustar Frecuencia de Monitoreo

En `lyria_realtime.py`, línea ~110:
```python
time.sleep(0.1)  # Cambiar a 0.05 para más responsive
```

## Performance

- El sistema está optimizado para tiempo real
- Usa threading para no bloquear el UI
- Cola de eventos para procesamiento asíncrono
- Monitoreo cada 100ms del archivo JSON

## Notas Importantes

⚠️ **Costos de API**: La API de Lyria puede tener costos asociados. Revisa la documentación de Google AI.

⚠️ **Latencia**: Hay un pequeño delay entre dibujar y escuchar el audio (debido a la generación en la nube).

⚠️ **Rate Limits**: Google AI tiene límites de requests por minuto. Ajusta la frecuencia si es necesario.

✅ **Offline**: Si no hay API key, el programa funciona normalmente sin música.
