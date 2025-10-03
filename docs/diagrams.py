"""
Visualización de la arquitectura del proyecto.

Este archivo contiene diagramas ASCII de la estructura del sistema.
"""

ARCHITECTURE_DIAGRAM = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                      PINTURA CON GESTOS - ARQUITECTURA                    ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────┐
│                            PAINT APP (Main)                             │
│                         Orquestador Principal                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ - Gestiona bucle principal                                      │   │
│  │ - Coordina todos los componentes                                │   │
│  │ - Procesa entrada de teclado                                    │   │
│  │ - Renderiza ventanas                                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└────────┬──────────────────────────┬──────────────────────┬──────────────┘
         │                          │                      │
         │                          │                      │
┌────────▼─────────┐      ┌─────────▼────────┐   ┌────────▼─────────┐
│ GESTURE DETECTOR │      │  BRUSH MANAGER   │   │  GESTURE         │
│                  │      │                  │   │  FEEDBACK        │
│ MediaPipe Hands  │      │ Strategy Pattern │   │                  │
│ ┌──────────────┐ │      │ ┌──────────────┐ │   │ Visual Feedback  │
│ │ detect hands │ │      │ │  LineBrush   │ │   │ ┌──────────────┐ │
│ │ landmarks    │ │      │ │  DabBrush    │ │   │ │ draw finger  │ │
│ │ gestures     │ │      │ │  SprayBrush  │ │   │ │ states       │ │
│ └──────────────┘ │      │ │  ...more     │ │   │ └──────────────┘ │
└──────────────────┘      │ └──────────────┘ │   └──────────────────┘
                          └────────┬─────────┘
                                   │
                          ┌────────▼─────────┐
                          │     CANVAS       │
                          │                  │
                          │ Lienzo Digital   │
                          │ ┌──────────────┐ │
                          │ │ Strokes      │ │
                          │ │ Colors       │ │
                          │ │ Points       │ │
                          │ │ Render       │ │
                          │ └──────────────┘ │
                          └──────────────────┘
                                   │
                          ┌────────▼─────────┐
                          │     CONFIG       │
                          │                  │
                          │ Configuración    │
                          │ Global           │
                          └──────────────────┘
"""

DATA_FLOW = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                           FLUJO DE DATOS                                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

1. CAPTURA
   📹 Camera → Frame (BGR)
   
2. PROCESAMIENTO
   Frame → cv2.flip() → Frame Espejo
   Frame → cv2.cvtColor() → Frame RGB
   
3. DETECCIÓN
   Frame RGB → MediaPipe Hands → Results
   Results → Hand Landmarks (21 puntos 3D)
   
4. IDENTIFICACIÓN DE GESTO
   Landmarks → is_drawing_gesture() → Boolean
   Landmarks → get_index_tip_position() → (x, y)
   
5. ACTUALIZACIÓN DE CANVAS
   Si gesto detectado:
     (x, y) → canvas.add_point() → Añadir a deque
   Si no:
     canvas.break_current_stroke() → Nuevo segmento
   
6. RENDERIZADO
   Canvas + BrushManager → Brush.draw()
   Para cada color:
     Para cada stroke:
       Para cada punto:
         p1, p2 → brush.draw(canvas, p1, p2, color)
   
7. FEEDBACK VISUAL
   Landmarks → GestureFeedback.draw()
   Dibuja estado de cada dedo con colores
   
8. VISUALIZACIÓN
   cv2.imshow("Tracking", frame_con_feedback)
   cv2.imshow("Paint", canvas_renderizado)
   
9. INPUT
   cv2.waitKey(1) → Procesar teclas
   Actualizar estado según input
   
10. LOOP
    Repetir desde paso 1
"""

CLASS_HIERARCHY = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                        JERARQUÍA DE CLASES                                ║
╚═══════════════════════════════════════════════════════════════════════════╝

Brush (ABC)
├── LineBrush
├── DabBrush
└── (Extensiones en extensions.py)
    ├── SprayBrush
    ├── CalligraphyBrush
    ├── GlitchBrush
    ├── NeonBrush
    └── WatercolorBrush

PaintApp
├── GestureDetector
│   └── mp.solutions.hands.Hands
├── BrushManager
│   └── {tipo: Clase de Brush}
├── Canvas
│   └── {color: [deque, deque, ...]}
└── GestureFeedback

ImageExporter (utils)
ArtisticFilters (utils)
PerformanceMonitor (utils)
ColorPalette (utils)
SessionRecorder (utils)
StrokeAnalyzer (utils)
"""

RESPONSIBILITY_MAP = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                    MAPA DE RESPONSABILIDADES                              ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌─────────────────────┬──────────────────────────────────────────────────┐
│ COMPONENTE          │ RESPONSABILIDAD                                  │
├─────────────────────┼──────────────────────────────────────────────────┤
│ PaintApp            │ Coordinar aplicación, bucle principal            │
│ GestureDetector     │ Detectar manos y gestos específicos              │
│ BrushManager        │ Gestionar tipos y tamaños de pinceles            │
│ Canvas              │ Almacenar y renderizar trazos                    │
│ GestureFeedback     │ Mostrar estado visual de gestos                  │
│ Brush (ABC)         │ Definir interfaz para pinceles                   │
│ LineBrush           │ Dibujar líneas continuas                         │
│ DabBrush            │ Dibujar con efecto impresionista                 │
│ Config              │ Almacenar configuración global                   │
│ Utils               │ Herramientas auxiliares (export, filters, etc.)  │
│ Extensions          │ Ejemplos de extensiones del sistema              │
└─────────────────────┴──────────────────────────────────────────────────┘
"""

EXTENSION_POINTS = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                       PUNTOS DE EXTENSIÓN                                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

🎨 NUEVOS PINCELES
   1. Heredar de Brush
   2. Implementar draw(canvas, p1, p2, color)
   3. Registrar en BrushManager._brushes
   4. Añadir a config.BRUSH_TYPES
   
   Ejemplo:
   class MiPincel(Brush):
       def draw(self, canvas, p1, p2, color):
           # Tu lógica aquí
           pass

🤚 NUEVOS GESTOS
   1. Crear método estático en GestureDetector
   2. Usar landmarks para detectar condiciones
   3. Integrar en PaintApp.process_frame()
   
   Ejemplo:
   @staticmethod
   def is_mi_gesto(landmarks):
       # Tu lógica de detección
       return True/False

🎨 NUEVOS COLORES
   1. Añadir a config.COLORS
   2. Añadir a config.COLOR_NAMES
   3. Añadir control de teclado en main.py
   
   Ejemplo:
   COLORS = {
       'AZUL': (255, 0, 0),
       'MI_COLOR': (R, G, B)  # ← Nuevo
   }

🔧 NUEVOS FILTROS
   1. Añadir método estático en ArtisticFilters
   2. Usar OpenCV para transformar imagen
   
   Ejemplo:
   @staticmethod
   def apply_mi_filtro(image):
       # Tu procesamiento
       return transformed_image

📊 NUEVO ANÁLISIS
   1. Añadir método en StrokeAnalyzer
   2. Analizar canvas.strokes
   
   Ejemplo:
   @staticmethod
   def analyze_mi_metrica(strokes):
       # Tu análisis
       return resultado
"""

TESTING_GUIDE = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                          GUÍA DE TESTING                                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

📋 ESTRUCTURA DE TESTS

test_components.py
├── TestBrushes
│   ├── test_line_brush_draws
│   ├── test_dab_brush_draws
│   ├── test_brush_manager_switches_type
│   └── test_brush_manager_switches_size
└── TestCanvas
    ├── test_canvas_initializes_white
    ├── test_add_point
    ├── test_clear_canvas
    ├── test_change_color
    └── test_break_stroke

🧪 CÓMO AÑADIR TESTS

class TestMiComponente(unittest.TestCase):
    def setUp(self):
        # Preparación
        self.componente = MiComponente()
    
    def test_mi_funcionalidad(self):
        # Ejecutar
        resultado = self.componente.hacer_algo()
        
        # Verificar
        self.assertEqual(resultado, esperado)

▶️ EJECUTAR TESTS

# Todos los tests
python -m unittest test_components.py -v

# Test específico
python -m unittest test_components.TestBrushes.test_line_brush_draws -v

# Con cobertura (requiere coverage)
coverage run -m unittest test_components.py
coverage report
"""

def print_all_diagrams():
    """Imprime todos los diagramas."""
    print(ARCHITECTURE_DIAGRAM)
    print("\n" + "="*80 + "\n")
    print(DATA_FLOW)
    print("\n" + "="*80 + "\n")
    print(CLASS_HIERARCHY)
    print("\n" + "="*80 + "\n")
    print(RESPONSIBILITY_MAP)
    print("\n" + "="*80 + "\n")
    print(EXTENSION_POINTS)
    print("\n" + "="*80 + "\n")
    print(TESTING_GUIDE)


if __name__ == "__main__":
    print_all_diagrams()
