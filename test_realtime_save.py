"""
Script de prueba para verificar el guardado en tiempo real del canvas.
Simula el dibujo y muestra cómo se actualiza el archivo JSON.
"""

import sys
import os
import time
import json

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.canvas import Canvas

# Configuración de prueba
COLORS = {
    'AZUL': (255, 0, 0),
    'VERDE': (0, 255, 0),
    'ROJO': (0, 0, 255),
    'AMARILLO': (0, 255, 255)
}

def print_json_content(filename):
    """Muestra el contenido del archivo JSON."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"\n📄 Contenido de {filename}:")
        print(f"   Total de puntos: {len(data['strokes'])}")
        if data['strokes']:
            print(f"   Primeros puntos:")
            for i, point in enumerate(data['strokes'][:3]):
                print(f"     {i+1}. x={point['x']}, y={point['y']}, "
                      f"color={point['color']}, brush={point['brush_type']}, "
                      f"size={point['brush_size']}")
    else:
        print(f"\n❌ Archivo {filename} no existe")

def test_real_time_save():
    """Prueba el guardado en tiempo real."""
    print("=" * 70)
    print("PRUEBA DE GUARDADO EN TIEMPO REAL")
    print("=" * 70)
    
    save_file = "canvas_state.json"
    
    # Eliminar archivo si existe (limpieza previa)
    if os.path.exists(save_file):
        os.remove(save_file)
        print(f"✓ Archivo anterior eliminado")
    
    # Crear canvas
    print(f"\n1️⃣  Creando canvas...")
    canvas = Canvas(800, 600, COLORS, auto_save_file=save_file)
    print(f"✓ Canvas creado")
    print_json_content(save_file)
    
    # Simular trazo 1
    print(f"\n2️⃣  Dibujando trazo 1 (AZUL, LINEA)...")
    canvas.start_stroke('AZUL', 'LINEA', 5)
    for i in range(5):
        canvas.add_point(0.1 + i * 0.02, 0.2 + i * 0.01)
        time.sleep(0.1)  # Simular dibujo en tiempo real
    canvas.end_stroke()
    print(f"✓ Trazo 1 completado")
    print_json_content(save_file)
    
    # Simular trazo 2
    print(f"\n3️⃣  Dibujando trazo 2 (ROJO, DAB)...")
    canvas.start_stroke('ROJO', 'DAB', 10)
    for i in range(4):
        canvas.add_point(0.4 + i * 0.03, 0.5 + i * 0.02)
        time.sleep(0.1)
    canvas.end_stroke()
    print(f"✓ Trazo 2 completado")
    print_json_content(save_file)
    
    # Simular trazo 3
    print(f"\n4️⃣  Dibujando trazo 3 (AMARILLO, LINEA)...")
    canvas.start_stroke('AMARILLO', 'LINEA', 8)
    for i in range(3):
        canvas.add_point(0.6 + i * 0.02, 0.3 - i * 0.01)
        time.sleep(0.1)
    canvas.end_stroke()
    print(f"✓ Trazo 3 completado")
    print_json_content(save_file)
    
    # Mostrar estadísticas finales
    print(f"\n5️⃣  Estadísticas finales:")
    print(f"   Total de trazos en canvas: {len(canvas.strokes)}")
    
    # Mostrar el JSON completo
    print(f"\n📋 Contenido completo del archivo JSON:")
    print("-" * 70)
    with open(save_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    print("-" * 70)
    
    # Simular cierre de programa
    print(f"\n6️⃣  Cerrando programa (eliminando archivo)...")
    canvas.delete_save_file()
    
    if os.path.exists(save_file):
        print(f"❌ ERROR: El archivo NO fue eliminado")
    else:
        print(f"✓ Archivo eliminado correctamente")
    
    print("\n" + "=" * 70)
    print("PRUEBA COMPLETADA")
    print("=" * 70)
    print("\n💡 RESUMEN:")
    print("   • El archivo JSON se crea automáticamente al iniciar")
    print("   • Se actualiza en TIEMPO REAL cada vez que añades un punto")
    print("   • Se elimina automáticamente cuando cierras el programa")
    print("   • Formato: {'strokes': [{'x', 'y', 'color', 'brush_type', 'brush_size', 'time'}]}")

if __name__ == "__main__":
    try:
        test_real_time_save()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
