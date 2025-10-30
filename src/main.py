"""
Aplicación principal de pintura con gestos.
"""

import cv2
from core.config import (
    PAINT_WINDOW_WIDTH, PAINT_WINDOW_HEIGHT, PAINT_WINDOW_NAME,
    CAMERA_WIDTH, CAMERA_HEIGHT, TRACKING_WINDOW_NAME,
    COLORS, COLOR_NAMES, BRUSH_TYPES, BRUSH_SIZES
)
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

        cv2.namedWindow(PAINT_WINDOW_NAME, cv2.WINDOW_AUTOSIZE)

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        
        self.running = True
    
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
        print("Los dedos corazón, anular y meñique deben estar flexionados hacia la palma.")
        print("Observa el feedback visual en la ventana 'Tracking' para ajustar tu mano.")
        print("=" * 80)
    
    def process_keyboard_input(self):
        """Procesa la entrada del teclado."""
        key = cv2.waitKey(1) & 0xFF

        # Debug: mostrar código de tecla cuando se detecta alguna pulsación
        if key != 255:
            try:
                print(f"Tecla pulsada: code={key} char={chr(key)}")
            except Exception:
                print(f"Tecla pulsada: code={key}")
        
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
        # Soportar 'b' minúscula y mayúscula para seleccionar color blanco (o quinto color)
        elif key in (ord("b"), ord("B")):
            color = self.canvas.set_color(4)
            print(f"Color seleccionado: {color}")
        elif key == ord("e"):
            # Activar borrador (si está disponible en la configuración)
            brush_type = self.brush_manager.set_type('BORRADOR')
            if brush_type:
                print("Modo borrador activado.")
            else:
                print("Borrador no disponible en BRUSH_TYPES.")
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
        
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark
                
                if self.gesture_detector.is_drawing_gesture(landmarks):
                    gesture_detected = True
                    x, y = self.gesture_detector.get_index_tip_position(landmarks)
                    # Pasar el gestor de pinceles para que el canvas guarde el pincel usado
                    self.canvas.add_point(x, y, self.brush_manager)
                
                # Dibujar retroalimentación
                self.feedback.draw(frame, landmarks, gesture_detected)
        
        if not gesture_detected:
            # Romper el trazo actual cuando no hay gesto
            self.canvas.break_current_stroke()
        
        return frame, gesture_detected
    
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
            # Pasar el gestor de pinceles al canvas para que asigne pinceles a cada trazo
            self.canvas.render(self.brush_manager)
            
            # Mostrar ventanas
            cv2.imshow(TRACKING_WINDOW_NAME, processed_frame)
            cv2.imshow(PAINT_WINDOW_NAME, self.canvas.get_image())
            
            # Procesar entrada de teclado
            self.process_keyboard_input()
        
        self.cleanup()
    
    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.gesture_detector.close()
        print("Aplicación cerrada correctamente.")


def main():
    app = PaintApp()
    app.run()


if __name__ == "__main__":
    main()
