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

# Colores disponibles (B, G, R, Y) - OpenCV usa BGR
COLORS = {
    'AZUL': (255, 0, 0),
    'VERDE': (0, 255, 0),
    'ROJO': (0, 0, 255),
    'AMARILLO': (0, 255, 255),
    'BLANCO': (255, 255, 255)
}

# Mantener una lista de nombres consistente con el dict COLORS
COLOR_NAMES = list(COLORS.keys())

# Tipos de pincel disponibles
BRUSH_TYPES = ["LINEA", "DAB", "BORRADOR"]

# Tamaños de pincel disponibles
BRUSH_SIZES = [2, 5, 10]  # Pequeño, Mediano, Grande

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
