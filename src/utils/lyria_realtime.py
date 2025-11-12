"""
Integración con Google Lyria API para generar música en tiempo real
basada en los trazos del canvas.
"""

import json
import time
import threading
import os
import asyncio
from typing import Dict, List, Optional, Tuple
from collections import deque

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️  google-genai no instalado. Ejecuta: pip install google-genai")

try:
    import sounddevice as sd
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️  sounddevice no instalado (audio no se reproducirá). Ejecuta: pip install sounddevice")


class LyriaRealtimeAudio:
    """
    Genera música en tiempo real usando Google Lyria API basándose
    en los trazos del canvas guardados en JSON.
    """
    
    # Mapeo simple de colores a instrumentos
    """"
    COLOR_TO_INSTRUMENT = {
        "AZUL": "peruvian harp arpeggios",
        "VERDE": "charango strums",
        "ROJO": "viola cantabile",
        "AMARILLO": "peruvian ocarina melody",
        "CYAN": "siku pan flute choir",
        "MAGENTA": "quena flute vibrato",
        "ROSA": "andino violin harmonics",
        "GRIS": "rainstick ambience",
        "TURQUESA": "pan flute glissandos", # zampoña
        "INDIGO": "bombo leguero pulses",
        "DORADO": "huayno brass trumpet",
        "MARRON": "cajon peruano grooves",
        "NEGRO": "piano",
        "BLANCO": "harp harmonics",
        "PURPURA": "cajita metallic hits",
        "NARANJA": "festival brass fanfare"
    }
    """
    COLOR_TO_INSTRUMENT = {
        "AZUL": "electro swing",
        "VERDE": "cajita metallic hits",
        "ROJO": "electric guitar riffs",
        "AMARILLO": "bright marimba polyrhythms with glockenspiel sprinkles",
        "CYAN": "ambient techno arpeggios with sidechained pads",
        "MAGENTA": "dream pop vocal chops floating over soft subs",
        "ROSA": "retro synthwave lead with gated reverb snares",
        "GRIS": "industrial drones and metallic percussive hits",
        "TURQUESA": "liquid drum and bass basslines with shimmering keys",
        "INDIGO": "dupstep",
        "DORADO": "jazzy trumpet melodies with upright bass walking lines",
        "MARRON": "russian techno rock",
        "NEGRO": "chacalon",
        "BLANCO": "peruvian ocarina melody",
        "PURPURA": "glitchy IDM patterns with granular sparks",
        "NARANJA": "piano",
        "LIMA": "hyperpop bubble arps with detuned leads",
        "COBALTO": "post-rock delay guitars and rolling toms",
        "CORAL": "Quiet melancholic piano",
        "PLATA": "andino violin harmonics"
    }
    # """

    # Dinámicas sugeridas por tipo de pincel
    BRUSH_TO_DYNAMIC = {
        "LINEA": {
            "label": "legato phrasing",
            "tempo_shift": -4,
            "temperature": 0.72,
        },
        "DAB": {
            "label": "staccato pulses",
            "tempo_shift": 10,
            "temperature": 0.92,
        },
        "ERASER": {
            "label": "gentle rests",
            "tempo_shift": -12,
            "temperature": 0.6,
        },
    }

    DEFAULT_DYNAMIC = {
        "label": "steady pulse",
        "tempo_shift": 0,
        "temperature": 0.8,
    }

    DYNAMIC_MEMORY_SECONDS = 4.0
    
    def __init__(self, api_key: str, canvas_state_file: str = "canvas_state.json"):
        """
        Inicializa la integración con Lyria.
        
        Args:
            api_key: API key de Google AI Studio
            canvas_state_file: Ruta al archivo JSON del estado del canvas
        """
        self.api_key = api_key
        self.canvas_state_file = canvas_state_file
        
        # Cliente de Google GenAI
        self.client = None
        self.session = None
        self.event_loop = None
        
        if GENAI_AVAILABLE:
            try:
                self.client = genai.Client(
                    api_key=api_key,
                    http_options={'api_version': 'v1alpha'}
                )
            except Exception as e:
                print(f"⚠️  Error inicializando cliente GenAI: {e}")
        
        # Control del hilo de monitoreo
        self.running = False
        self.monitor_thread = None
        self.audio_thread = None
        
        # Último estado procesado
        self.last_processed_count = 0
        self.processed_strokes = set()
        
        # Cola de eventos musicales pendientes
        self.music_queue = deque(maxlen=100)
        
        # Configuración actual de música (simple)
        self.current_instruments = set()  # Instrumentos activos
        self.current_bpm = 140  # BPM más rápido para música andina/dinámica
        self.current_temperature = 0.8  # Más variación
        self.base_bpm = self.current_bpm
        self.global_scale = types.Scale.C_MAJOR_A_MINOR if GENAI_AVAILABLE else None
        self.last_prompt_update = 0  # Control de frecuencia de updates
        self.dynamic_usage: Dict[str, float] = {}
        self.last_config_update = 0.0
        self.canvas_active = False
        self.playback_active = False
        self.target_output_gain = 0.0
        self.output_gain = 0.0
        self.gain_smoothing = 0.12
        
        # Modo simulación
        self.simulation_mode = not GENAI_AVAILABLE or self.client is None
        
        # Motor de audio (se configura dinámicamente con el primer chunk)
        self.audio_available = AUDIO_AVAILABLE
        self.audio_stream: Optional[sd.OutputStream] = None
        self.default_sample_rate = 24000  # Valor por defecto si Lyria no provee info
        self.current_sample_rate: Optional[int] = None
        self.current_channels: Optional[int] = None
        
        if self.audio_available:
            try:
                sd.check_output_settings(
                    samplerate=self.default_sample_rate,
                    channels=1,
                    dtype='int16'
                )
                print("🔊 SoundDevice listo - se configurará con el primer audio recibido")
            except Exception as e:
                print(f"⚠️  Error verificando salida de audio: {e}")
                self.audio_available = False
        
        print("🎵 Lyria RealTime Audio inicializado")
        if self.simulation_mode:
            print(f"   ⚠️  Modo simulación (instala: pip install google-genai)")
        else:
            print(f"   ✅ Cliente GenAI configurado")
        if not self.audio_available:
            print(f"   ⚠️  Sin reproducción de audio (instala: pip install sounddevice)")
        else:
            print(f"   🎧 Esperando primer chunk para configurar la salida de audio")
        print(f"   Instrumentos disponibles: {list(self.COLOR_TO_INSTRUMENT.values())}")
    
    def start(self):
        """Inicia el monitoreo del archivo JSON y la generación de música."""
        if self.running:
            print("⚠️  Lyria ya está ejecutándose")
            return
        
        self.running = True
        
        # Iniciar hilo de monitoreo del archivo
        self.monitor_thread = threading.Thread(target=self._monitor_canvas_state, daemon=True)
        self.monitor_thread.start()
        
        # Iniciar hilo de generación de audio
        self.audio_thread = threading.Thread(target=self._audio_thread_runner, daemon=True)
        self.audio_thread.start()
        
        print("✅ Lyria RealTime iniciado - monitoreando canvas_state.json")
    
    def stop(self):
        """Detiene el monitoreo y generación de música."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        if self.audio_thread:
            self.audio_thread.join(timeout=2)
        
        # Cerrar SoundDevice
        if self.audio_stream:
            try:
                self.audio_stream.stop()
                self.audio_stream.close()
            except:
                pass
        
        print("🛑 Lyria RealTime detenido")
    
    def _monitor_canvas_state(self):
        """Monitorea continuamente el archivo JSON en busca de cambios."""
        while self.running:
            try:
                strokes = []
                if os.path.exists(self.canvas_state_file):
                    with open(self.canvas_state_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    strokes = data.get('strokes', []) or []

                current_count = len(strokes)

                if current_count == 0:
                    if self.last_processed_count != 0 or self.canvas_active:
                        self._handle_canvas_cleared()
                    self.last_processed_count = 0
                    time.sleep(0.1)
                    continue

                if current_count < self.last_processed_count:
                    self._handle_canvas_cleared()
                    self.last_processed_count = 0

                if current_count > self.last_processed_count:
                    new_strokes = strokes[self.last_processed_count:]
                    self._process_new_strokes(new_strokes)
                    self.last_processed_count = current_count
                
            except json.JSONDecodeError:
                # Archivo en proceso de escritura - esperar al siguiente ciclo
                time.sleep(0.05)
                continue
            except FileNotFoundError:
                # Aún no existe el archivo
                self._handle_canvas_cleared()
                self.last_processed_count = 0
            except Exception as e:
                print(f"❌ Error monitoreando canvas: {e}")
            
            time.sleep(0.1)  # Chequear cada 100ms
    
    def _process_new_strokes(self, strokes: List[Dict]):
        """
        Procesa nuevos trazos y los convierte en eventos musicales.
        
        Args:
            strokes: Lista de puntos nuevos del canvas
        """
        for stroke in strokes:
            # Extraer información del trazo
            color = stroke.get('color', 'AZUL')
            brush_type = stroke.get('brush_type', 'LINEA')
            brush_size = stroke.get('brush_size', 5)
            x = stroke.get('x', 0)
            y = stroke.get('y', 0)
            timestamp = stroke.get('time', time.time())
            
            # Convertir a evento musical
            music_event = self._stroke_to_music_event(
                color, brush_type, brush_size, x, y, timestamp
            )
            
            # Añadir a la cola de reproducción
            self.music_queue.append(music_event)

        if strokes and not self.canvas_active:
            self.canvas_active = True
            self.target_output_gain = 1.0

    def _handle_canvas_cleared(self):
        """Reacciona cuando el lienzo queda vacío o no existe."""
        if not self.canvas_active and not self.current_instruments and self.target_output_gain == 0.0:
            return

        self.canvas_active = False
        self.target_output_gain = 0.0
        self.playback_active = False
        self.current_instruments.clear()
        self.dynamic_usage.clear()
        self.music_queue.clear()
        self.last_prompt_update = 0
        self.last_config_update = 0.0

        if self.event_loop and self.event_loop.is_running():
            asyncio.run_coroutine_threadsafe(self._pause_session(), self.event_loop)
    
    def _stroke_to_music_event(self, color: str, brush_type: str, 
                                brush_size: int, x: int, y: int, 
                                timestamp: float) -> Dict:
        """
        Convierte un trazo del canvas en un evento musical.
        
        Args:
            color: Color del trazo
            brush_type: Tipo de pincel
            brush_size: Tamaño del pincel (usado para volumen, no se envía a Lyria)
            x, y: Coordenadas del punto
            timestamp: Momento del trazo
        
        Returns:
            Diccionario con parámetros musicales
        """
        # Solo el instrumento basado en color
        instrument = self.COLOR_TO_INSTRUMENT.get(color, "piano")
        
        return {
            'instrument': instrument,
            'color': color,
            'timestamp': timestamp,
            'brush_type': brush_type
        }
    
    def _audio_thread_runner(self):
        """Ejecuta el loop asyncio en un hilo separado."""
        # Crear un nuevo event loop para este hilo
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        
        try:
            if not self.simulation_mode and GENAI_AVAILABLE:
                # Modo real con API
                self.event_loop.run_until_complete(self._run_lyria_session())
            else:
                # Modo simulación
                self.event_loop.run_until_complete(self._run_simulation_loop())
        except Exception as e:
            print(f"❌ Error en audio thread: {e}")
        finally:
            self.event_loop.close()
    
    async def _run_simulation_loop(self):
        """Loop de simulación (sin API real)."""
        print("💡 Modo simulación activado - eventos se mostrarán en consola")
        
        while self.running:
            try:
                if len(self.music_queue) > 0:
                    event = self.music_queue.popleft()
                    print(f"🎵 {event['instrument']}")
                else:
                    await asyncio.sleep(0.05)
            except Exception as e:
                print(f"❌ Error en simulación: {e}")
                await asyncio.sleep(0.1)
    
    async def _run_lyria_session(self):
        """
        Mantiene una sesión activa con Lyria RealTime API.
        Procesa la cola de eventos y actualiza los prompts en tiempo real.
        """
        try:
            async with (
                self.client.aio.live.music.connect(
                    model='models/lyria-realtime-exp'
                ) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                self.playback_active = False
                self.target_output_gain = 0.0
                self.output_gain = 0.0
                print("✅ Sesión Lyria RealTime conectada")
                
                # Crear tarea para recibir y reproducir audio
                tg.create_task(self._receive_and_play_audio(session))
                
                # Configurar prompts iniciales - Base de música andina
                await session.set_weighted_prompts(
                    prompts=[
                        types.WeightedPrompt(text="orchestra music", weight=1.5),
                    ]
                )
                
                # Configurar generación de música con MÁXIMA calidad
                await session.set_music_generation_config(
                    config=types.LiveMusicGenerationConfig(
                        bpm=self.current_bpm,
                        temperature=self.current_temperature,
                        scale=self.global_scale,  # Escala global (no cambia)
                        music_generation_mode=types.MusicGenerationMode.QUALITY  # QUALITY para mejor audio
                    )
                )
                
                print(f"⚙️  Configuración de calidad aplicada:")
                print(f"   - Modo: QUALITY (máxima calidad de audio)")
                print(f"   - BPM: {self.current_bpm}")
                print(f"   - Temperature: {self.current_temperature}")
                print(f"   - Scale: {self.global_scale}")
                
                print("⏸️  Esperando primeros trazos para iniciar reproducción...")
                
                # Loop principal de procesamiento - MÁS RÁPIDO
                while self.running:
                    if len(self.music_queue) > 0:
                        # Procesar más eventos por ciclo para ser más responsive
                        events_to_process = min(10, len(self.music_queue))
                        for _ in range(events_to_process):
                            if len(self.music_queue) > 0:
                                event = self.music_queue.popleft()
                                await self._process_music_event(session, event)
                    
                    await asyncio.sleep(0.1)  # Pausa corta para ser más dinámico
                        
        except Exception as e:
            print(f"❌ Error en sesión Lyria: {e}")
            import traceback
            traceback.print_exc()
            print(f"   Cambiando a modo simulación...")
            self.simulation_mode = True
            await self._run_simulation_loop()
    
    def _extract_audio_format(self, audio_chunk) -> Tuple[int, int]:
        """Obtiene sample rate y canales desde un chunk de audio."""
        sample_rate: Optional[int] = None
        channels: Optional[int] = None

        for attr_name in ("sample_rate", "sampleRate"):
            value = getattr(audio_chunk, attr_name, None)
            if value is not None:
                try:
                    sample_rate = int(value)
                    break
                except (TypeError, ValueError):
                    sample_rate = None

        for attr_name in ("channels", "num_channels", "numChannels"):
            value = getattr(audio_chunk, attr_name, None)
            if value is not None:
                try:
                    channels = int(value)
                    break
                except (TypeError, ValueError):
                    channels = None

        mime = getattr(audio_chunk, "mime_type", None) or getattr(audio_chunk, "mimeType", None)
        if mime:
            params = mime.split(';')
            for raw_param in params[1:]:
                key, _, value = raw_param.partition('=')
                key = key.strip().lower()
                value = value.strip()
                if not value:
                    continue
                if key == 'rate' and sample_rate is None:
                    try:
                        sample_rate = int(value)
                    except ValueError:
                        pass
                elif key in {'channels', 'ch'} and channels is None:
                    try:
                        channels = int(value)
                    except ValueError:
                        pass

        if not sample_rate or sample_rate <= 0:
            sample_rate = self.default_sample_rate
        if not channels or channels <= 0:
            channels = 1

        return sample_rate, channels

    def _ensure_output_stream(self, sample_rate: int, channels: int):
        """Configura o reconfigura la salida de audio según el chunk recibido."""
        if not self.audio_available:
            return

        if (
            self.audio_stream is not None
            and self.current_sample_rate == sample_rate
            and self.current_channels == channels
        ):
            return

        if self.audio_stream is not None:
            try:
                self.audio_stream.stop()
                self.audio_stream.close()
            except Exception:
                pass

        try:
            self.audio_stream = sd.OutputStream(
                samplerate=sample_rate,
                channels=channels,
                dtype='int16',
                blocksize=max(256, 1024 // max(1, channels)),
                latency='low',
                dither_off=False,
                clip_off=False,
                prime_output_buffers_using_stream_callback=True
            )
            self.audio_stream.start()
            self.current_sample_rate = sample_rate
            self.current_channels = channels
            print(f"🔊 Salida de audio configurada: {sample_rate} Hz | canales: {channels}")
        except Exception as e:
            print(f"⚠️  Error configurando salida de audio ({sample_rate} Hz, {channels} ch): {e}")
            self.audio_stream = None
            self.current_sample_rate = None
            self.current_channels = None

    async def _receive_and_play_audio(self, session):
        """
        Tarea en background que recibe y procesa el audio en streaming con MÁXIMA calidad.
        
        Args:
            session: Sesión activa de Lyria
        """
        try:
            print("🎧 Iniciando recepción de audio en streaming...")
            audio_chunk_count = 0
            total_bytes_received = 0
            
            async for message in session.receive():
                if not self.running:
                    break
                
                # Extraer chunks de audio del mensaje
                if hasattr(message, 'server_content') and hasattr(message.server_content, 'audio_chunks'):
                    for audio_chunk in message.server_content.audio_chunks:
                        audio_data = audio_chunk.data
                        
                        if audio_data and len(audio_data) > 0:
                            sample_rate, channels = self._extract_audio_format(audio_chunk)
                            self._ensure_output_stream(sample_rate, channels)

                            audio_chunk_count += 1
                            total_bytes_received += len(audio_data)
                            
                            # Reproducir el audio con procesamiento de alta calidad
                            await self._play_audio_async(audio_data)
                            
                            # Log cada 50 chunks para no saturar consola
                            if audio_chunk_count % 50 == 0:
                                kb_received = total_bytes_received / 1024
                                print(f"🔊 Stream activo: {audio_chunk_count} chunks | {kb_received:.1f} KB recibidos")
                
                # Sin pausa - máxima velocidad de procesamiento
                await asyncio.sleep(0)
                
        except Exception as e:
            print(f"❌ Error recibiendo audio: {e}")
            import traceback
            traceback.print_exc()
    
    async def _process_music_event(self, session, event: Dict):
        """
        Procesa un evento musical y actualiza los prompts de Lyria.
        
        Args:
            session: Sesión activa de Lyria
            event: Evento musical con parámetros
        """
        try:
            instrument = event['instrument']
            brush_type = event.get('brush_type', 'LINEA')
            now = time.time()

            await self._ensure_session_playing(session)
            self.target_output_gain = max(self.target_output_gain, 1.0)
            self.canvas_active = True

            # Agregar instrumento al set de activos
            self.current_instruments.add(instrument)

            # Registrar dinámica asociada al tipo de pincel
            dynamic_info = self.BRUSH_TO_DYNAMIC.get(brush_type, self.DEFAULT_DYNAMIC)
            dynamic_label = dynamic_info.get('label')
            if dynamic_label:
                self.dynamic_usage[dynamic_label] = now

            # Eliminar dinámicas antiguas para mantener el contexto fresco
            self._prune_stale_dynamics(now)

            # Ajustar configuración global si la dinámica lo requiere
            await self._apply_dynamic_config(session, dynamic_info, now)

            # Actualizar prompts cada 1 segundo para ser más dinámico
            if now - self.last_prompt_update < 1.0:
                return

            self.last_prompt_update = now

            # Crear prompts con instrumentos activos y dinámicas recientes
            prompts = [types.WeightedPrompt(text=inst, weight=1.0)
                       for inst in self.current_instruments]

            active_dynamics = list(self.dynamic_usage.keys())
            for label in active_dynamics:
                prompts.append(types.WeightedPrompt(text=label, weight=0.4))

            if prompts:
                await session.set_weighted_prompts(prompts=prompts)
                if active_dynamics:
                    print(f"🎵 Activos: {', '.join(self.current_instruments)} | Dinámicas: {', '.join(active_dynamics)}")
                else:
                    print(f"🎵 Activos: {', '.join(self.current_instruments)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _ensure_session_playing(self, session):
        """Garantiza que la sesión esté reproduciendo música."""
        if self.playback_active:
            return
        if not hasattr(session, 'play'):
            return
        try:
            await session.play()
            self.playback_active = True
            if not self.canvas_active:
                self.canvas_active = True
            self.target_output_gain = max(self.target_output_gain, 1.0)
        except Exception as e:
            print(f"⚠️  No se pudo iniciar la reproducción: {e}")

    async def _pause_session(self):
        """Pausa la sesión si es posible."""
        if not self.session:
            return

        pause_coro = None
        if hasattr(self.session, 'pause'):
            pause_coro = getattr(self.session, 'pause')
        elif hasattr(self.session, 'stop'):
            pause_coro = getattr(self.session, 'stop')

        if pause_coro is None:
            self.playback_active = False
            return

        try:
            await pause_coro()
        except Exception as e:
            print(f"⚠️  No se pudo pausar la sesión: {e}")
        finally:
            self.playback_active = False

    async def _apply_dynamic_config(self, session, dynamic_info: Dict, current_time: float):
        """Suaviza cambios de tempo/temperatura según la dinámica seleccionada."""
        if not GENAI_AVAILABLE:
            return

        if current_time - self.last_config_update < 0.4:
            return

        tempo_shift = dynamic_info.get('tempo_shift', 0)
        target_bpm = self._clamp(self.base_bpm + tempo_shift, 90, 180)
        target_temperature = dynamic_info.get('temperature', self.current_temperature)

        new_bpm = self._smooth_value(self.current_bpm, target_bpm, factor=0.5)
        new_temperature = self._smooth_value(self.current_temperature, target_temperature, factor=0.35)
        new_temperature = self._clamp(new_temperature, 0.1, 1.2)

        if (
            abs(new_bpm - self.current_bpm) < 0.05
            and abs(new_temperature - self.current_temperature) < 0.01
        ):
            return

        self.current_bpm = new_bpm
        self.current_temperature = new_temperature

        await session.set_music_generation_config(
            config=types.LiveMusicGenerationConfig(
                bpm=int(round(self.current_bpm)),
                temperature=self.current_temperature,
                scale=self.global_scale,
                music_generation_mode=types.MusicGenerationMode.QUALITY
            )
        )
        self.last_config_update = current_time

    def _prune_stale_dynamics(self, current_time: float):
        """Elimina dinámicas que no se han usado recientemente."""
        stale_labels = [
            label for label, seen_at in self.dynamic_usage.items()
            if current_time - seen_at > self.DYNAMIC_MEMORY_SECONDS
        ]
        for label in stale_labels:
            self.dynamic_usage.pop(label, None)

    @staticmethod
    def _smooth_value(current: float, target: float, factor: float = 0.5) -> float:
        """Interpolación lineal simple entre valores actuales y objetivo."""
        factor = max(0.0, min(1.0, factor))
        return current + (target - current) * factor

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        """Limita un valor dentro de un rango específico."""
        return max(minimum, min(maximum, value))

    async def _play_audio_async(self, audio_data: bytes):
        """
        Reproduce audio con MÁXIMA calidad - Procesamiento profesional.
        
        Args:
            audio_data: Datos de audio en formato PCM 16-bit desde Lyria
        """
        if not self.audio_available or self.audio_stream is None:
            return

        try:
            # 1. Convertir bytes a numpy array int16
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            if len(audio_array) == 0:
                return

            channels = self.current_channels or 1
            total_samples = len(audio_array)
            frames = total_samples // channels

            if frames == 0:
                return

            trimmed_samples = frames * channels
            if trimmed_samples != total_samples:
                audio_array = audio_array[:trimmed_samples]

            # 2. Convertir a float32 y reordenar a (frames, channels)
            audio_float = audio_array.astype(np.float32).reshape(frames, channels)

            # 3. Normalizar a rango [-1.0, 1.0] para evitar distorsión
            max_val = 32768.0
            audio_normalized = audio_float / max_val

            # 4. Aplicar soft clipping para evitar distorsión (limiter suave)
            audio_normalized = np.tanh(audio_normalized * 0.95) * 0.95

            # 5. Aplicar fade in/out muy corto para evitar clicks
            fade_samples = min(32, audio_normalized.shape[0] // 4)
            if fade_samples > 0:
                fade_curve = np.linspace(0.0, 1.0, fade_samples).reshape(-1, 1)
                audio_normalized[:fade_samples] *= fade_curve
                audio_normalized[-fade_samples:] *= fade_curve[::-1]

            # 6. Aplicar ganancia de salida progresiva
            self.output_gain = self._smooth_value(self.output_gain, self.target_output_gain, self.gain_smoothing)
            applied_gain = self.output_gain
            if applied_gain <= 1e-4 and self.target_output_gain == 0.0:
                applied_gain = 0.0
                self.output_gain = 0.0

            audio_normalized *= applied_gain

            # 7. Convertir de vuelta a int16
            audio_processed = np.ascontiguousarray((audio_normalized * max_val).astype(np.int16))

            # 8. Escribir al stream con thread pool (non-blocking)
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._write_audio_to_stream,
                audio_processed
            )

        except Exception as e:
            print(f"❌ Error reproduciendo audio: {e}")
            import traceback
            traceback.print_exc()
    
    def _write_audio_to_stream(self, audio_data: np.ndarray):
        """
        Escribe audio al stream de forma segura con manejo de errores.
        
        Args:
            audio_data: Array numpy con datos de audio procesados
        """
        try:
            self.audio_stream.write(audio_data)
        except sd.PortAudioError as e:
            if 'Output underflowed' not in str(e):
                print(f"⚠️  Error en stream de audio: {e}")
    
    def get_stats(self) -> Dict:
        """Retorna estadísticas del sistema de audio en tiempo real."""
        return {
            'running': self.running,
            'processed_strokes': self.last_processed_count,
            'pending_events': len(self.music_queue),
            'active_instruments': list(self.current_instruments),
            'total_instruments': len(self.COLOR_TO_INSTRUMENT)
        }
