import cv2
import numpy as np
from collections import deque
import mediapipe as mp
import random

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.4, min_tracking_confidence=0.5)
# mp_draw = mp.solutions.drawing_utils # No usaremos el drawing_utils por defecto para dibujar los landmarks

# Deques para almacenar puntos para cada color y segmento de trazo
bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]

# Índices para el segmento de trazo actual para cada color
blue_index = 0
green_index = 0
red_index = 0
yellow_index = 0

# Colores para dibujar (B, G, R, Y)
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]  # OpenCV usa BGR
color_names = ["AZUL", "VERDE", "ROJO", "AMARILLO"]
colorIndex = 0  # Color seleccionado actualmente (por defecto: AZUL)

# Definir tipos de pincel y tamaños
brush_types = ["LINEA", "DAB"]  # LINEA para trazo continuo, DAB para efecto impresionista
brushTypeIndex = 0  # 0: LINEA, 1: DAB (por defecto: LINEA)

brush_sizes = [2, 5, 10]  # Pequeño, Mediano, Grande (grosor de línea / radio de dab)
brushSizeIndex = 0  # Tamaño de pincel seleccionado actualmente (por defecto: PEQUEÑO)

# Configuración de la ventana de pintura (lienzo)
PAINT_WINDOW_WIDTH = 1280
PAINT_WINDOW_HEIGHT = 720
paintWindow = np.zeros((PAINT_WINDOW_HEIGHT, PAINT_WINDOW_WIDTH, 3), dtype=np.uint8) + 255
cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

# Configuración de la cámara
cap = cv2.VideoCapture(0)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

# --- CONSTANTE PARA LA FLEXIBILIDAD EN LA DETECCIÓN DE GESTOS ---
# Un valor más alto hace la detección menos estricta (más fácil de activar)
# Un valor más bajo la hace más estricta. Ajusta según tus necesidades.
FLEXIBILITY_THRESHOLD = 0.02  # Un porcentaje pequeño del espacio de coordenadas normalizado (0 a 1)


# --- FUNCIÓN DE DETECCIÓN DE GESTOS: Índice extendido, otros flexionados (Pulgar ignorado) ---
def is_drawing_gesture(landmarks):  # handedness_label ya no es necesario aquí
    # Funciones auxiliares para obtener coordenadas de forma más limpia
    def get_y(landmark_idx): return landmarks[landmark_idx].y

    # 1. Dedo índice extendido
    # La punta (8) debe estar por encima de PIP (7), y PIP (7) por encima de MCP (6)
    index_extended = (get_y(mp_hands.HandLandmark.INDEX_FINGER_TIP) < get_y(
        mp_hands.HandLandmark.INDEX_FINGER_PIP) - FLEXIBILITY_THRESHOLD) and \
                     (get_y(mp_hands.HandLandmark.INDEX_FINGER_PIP) < get_y(
                         mp_hands.HandLandmark.INDEX_FINGER_MCP) - FLEXIBILITY_THRESHOLD)

    # 2. Dedos corazón, anular y meñique deben estar flexionados
    # La punta debe estar por debajo de la articulación PIP (es decir, tip_y > pip_y)
    middle_flexed = (get_y(mp_hands.HandLandmark.MIDDLE_FINGER_TIP) > get_y(
        mp_hands.HandLandmark.MIDDLE_FINGER_PIP) + FLEXIBILITY_THRESHOLD)
    ring_flexed = (get_y(mp_hands.HandLandmark.RING_FINGER_TIP) > get_y(
        mp_hands.HandLandmark.RING_FINGER_PIP) + FLEXIBILITY_THRESHOLD)
    pinky_flexed = (
                get_y(mp_hands.HandLandmark.PINKY_TIP) > get_y(mp_hands.HandLandmark.PINKY_PIP) + FLEXIBILITY_THRESHOLD)

    # Todas las condiciones deben cumplirse para el gesto de dibujo (pulgar ahora ignorado)
    return index_extended and middle_flexed and ring_flexed and pinky_flexed


# --- FUNCIÓN PARA GRAFICAR LA POSICIÓN CONFIGURADA (RETROALIMENTACIÓN VISUAL) ---
def draw_gesture_feedback(frame, landmarks, is_gesture_active):  # handedness_label ya no es necesario aquí
    H, W, _ = frame.shape

    # Helper para convertir coords normalizadas a píxeles
    def to_pixel(landmark_coord):
        return (int(landmark_coord.x * W), int(landmark_coord.y * H))

    # Colores para feedback
    COLOR_MET = (0, 255, 0)  # Verde si la condición se cumple
    COLOR_NOT_MET = (0, 0, 255)  # Rojo si la condición no se cumple
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    TEXT_SCALE = 0.5
    TEXT_THICKNESS = 1
    LINE_THICKNESS = 2
    RADIUS = 5

    feedback_text_lines = []

    # Funciones auxiliares para obtener coordenadas de forma más limpia
    def get_y(landmark_idx):
        return landmarks[landmark_idx].y

    # --- Dedo Índice ---
    index_tip_px = to_pixel(landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP])
    index_dip_px = to_pixel(landmarks[mp_hands.HandLandmark.INDEX_FINGER_DIP])
    index_pip_px = to_pixel(landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP])
    index_mcp_px = to_pixel(landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP])

    index_extended_y_check_1 = get_y(mp_hands.HandLandmark.INDEX_FINGER_TIP) < get_y(
        mp_hands.HandLandmark.INDEX_FINGER_PIP) - FLEXIBILITY_THRESHOLD
    index_extended_y_check_2 = get_y(mp_hands.HandLandmark.INDEX_FINGER_PIP) < get_y(
        mp_hands.HandLandmark.INDEX_FINGER_MCP) - FLEXIBILITY_THRESHOLD
    index_condition_met = index_extended_y_check_1 and index_extended_y_check_2

    color_index = COLOR_MET if index_condition_met else COLOR_NOT_MET

    cv2.line(frame, index_mcp_px, index_pip_px, color_index, LINE_THICKNESS)
    cv2.line(frame, index_pip_px, index_dip_px, color_index, LINE_THICKNESS)
    cv2.line(frame, index_dip_px, index_tip_px, color_index, LINE_THICKNESS)
    cv2.circle(frame, index_tip_px, RADIUS, color_index, -1)
    cv2.circle(frame, index_dip_px, RADIUS, color_index, -1)
    cv2.circle(frame, index_pip_px, RADIUS, color_index, -1)
    cv2.circle(frame, index_mcp_px, RADIUS, color_index, -1)
    if not index_condition_met:
        feedback_text_lines.append("Indice: NO EXTENDIDO")
    else:
        feedback_text_lines.append("Indice: EXTENDIDO")

    # --- Dedos Corazón, Anular y Meñique (Flexionados) ---
    finger_data = [
        (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_DIP,
         mp_hands.HandLandmark.MIDDLE_FINGER_PIP, mp_hands.HandLandmark.MIDDLE_FINGER_MCP, "Corazon"),
        (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_DIP,
         mp_hands.HandLandmark.RING_FINGER_PIP, mp_hands.HandLandmark.RING_FINGER_MCP, "Anular"),
        (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_DIP, mp_hands.HandLandmark.PINKY_PIP,
         mp_hands.HandLandmark.PINKY_MCP, "Meñique"),
    ]

    for tip_idx, dip_idx, pip_idx, mcp_idx, name in finger_data:
        tip_px = to_pixel(landmarks[tip_idx])
        dip_px = to_pixel(landmarks[dip_idx])
        pip_px = to_pixel(landmarks[pip_idx])
        mcp_px = to_pixel(landmarks[mcp_idx])

        # Condición de flexionado: la punta debe estar por debajo de la PIP
        flexed_condition = get_y(tip_idx) > get_y(pip_idx) + FLEXIBILITY_THRESHOLD
        color_finger = COLOR_MET if flexed_condition else COLOR_NOT_MET

        cv2.line(frame, mcp_px, pip_px, color_finger, LINE_THICKNESS)
        cv2.line(frame, pip_px, dip_px, color_finger, LINE_THICKNESS)
        cv2.line(frame, dip_px, tip_px, color_finger, LINE_THICKNESS)
        cv2.circle(frame, tip_px, RADIUS, color_finger, -1)
        cv2.circle(frame, dip_px, RADIUS, color_finger, -1)
        cv2.circle(frame, pip_px, RADIUS, color_finger, -1)
        cv2.circle(frame, mcp_px, RADIUS, color_finger, -1)
        if not flexed_condition:
            feedback_text_lines.append(f"{name}: NO FLEXIONADO")
        else:
            feedback_text_lines.append(f"{name}: FLEXIONADO")

    # Mostrar estado general del gesto
    if is_gesture_active:
        cv2.putText(frame, "GESTO OK - DIBUJANDO", (10, 30), FONT, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        cv2.putText(frame, "GESTO NO DETECTADO", (10, 30), FONT, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
        for line_num, text_feedback in enumerate(feedback_text_lines):
            cv2.putText(frame, text_feedback, (10, 60 + line_num * 25), FONT, TEXT_SCALE, (0, 0, 255), TEXT_THICKNESS,
                        cv2.LINE_AA)


print("--- Control Teclado para Pintura Interactiva (Gesto de Índice Único Extendio) ---")
print(" 'q': Salir del programa")
print(" 'c': Borrar todo el lienzo")
print(" '1', '2', '3', '4': Seleccionar color (AZUL, VERDE, ROJO, AMARILLO)")
print(" 't': Cambiar tipo de pincel (LINEA / DAB)")
print(" 's': Cambiar tamaño de pincel (PEQUEÑO / MEDIANO / GRANDE)")
print("\n--- Dibujo con la Mano (Gesto Simplificado con Retroalimentación Visual) ---")
print(f"Para dibujar, extiende SOLO tu dedo índice. El pulgar no es relevante.")
print("Los dedos corazón, anular y meñique deben estar flexionados hacia la palma.")
print("Observa el feedback visual en la ventana 'Tracking' para ajustar tu mano.")
print("Puedes ajustar 'FLEXIBILITY_THRESHOLD' en el código para que sea más o menos estricto.")
print("-------------------------------------------------------------------------")

# Bucle principal
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Voltear horizontalmente para efecto espejo

    # Detección de manos
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    gesture_detected_this_frame = False

    if result.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(result.multi_hand_landmarks):
            # NO USAMOS mp_draw.draw_landmarks aquí, nuestra función draw_gesture_feedback dibuja los landmarks con colores de estado

            # handedness_label ya no es necesario aquí para el gesto, pero MediaPipe todavía lo proporciona
            # Podrías usarlo si quisieras dibujar algo específico para mano izquierda/derecha, pero para el gesto ya no.
            # handedness_label = result.multi_handedness[i].classification[0].label
            landmarks = hand_landmarks.landmark

            if is_drawing_gesture(landmarks):  # Ahora solo se pasa 'landmarks'
                gesture_detected_this_frame = True
                index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Escalar las coordenadas del centro desde la resolución del 'frame'
                # a la resolución fija del 'paintWindow'
                paint_x = int(index_tip.x * PAINT_WINDOW_WIDTH)
                paint_y = int(index_tip.y * PAINT_WINDOW_HEIGHT)
                scaled_center = (paint_x, paint_y)

                # Añadir punto al trazo actual para el color seleccionado
                if colorIndex == 0:
                    bpoints[blue_index].appendleft(scaled_center)
                elif colorIndex == 1:
                    gpoints[green_index].appendleft(scaled_center)
                elif colorIndex == 2:
                    rpoints[red_index].appendleft(scaled_center)
                elif colorIndex == 3:
                    ypoints[yellow_index].appendleft(scaled_center)
            else:
                # Si el gesto de dibujo no se detecta, romper el trazo actual
                # Esto asegura trazos distintos cuando el "bolígrafo" se "levanta"
                # Solo añade un nuevo deque si el actual ya tiene puntos
                if bpoints and len(bpoints[blue_index]) != 0:
                    bpoints.append(deque(maxlen=1024))
                    blue_index += 1
                if gpoints and len(gpoints[green_index]) != 0:
                    gpoints.append(deque(maxlen=1024))
                    green_index += 1
                if rpoints and len(rpoints[red_index]) != 0:
                    rpoints.append(deque(maxlen=1024))
                    red_index += 1
                if ypoints and len(ypoints[yellow_index]) != 0:
                    ypoints.append(deque(maxlen=1024))
                    yellow_index += 1

            # --- LLAMAR A LA FUNCIÓN DE GRAFICADO DE FEEDBACK ---
            # Aquí también se elimina handedness_label si no se usa internamente en draw_gesture_feedback
            draw_gesture_feedback(frame, landmarks, gesture_detected_this_frame)

    # --- Dibujar líneas/dabs en el lienzo (paintWindow) ---
    points_list = [bpoints, gpoints, rpoints, ypoints]
    current_brush_size = brush_sizes[brushSizeIndex]

    for i in range(len(points_list)):  # Iterar por cada color
        for j in range(len(points_list[i])):  # Iterar por cada segmento de trazo del color
            for k in range(1, len(points_list[i][j])):  # Iterar por los puntos dentro del segmento
                p1 = points_list[i][j][k - 1]
                p2 = points_list[i][j][k]
                if p1 is None or p2 is None:  # Asegurarse de que los puntos existen
                    continue

                if brushTypeIndex == 0:  # Pincel LINEA (trazo continuo)
                    cv2.line(paintWindow, p1, p2, colors[i], current_brush_size)
                elif brushTypeIndex == 1:  # Pincel DAB (impresionista)
                    distance = np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
                    num_dabs = max(1, int(distance / (current_brush_size * 1.5)))

                    for step in range(num_dabs):
                        alpha = step / num_dabs
                        dab_x = int(p1[0] * (1 - alpha) + p2[0] * alpha)
                        dab_y = int(p1[1] * (1 - alpha) + p2[1] * alpha)

                        offset_x = random.randint(-current_brush_size // 2, current_brush_size // 2)
                        offset_y = random.randint(-current_brush_size // 2, current_brush_size // 2)

                        random_radius_offset = random.randint(-current_brush_size // 3, current_brush_size // 3)
                        dab_radius = max(1, current_brush_size + random_radius_offset)

                        final_dab_x = max(0, min(PAINT_WINDOW_WIDTH - 1, dab_x + offset_x))
                        final_dab_y = max(0, min(PAINT_WINDOW_HEIGHT - 1, dab_y + offset_y))

                        cv2.circle(paintWindow, (final_dab_x, final_dab_y), dab_radius, colors[i], -1)

    cv2.imshow("Tracking", frame)
    cv2.imshow("Paint", paintWindow)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("c"):
        paintWindow = np.zeros((PAINT_WINDOW_HEIGHT, PAINT_WINDOW_WIDTH, 3), dtype=np.uint8) + 255
        bpoints = [deque(maxlen=1024)]
        gpoints = [deque(maxlen=1024)]
        rpoints = [deque(maxlen=1024)]
        ypoints = [deque(maxlen=1024)]
        blue_index = 0
        green_index = 0
        red_index = 0
        yellow_index = 0
        print("Lienzo borrado.")
    elif key == ord("1"):
        colorIndex = 0  # Azul
        print(f"Color seleccionado: {color_names[colorIndex]}")
    elif key == ord("2"):
        colorIndex = 1  # Verde
        print(f"Color seleccionado: {color_names[colorIndex]}")
    elif key == ord("3"):
        colorIndex = 2  # Rojo
        print(f"Color seleccionado: {color_names[colorIndex]}")
    elif key == ord("4"):
        colorIndex = 3  # Amarillo
        print(f"Color seleccionado: {color_names[colorIndex]}")
    elif key == ord("t"):
        brushTypeIndex = (brushTypeIndex + 1) % len(brush_types)
        print(f"Tipo de pincel: {brush_types[brushTypeIndex]}")
    elif key == ord("s"):
        brushSizeIndex = (brushSizeIndex + 1) % len(brush_sizes)
        print(f"Tamaño de pincel: {brush_sizes[brushSizeIndex]}")

cap.release()
cv2.destroyAllWindows()