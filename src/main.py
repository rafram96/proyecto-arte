"""
Aplicación principal de pintura con gestos.
"""

import cv2
from core.config import (
    PAINT_WINDOW_WIDTH, PAINT_WINDOW_HEIGHT, PAINT_WINDOW_NAME,
    CAMERA_WIDTH, CAMERA_HEIGHT, TRACKING_WINDOW_NAME,
    COLORS, COLOR_NAMES, BRUSH_TYPES, BRUSH_SIZES
)
from core.config import UI_TOP_PADDING, UI_BOX_SIZE, UI_BOX_SPACING
from core.gesture_detector import GestureDetector
from core.brushes import BrushManager
from core.canvas import Canvas
from core.feedback import GestureFeedback


class PaintApp:
    """Aplicación principal de pintura con gestos de mano."""
    
    def __init__(self):
        # Inicializar componentes
        self.gesture_detector = GestureDetector()
        self.brush_manager = BrushManager(BRUSH_TYPES, BRUSH_SIZES)
        self.canvas = Canvas(PAINT_WINDOW_WIDTH, PAINT_WINDOW_HEIGHT, COLORS)
        self.feedback = GestureFeedback()
        
        # Configurar ventanas
        cv2.namedWindow(PAINT_WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
        
        # Configurar cámara
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        
        self.running = True
        # Estado previo del gesto para detectar inicio/fin de trazo
        self._prev_gesture = False
        # Estado para selección por pinch (índice+medio)
        self._prev_pinch = False
        self._pinch_candidate = None
        # Última posición del índice reportada (normalizada 0..1)
        self._last_pointer = None
    
    def print_instructions(self):
        """Imprime las instrucciones de uso."""
        print("=" * 80)
        print("PINTURA INTERACTIVA CON GESTOS - TRANSGRESIÓN DIGITAL")
        print("=" * 80)
        print("\n--- Control de Teclado ---")
        print(" 'q': Salir del programa")
        print(" 'c': Borrar todo el lienzo")
        print(" '1', '2', '3', '4': Seleccionar color (AZUL, VERDE, ROJO, AMARILLO)")
        print(" 't': Cambiar tipo de pincel (LINEA / DAB)")
        print(" 's': Cambiar tamaño de pincel (PEQUEÑO / MEDIANO / GRANDE)")
        print("\n--- Dibujo con la Mano ---")
        print("Para dibujar, extiende SOLO tu dedo índice.")
        print("Los dedos corazón y anular deben estar flexionados hacia la palma. (El meñique se ignora)")
        print("Observa el feedback visual en la ventana 'Tracking' para ajustar tu mano.")
        print("=" * 80)
    
    def process_keyboard_input(self):
        """Procesa la entrada del teclado."""
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord("q"):
            self.running = False
        elif key == ord("c"):
            self.canvas.clear()
            print("Lienzo borrado.")
        elif key == ord("1"):
            color = self.canvas.set_color(0)
            print(f"Color seleccionado: {color}")
        elif key == ord("2"):
            color = self.canvas.set_color(1)
            print(f"Color seleccionado: {color}")
        elif key == ord("3"):
            color = self.canvas.set_color(2)
            print(f"Color seleccionado: {color}")
        elif key == ord("4"):
            color = self.canvas.set_color(3)
            print(f"Color seleccionado: {color}")
        elif key == ord("t"):
            brush_type = self.brush_manager.next_type()
            print(f"Tipo de pincel: {brush_type}")
        elif key == ord("s"):
            brush_size = self.brush_manager.next_size()
            print(f"Tamaño de pincel: {brush_size}")
    
    def process_frame(self, frame):
        """
        Procesa un frame de la cámara.
        
        Args:
            frame: Frame capturado de la cámara
            
        Returns:
            bool: True si se detectó un gesto de dibujo
        """
        # Voltear horizontalmente para efecto espejo
        frame = cv2.flip(frame, 1)
        
        # Convertir a RGB para MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.gesture_detector.process_frame(rgb_frame)

        gesture_detected = False
        current_pinch = False
        current_pointer = None
        
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark
                # Actualizar estado de pinch y posición del índice (siempre)
                current_pinch = self.gesture_detector.is_pinch(landmarks)
                current_pointer = self.gesture_detector.get_index_tip_position(landmarks)

                if self.gesture_detector.is_drawing_gesture(landmarks):
                    gesture_detected = True
                    x, y = current_pointer
                    # Si el gesto acaba de comenzar, iniciar un nuevo trazo con la configuración actual
                    if not self._prev_gesture:
                        color_name = self.canvas.get_current_color_name()
                        brush_type = self.brush_manager.get_current_type_name()
                        brush_size = self.brush_manager.get_current_size()
                        self.canvas.start_stroke(color_name, brush_type, brush_size)

                    self.canvas.add_point(x, y)
                
                # Dibujar retroalimentación
                self.feedback.draw(frame, landmarks, gesture_detected)
        
        if not gesture_detected and self._prev_gesture:
            # Romper el trazo actual cuando el gesto terminó
            self.canvas.break_current_stroke()
        # Actualizar estado previo y guardar pointer/pinch para uso en UI
        self._prev_gesture = gesture_detected
        # self._prev_pinch se gestiona en _handle_pinch_selection, pero guardamos el último estado observado
        self._last_pointer = current_pointer
        self._last_pinch = current_pinch

        return frame, gesture_detected

    def _build_ui_items(self):
        """Construye una lista de elementos UI con sus rectángulos en coordenadas del canvas."""
        items = []
        x = UI_BOX_SPACING
        y = UI_TOP_PADDING

        # Colores
        for i, name in enumerate(COLOR_NAMES):
            rect = (x, y, UI_BOX_SIZE, UI_BOX_SIZE)
            items.append({'type': 'color', 'value': name, 'rect': rect, 'index': i})
            x += UI_BOX_SIZE + UI_BOX_SPACING

        # Borrador (herramienta)
        rect = (x, y, UI_BOX_SIZE, UI_BOX_SIZE)
        items.append({'type': 'tool', 'value': 'ERASER', 'rect': rect})
        x += UI_BOX_SIZE + UI_BOX_SPACING

        # Tipos de pincel (excluir ERASER si ya mostrado)
        for bt in BRUSH_TYPES:
            if bt == 'ERASER':
                continue
            rect = (x, y, UI_BOX_SIZE, UI_BOX_SIZE)
            items.append({'type': 'brush', 'value': bt, 'rect': rect})
            x += UI_BOX_SIZE + UI_BOX_SPACING

        # Tamaños
        for sz in BRUSH_SIZES:
            rect = (x, y, UI_BOX_SIZE, UI_BOX_SIZE)
            items.append({'type': 'size', 'value': sz, 'rect': rect})
            x += UI_BOX_SIZE + UI_BOX_SPACING

        return items

    def _get_item_at(self, ui_items, px, py):
        for it in ui_items:
            x, y, w, h = it['rect']
            if x <= px <= x + w and y <= py <= y + h:
                return it
        return None

    def _draw_ui_overlay(self, img, ui_items, pointer_norm, pinch):
        """Dibuja los recuadros UI sobre la imagen del canvas."""
        for it in ui_items:
            x, y, w, h = it['rect']
            if it['type'] == 'color':
                color_bgr = self.canvas.colors.get(it['value'], (200, 200, 200))
                cv2.rectangle(img, (x, y), (x + w, y + h), color_bgr, -1)
            else:
                # fondo gris para otros items
                cv2.rectangle(img, (x, y), (x + w, y + h), (240, 240, 240), -1)

            # borde
            cv2.rectangle(img, (x, y), (x + w, y + h), (50, 50, 50), 1)

            # etiqueta
            label = ''
            if it['type'] == 'tool' and it['value'] == 'ERASER':
                label = 'E'
            elif it['type'] == 'brush':
                label = it['value'][0]
            elif it['type'] == 'size':
                label = str(it['value'])
            elif it['type'] == 'color':
                label = ''

            if label:
                cv2.putText(img, label, (x + 6, y + h - 8), 0, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

        # Si hay pointer, dibujar indicador y resaltar hover
        if pointer_norm is not None:
            px = int(max(0, min(1, pointer_norm[0])) * self.canvas.width)
            py = int(max(0, min(1, pointer_norm[1])) * self.canvas.height)
            hover = self._get_item_at(ui_items, px, py)
            if hover is not None:
                x, y, w, h = hover['rect']
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 200, 255), 2)

            # pointer circle
            cv2.circle(img, (px, py), 6, (0, 0, 255) if pinch else (0, 255, 0), -1)

    def _apply_selection(self, item):
        if item is None:
            return
        if item['type'] == 'color':
            idx = item.get('index', 0)
            color = self.canvas.set_color(idx)
            print(f"Color seleccionado (UI): {color}")
        elif item['type'] == 'tool':
            val = item['value']
            # set brush type if exists
            if val in self.brush_manager.brush_types:
                self.brush_manager.current_type_index = self.brush_manager.brush_types.index(val)
                print(f"Herramienta seleccionada: {val}")
        elif item['type'] == 'brush':
            val = item['value']
            if val in self.brush_manager.brush_types:
                self.brush_manager.current_type_index = self.brush_manager.brush_types.index(val)
                print(f"Tipo de pincel seleccionado (UI): {val}")
        elif item['type'] == 'size':
            val = item['value']
            if val in self.brush_manager.brush_sizes:
                self.brush_manager.current_size_index = self.brush_manager.brush_sizes.index(val)
                print(f"Tamaño seleccionado (UI): {val}")

    def _handle_pinch_selection(self, ui_items):
        current_pinch = getattr(self, '_last_pinch', False)
        prev = getattr(self, '_prev_pinch', False)
        pointer = getattr(self, '_last_pointer', None)

        if pointer is None:
            # actualizar estado y salir
            self._prev_pinch = current_pinch
            return

        px = int(max(0, min(1, pointer[0])) * self.canvas.width)
        py = int(max(0, min(1, pointer[1])) * self.canvas.height)

        if current_pinch and not prev:
            # pinch iniciado -> guardar candidato
            candidate = self._get_item_at(ui_items, px, py)
            self._pinch_candidate = candidate
        elif not current_pinch and prev:
            # pinch liberado -> confirmar selección si es el mismo item
            current = self._get_item_at(ui_items, px, py)
            if self._pinch_candidate is not None and current is not None:
                # comparar por tipo+value
                if (self._pinch_candidate.get('type') == current.get('type') and
                        self._pinch_candidate.get('value') == current.get('value')):
                    self._apply_selection(current)
            self._pinch_candidate = None

        # actualizar estado
        self._prev_pinch = current_pinch
    
    def run(self):
        """Ejecuta el bucle principal de la aplicación."""
        self.print_instructions()
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Error al capturar frame de la cámara.")
                break
            
            # Procesar frame
            processed_frame, _ = self.process_frame(frame)
            
            # Renderizar canvas
            # Pasamos el manager para que Canvas use el pincel correcto por trazo
            self.canvas.render(self.brush_manager)
            
            # Dibujar UI encima del canvas y manejar selección por pinch
            ui_img = self.canvas.get_image().copy()
            ui_items = self._build_ui_items()
            self._draw_ui_overlay(ui_img, ui_items, self._last_pointer, getattr(self, '_last_pinch', False))

            # Manejar la lógica de selección: pinch start -> candidate, pinch release -> apply
            self._handle_pinch_selection(ui_items)

            # Mostrar ventanas
            cv2.imshow(TRACKING_WINDOW_NAME, processed_frame)
            cv2.imshow(PAINT_WINDOW_NAME, ui_img)
            
            # Procesar entrada de teclado
            self.process_keyboard_input()
        
        self.cleanup()
    
    def cleanup(self):
        """Limpia recursos antes de cerrar."""
        self.cap.release()
        cv2.destroyAllWindows()
        self.gesture_detector.close()
        print("Aplicación cerrada correctamente.")


def main():
    """Punto de entrada de la aplicación."""
    app = PaintApp()
    app.run()


if __name__ == "__main__":
    main()
