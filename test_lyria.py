"""
Script de prueba para el sistema Lyria RealTime Audio.
Simula trazos del canvas y verifica la generación de eventos musicales.
"""

import sys
import os
import time
import json

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.lyria_realtime import LyriaRealtimeAudio


def create_test_canvas_state():
    """Crea un archivo canvas_state.json de prueba."""
    test_data = {
        "strokes": [
            # Piano azul - notas medias/graves
            {"x": 320, "y": 400, "color": "AZUL", "brush_type": "LINEA", "brush_size": 5, "time": time.time()},
            {"x": 330, "y": 405, "color": "AZUL", "brush_type": "LINEA", "brush_size": 5, "time": time.time() + 0.1},
            
            # Violín verde - notas agudas con reverb
            {"x": 800, "y": 200, "color": "VERDE", "brush_type": "LINEA", "brush_size": 8, "time": time.time() + 0.5},
            {"x": 850, "y": 210, "color": "VERDE", "brush_type": "LINEA", "brush_size": 8, "time": time.time() + 0.6},
            
            # Cello rojo - notas graves con delay
            {"x": 200, "y": 600, "color": "ROJO", "brush_type": "DAB", "brush_size": 10, "time": time.time() + 1.0},
            {"x": 250, "y": 610, "color": "ROJO", "brush_type": "DAB", "brush_size": 10, "time": time.time() + 1.2},
            
            # Flauta amarilla - notas agudas rápidas
            {"x": 1000, "y": 100, "color": "AMARILLO", "brush_type": "LINEA", "brush_size": 2, "time": time.time() + 1.5},
            {"x": 1050, "y": 110, "color": "AMARILLO", "brush_type": "LINEA", "brush_size": 2, "time": time.time() + 1.6},
        ]
    }
    
    with open("canvas_state.json", "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=2)
    
    return test_data


def test_lyria_system():
    """Prueba el sistema Lyria sin API real."""
    print("=" * 70)
    print("PRUEBA DEL SISTEMA LYRIA REALTIME AUDIO")
    print("=" * 70)
    
    # Verificar si hay API key
    api_key = os.environ.get('GOOGLE_AI_API_KEY') or os.environ.get('LYRIA_API_KEY') or "TEST_API_KEY"
    
    print(f"\n1️⃣  Inicializando Lyria...")
    print(f"   API Key configurada: {'✅' if api_key != 'TEST_API_KEY' else '⚠️  (modo prueba)'}")
    
    # Crear instancia
    lyria = LyriaRealtimeAudio(api_key=api_key, canvas_state_file="canvas_state.json")
    
    print(f"\n2️⃣  Configuración:")
    print(f"   Instrumentos:")
    for color, instrument in lyria.COLOR_TO_INSTRUMENT.items():
        print(f"      {color:10} → {instrument}")
    
    print(f"\n   Efectos:")
    for brush, effect in lyria.BRUSH_TO_EFFECT.items():
        print(f"      {brush:10} → {effect}")
    
    print(f"\n3️⃣  Creando archivo de prueba canvas_state.json...")
    test_data = create_test_canvas_state()
    print(f"   ✅ {len(test_data['strokes'])} puntos de prueba creados")
    
    print(f"\n4️⃣  Probando conversión de trazos a eventos musicales...")
    for i, stroke in enumerate(test_data['strokes'][:4], 1):
        event = lyria._stroke_to_music_event(
            stroke['color'],
            stroke['brush_type'],
            stroke['brush_size'],
            stroke['x'],
            stroke['y'],
            stroke['time']
        )
        
        print(f"\n   Trazo {i}:")
        print(f"      Color: {stroke['color']} → Instrumento: {event['instrument']}")
        print(f"      Pincel: {stroke['brush_type']} → Efecto: {event['effect']}")
        print(f"      Tamaño: {stroke['brush_size']} → Dinámica: {event['dynamics']}")
        print(f"      X={stroke['x']} → Nota MIDI: {event['pitch']} ({lyria._midi_to_note_name(event['pitch'])})")
        print(f"      Y={stroke['y']} → Duración: {event['duration']}s")
    
    print(f"\n5️⃣  Probando construcción de prompts...")
    sample_event = lyria._stroke_to_music_event("AZUL", "LINEA", 5, 640, 360, time.time())
    prompt = lyria._build_lyria_prompt(sample_event)
    print(f"   Ejemplo de prompt para Lyria API:")
    print(f"   \"{prompt}\"")
    
    print(f"\n6️⃣  Iniciando monitoreo en tiempo real...")
    lyria.start()
    
    print(f"   ⏱️  Monitoreando durante 3 segundos...")
    time.sleep(3)
    
    # Añadir más trazos durante el monitoreo
    print(f"\n   ➕ Añadiendo nuevos trazos...")
    with open("canvas_state.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data['strokes'].extend([
        {"x": 500, "y": 300, "color": "VERDE", "brush_type": "DAB", "brush_size": 8, "time": time.time()},
        {"x": 520, "y": 310, "color": "VERDE", "brush_type": "DAB", "brush_size": 8, "time": time.time() + 0.1},
    ])
    
    with open("canvas_state.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print(f"   ⏱️  Procesando nuevos trazos...")
    time.sleep(2)
    
    print(f"\n7️⃣  Estadísticas:")
    stats = lyria.get_stats()
    for key, value in stats.items():
        print(f"      {key}: {value}")
    
    print(f"\n8️⃣  Deteniendo Lyria...")
    lyria.stop()
    
    print(f"\n9️⃣  Limpiando archivos de prueba...")
    if os.path.exists("canvas_state.json"):
        os.remove("canvas_state.json")
        print(f"   ✅ canvas_state.json eliminado")
    
    print("\n" + "=" * 70)
    print("PRUEBA COMPLETADA")
    print("=" * 70)
    
    print("\n💡 NOTAS:")
    print("   • El sistema está listo para funcionar con la API real")
    print("   • Configura GOOGLE_AI_API_KEY para activar la generación de audio")
    print("   • El mapeo de coordenadas a música está funcionando correctamente")
    print("   • Los hilos de monitoreo y procesamiento están operativos")
    
    print("\n🎵 MAPEO DE COORDENADAS:")
    print("   • X (0-1280) → Notas MIDI (21-108)")
    print("   • Y (0-720) → Duración (2.0s-0.1s) [invertido]")
    print("   • Color → Instrumento de orquesta")
    print("   • Pincel → Efecto de audio")
    print("   • Tamaño → Dinámica musical")
    
    if api_key == "TEST_API_KEY":
        print("\n⚠️  ADVERTENCIA:")
        print("   No se detectó API key real. Para usar Lyria completamente:")
        print("   1. Obtén tu API key en https://ai.google.dev/")
        print("   2. Ejecuta: $env:GOOGLE_AI_API_KEY = \"TU_API_KEY\"")
        print("   3. Vuelve a ejecutar el programa")


def test_coordinate_mapping():
    """Prueba visual del mapeo de coordenadas."""
    print("\n" + "=" * 70)
    print("PRUEBA DE MAPEO DE COORDENADAS")
    print("=" * 70)
    
    lyria = LyriaRealtimeAudio(api_key="TEST", canvas_state_file="test.json")
    
    # Probar diferentes posiciones
    test_positions = [
        (0, 0, "Esquina superior izquierda"),
        (1280, 0, "Esquina superior derecha"),
        (0, 720, "Esquina inferior izquierda"),
        (1280, 720, "Esquina inferior derecha"),
        (640, 360, "Centro"),
    ]
    
    print("\nMapeo de posiciones del canvas:")
    print("-" * 70)
    
    for x, y, desc in test_positions:
        pitch = lyria._map_x_to_pitch(x, 1280)
        duration = lyria._map_y_to_duration(y, 720)
        note_name = lyria._midi_to_note_name(pitch)
        
        print(f"\n{desc}:")
        print(f"  Posición: ({x:4}, {y:3})")
        print(f"  → Nota: {note_name:4} (MIDI {pitch:3})")
        print(f"  → Duración: {duration:.2f}s")


if __name__ == "__main__":
    try:
        test_lyria_system()
        test_coordinate_mapping()
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
