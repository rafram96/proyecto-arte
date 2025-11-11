"""
Configuración global de la aplicación de pintura con gestos.
"""

# Configuración de la ventana de pintura
PAINT_WINDOW_WIDTH = 1280
PAINT_WINDOW_HEIGHT = 720
PAINT_WINDOW_NAME = 'Paint'

# Configuración de la cámara
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
TRACKING_WINDOW_NAME = 'Tracking'

# Configuración de MediaPipe
MAX_NUM_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.4
MIN_TRACKING_CONFIDENCE = 0.5

# Constante para la flexibilidad en la detección de gestos
# Un valor más alto hace la detección menos estricta (más fácil de activar)
# Un valor más bajo la hace más estricta
FLEXIBILITY_THRESHOLD = 0.02

# Suavizado para landmarks (posición de la punta del índice). Valor entre 0 y 1.
# Más alto = más respuesta (menos suavizado). Más bajo = menos jitter.
LANDMARK_SMOOTHING_ALPHA = 0.25

# Ajustes más estrictos para la detección/tracking por defecto (mejor estabilidad)
MIN_DETECTION_CONFIDENCE = 0.6
MIN_TRACKING_CONFIDENCE = 0.7
FLEXIBILITY_THRESHOLD = 0.03

# Colores disponibles (B, G, R, Y) - OpenCV usa BGR
COLORS = {
    'AZUL': (255, 106, 31),
    'VERDE': (119, 203, 27),
    'ROJO': (48, 59, 255),
    'AMARILLO': (71, 212, 255),
    'CYAN': (230, 201, 26),
    'MAGENTA': (206, 79, 255),
    'ROSA': (199, 143, 255),
    'GRIS': (184, 165, 160),
    'TURQUESA': (160, 210, 0),
    'INDIGO': (159, 42, 90),
    'DORADO': (27, 146, 196),
    'MARRON': (43, 74, 139),
    'NEGRO': (50, 50, 60),
    'BLANCO': (255, 255, 255),
    'PURPURA': (229, 71, 163),
    'NARANJA': (31, 122, 255),
    'LIMA': (60, 255, 167),
    'COBALTO': (186, 82, 15),
    'CORAL': (89, 111, 255),
    'PLATA': (219, 215, 215)
}

CANVAS_BACKGROUND_COLOR = (0, 0, 0)

COLOR_NAMES = [
    "AZUL",
    "VERDE",
    "ROJO",
    "AMARILLO",
    "CYAN",
    "MAGENTA",
    "ROSA",
    "GRIS",
    "TURQUESA",
    "INDIGO",
    "DORADO",
    "MARRON",
    "NEGRO",
    "BLANCO",
    "PURPURA",
    "NARANJA",
    "LIMA",
    "COBALTO",
    "CORAL",
    "PLATA"
]

# Tipos de pincel disponibles
BRUSH_TYPES = ["LINEA", "DAB", "ERASER"]

# Tamaños de pincel disponibles
BRUSH_SIZES = [2, 5, 10, 20, 50]  # Pequeño, Mediano, Grande, Gigante (20), Jumbo (50)

# Configuración de retroalimentación visual
FEEDBACK_COLOR_MET = (0, 255, 0)  # Verde si la condición se cumple
FEEDBACK_COLOR_NOT_MET = (0, 0, 255)  # Rojo si no se cumple
FEEDBACK_FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX
FEEDBACK_TEXT_SCALE = 0.5
FEEDBACK_TEXT_THICKNESS = 1
FEEDBACK_LINE_THICKNESS = 2
FEEDBACK_CIRCLE_RADIUS = 5

# Configuración de deques para trazos
MAX_POINTS_PER_STROKE = 1024

# Parámetro de suavizado para puntos (valor entre 0 y 1). Más cercano a 0 = más suavizado.
SMOOTHING_ALPHA = 0.35

# Distancia (en píxeles) usada por el borrador para eliminar trazos cercanos
ERASER_DISTANCE_THRESHOLD = 12

# UI: parámetros para la barra superior de selección
UI_TOP_PADDING = 8
UI_BOX_SIZE = 48
UI_BOX_SPACING = 8

# Tiempo (segundos) que hay que mantener el cursor sobre un elemento para seleccionarlo
HOVER_SELECT_SECONDS = 1.2

# Umbral para detectar "pinch" entre índice y medio (distancia normalizada 0..1)
# Si la distancia entre puntas es menor que este umbral, consideramos que están juntas.
PINCH_DISTANCE_THRESHOLD = 0.045

# Número de frames que permitimos perder la mano antes de terminar un trazo
MAX_LOST_HAND_FRAMES = 6
