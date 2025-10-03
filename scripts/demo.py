"""
Script de demostración y diagnóstico del sistema.

Ejecuta este script para verificar que todos los componentes funcionan correctamente.
"""

import sys
import os
import cv2
import numpy as np
import mediapipe as mp

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def check_dependencies():
    """Verifica que todas las dependencias estén instaladas."""
    print("=" * 60)
    print("VERIFICACIÓN DE DEPENDENCIAS")
    print("=" * 60)
    
    dependencies = {
        'opencv-python': cv2.__version__,
        'mediapipe': mp.__version__,
        'numpy': np.__version__
    }
    
    for name, version in dependencies.items():
        print(f"✓ {name}: {version}")
    
    print("\n¡Todas las dependencias están instaladas correctamente!")
    print()


def check_camera():
    """Verifica que la cámara esté disponible."""
    print("=" * 60)
    print("VERIFICACIÓN DE CÁMARA")
    print("=" * 60)
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("✗ Error: No se pudo abrir la cámara")
        print("  Intenta con diferentes índices: VideoCapture(1), VideoCapture(2), etc.")
        return False
    
    ret, frame = cap.read()
    if not ret:
        print("✗ Error: No se pudo leer frame de la cámara")
        cap.release()
        return False
    
    print(f"✓ Cámara detectada correctamente")
    print(f"  Resolución: {frame.shape[1]}x{frame.shape[0]}")
    
    cap.release()
    print()
    return True


def check_mediapipe():
    """Verifica que MediaPipe funcione correctamente."""
    print("=" * 60)
    print("VERIFICACIÓN DE MEDIAPIPE HANDS")
    print("=" * 60)
    
    try:
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.5
        )
        
        # Crear frame de prueba
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        rgb_frame = cv2.cvtColor(test_frame, cv2.COLOR_BGR2RGB)
        
        # Procesar
        result = hands.process(rgb_frame)
        
        hands.close()
        
        print("✓ MediaPipe Hands inicializado correctamente")
        print()
        return True
        
    except Exception as e:
        print(f"✗ Error al inicializar MediaPipe: {e}")
        print()
        return False


def check_modules():
    """Verifica que todos los módulos del proyecto se puedan importar."""
    print("=" * 60)
    print("VERIFICACIÓN DE MÓDULOS DEL PROYECTO")
    print("=" * 60)
    
    modules = [
        'core.config',
        'core.gesture_detector',
        'core.brushes',
        'core.canvas',
        'core.feedback',
        'utils.utils',
        'utils.extensions'
    ]
    
    all_ok = True
    
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name}.py")
        except ImportError as e:
            print(f"✗ {module_name}.py - Error: {e}")
            all_ok = False
    
    print()
    if all_ok:
        print("¡Todos los módulos se importaron correctamente!")
    else:
        print("Hay errores en algunos módulos. Revisa los mensajes anteriores.")
    
    print()
    return all_ok


def demo_brushes():
    """Demuestra los diferentes pinceles."""
    print("=" * 60)
    print("DEMOSTRACIÓN DE PINCELES")
    print("=" * 60)
    
    from core.brushes import LineBrush, DabBrush
    from core.config import COLORS
    
    # Crear canvas de demostración
    demo_canvas = np.zeros((400, 800, 3), dtype=np.uint8) + 255
    
    # Pincel de línea
    line_brush = LineBrush(size=3)
    for i in range(50):
        x = 100 + i * 4
        y = 100 + int(30 * np.sin(i * 0.2))
        p1 = (x, y)
        p2 = (x + 4, y + int(30 * np.sin((i + 1) * 0.2)))
        line_brush.draw(demo_canvas, p1, p2, COLORS['AZUL'])
    
    # Pincel dab
    dab_brush = DabBrush(size=5)
    for i in range(50):
        x = 100 + i * 4
        y = 250 + int(30 * np.sin(i * 0.2))
        p1 = (x, y)
        p2 = (x + 4, y + int(30 * np.sin((i + 1) * 0.2)))
        dab_brush.draw(demo_canvas, p1, p2, COLORS['ROJO'])
    
    # Etiquetas
    cv2.putText(demo_canvas, "LineBrush", (20, 110), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(demo_canvas, "DabBrush", (20, 260), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    cv2.imshow("Demo de Pinceles", demo_canvas)
    print("✓ Ventana de demostración abierta")
    print("  Presiona cualquier tecla para continuar...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print()


def demo_canvas():
    """Demuestra el sistema de canvas."""
    print("=" * 60)
    print("DEMOSTRACIÓN DE CANVAS")
    print("=" * 60)
    
    from core.canvas import Canvas
    from core.brushes import LineBrush
    from core.config import COLORS
    
    # Crear canvas
    canvas = Canvas(640, 480, COLORS)
    
    # Añadir puntos simulados
    print("  Añadiendo trazos simulados...")
    
    # Trazo 1 (Azul)
    canvas.set_color(0)
    for i in range(50):
        x = 0.2 + i * 0.01
        y = 0.3 + 0.1 * np.sin(i * 0.3)
        canvas.add_point(x, y)
    
    canvas.break_current_stroke()
    
    # Trazo 2 (Rojo)
    canvas.set_color(2)
    for i in range(50):
        x = 0.2 + i * 0.01
        y = 0.6 + 0.1 * np.sin(i * 0.3)
        canvas.add_point(x, y)
    
    # Renderizar
    brush = LineBrush(size=3)
    canvas.render(brush)
    
    cv2.imshow("Demo de Canvas", canvas.get_image())
    print("✓ Canvas renderizado correctamente")
    print("  Presiona cualquier tecla para continuar...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print()


def run_full_demo():
    """Ejecuta una demostración completa del sistema."""
    print("\n")
    print("=" * 60)
    print("DEMOSTRACIÓN COMPLETA DEL SISTEMA")
    print("Pintura Interactiva con Gestos - Transgresión Digital")
    print("=" * 60)
    print()
    
    # Verificaciones
    check_dependencies()
    
    camera_ok = check_camera()
    mediapipe_ok = check_mediapipe()
    modules_ok = check_modules()
    
    if not (camera_ok and mediapipe_ok and modules_ok):
        print("\n⚠️  Hay problemas con el sistema. Revisa los errores anteriores.")
        return False
    
    # Demos visuales
    print("Ahora se mostrarán algunas demostraciones visuales.")
    print("Presiona cualquier tecla en cada ventana para continuar.\n")
    
    input("Presiona ENTER para ver la demo de pinceles...")
    demo_brushes()
    
    input("Presiona ENTER para ver la demo de canvas...")
    demo_canvas()
    
    print("=" * 60)
    print("✓ TODAS LAS VERIFICACIONES COMPLETADAS")
    print("=" * 60)
    print()
    print("El sistema está listo para usar. Ejecuta:")
    print("  python main.py")
    print()
    
    return True


def print_system_info():
    """Imprime información del sistema."""
    print("=" * 60)
    print("INFORMACIÓN DEL SISTEMA")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Plataforma: {sys.platform}")
    print()


if __name__ == "__main__":
    print_system_info()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "camera":
            check_camera()
        elif command == "deps":
            check_dependencies()
        elif command == "mediapipe":
            check_mediapipe()
        elif command == "modules":
            check_modules()
        elif command == "brushes":
            demo_brushes()
        elif command == "canvas":
            demo_canvas()
        else:
            print(f"Comando desconocido: {command}")
            print("\nComandos disponibles:")
            print("  python demo.py camera    - Verifica la cámara")
            print("  python demo.py deps      - Verifica dependencias")
            print("  python demo.py mediapipe - Verifica MediaPipe")
            print("  python demo.py modules   - Verifica módulos")
            print("  python demo.py brushes   - Demo de pinceles")
            print("  python demo.py canvas    - Demo de canvas")
    else:
        # Demo completa
        run_full_demo()
