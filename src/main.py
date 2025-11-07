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
import argparse
import subprocess
import shutil
import time


def _list_directshow_devices_ffmpeg():
    """Intentar listar dispositivos DirectShow usando ffmpeg (solo Windows)."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return []
    try:
        p = subprocess.run([ffmpeg, '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'],
                           stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, timeout=3)
        out = p.stderr.splitlines()
        devices = []
        capture_section = False
        for line in out:
            if 'DirectShow video devices' in line:
                capture_section = True
                continue
            if capture_section:
                if 'DirectShow audio devices' in line:
                    break
                if '"' in line:
                    parts = line.split('"')
                    if len(parts) >= 2:
                        name = parts[1].strip()
                        if name:
                            devices.append(name)
        return devices
    except Exception:
        return []


def open_camera(preferred=None, try_range=8, wait_ms=300):
    """Abrir cámara de forma robusta en Windows.

    preferred: None, índice (int o string) o cadena tipo 'video=Nombre'
    """
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, None]

    def try_open(src, backend=None):
        try:
            if backend is None:
                cap = cv2.VideoCapture(src)
            else:
                cap = cv2.VideoCapture(src, backend)
        except Exception:
            try:
                cap = cv2.VideoCapture(src)
            except Exception:
                return None
        if not cap or not cap.isOpened():
            try:
                cap.release()
            except Exception:
                pass
            return None
        # validar que devuelve frames
        t0 = time.time()
        ok = False
        while time.time() - t0 < (wait_ms / 1000.0):
            ret, _ = cap.read()
            if ret:
                ok = True
                break
        if not ok:
            try:
                cap.release()
            except Exception:
                pass
            return None
        return cap

    # si prefieren dispositivo
    if preferred:
        try:
            idx = int(preferred)
            for b in backends:
                cap = try_open(idx, backend=b)
                if cap:
                    print(f"Cámara abierta: index={idx}, backend={b}")
                    return cap
        except ValueError:
            cand = preferred
            if not cand.lower().startswith("video=") and "video=" not in cand:
                cand = f'video={preferred}'
            for b in backends:
                cap = try_open(cand, backend=b)
                if cap:
                    print(f'Camera abierta: device="{cand}", backend={b}')
                    return cap
        print(f"No se pudo abrir la cámara solicitada: {preferred} - se intentará autodetección")

    # autodetección por índices
    for i in range(try_range):
        for b in backends:
            cap = try_open(i, backend=b)
            if cap:
                print(f"Cámara autodetectada: index={i}, backend={b}")
                return cap

    # intentar nombres via ffmpeg
    devices = _list_directshow_devices_ffmpeg()
    for name in devices:
        cand = f'video={name}'
        for b in backends:
            cap = try_open(cand, backend=b)
            if cap:
                print(f"Cámara abierta por nombre: {name} (DirectShow)")
                return cap

    # índices altos
    for i in range(try_range, try_range + 20):
        cap = try_open(i)
        if cap:
            print(f"Cámara detectada en índice alto: index={i}")
            return cap

    raise RuntimeError("No se pudo abrir ninguna cámara disponible.")


# parseo de argumentos simple (acepta --camera)
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--camera', '-c', help='Índice o "video=Nombre" (DirectShow).', default=None)
args, _unknown = parser.parse_known_args()


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

        # Inicializar control de voz (opcional). Import dinámico para evitar fallos si faltan dependencias.
        self.voice_listener = None
        self.voice_feedback = None
        try:
            from utils.voice_feedback import VoiceFeedback
            from utils.voice_listener import VoiceListener
            self.voice_feedback = VoiceFeedback()
            # command_callback será un método de la instancia
            self.voice_listener = VoiceListener(command_callback=self._on_voice_command, feedback=self.voice_feedback, language='es-ES')
            self.voice_listener.start()
            print("Voice control: listener started (Lumi).")
        except Exception:
            # Si falla importar o iniciar, seguimos sin control por voz
            self.voice_listener = None
            self.voice_feedback = None
        # Estado para confirmaciones visuales de voz
        self._last_voice_msg = None
        self._last_voice_time = 0.0
        
        # Abrir cámara (auto-detección o según --camera)
        try:
            self.cap = open_camera(preferred=args.camera, try_range=8)
        except Exception as e:
            print(f"Fallo al abrir cámara automática: {e}. Intentando cámara por defecto index 0")
            self.cap = cv2.VideoCapture(0)

        # Ajustar resolución deseada (si el dispositivo lo soporta)
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        except Exception:
            pass
        
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
                
                # Dibujar retroalimentación (pasamos modo actual para mostrarlo en TRACKING)
                mode_info = {
                    'tool': self.brush_manager.get_current_type_name(),
                    'color': self.canvas.get_current_color_name(),
                    'size': self.brush_manager.get_current_size()
                }
                self.feedback.draw(frame, landmarks, gesture_detected, mode_info)
        
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

            # etiqueta: usar etiquetas explícitas para evitar confusiones
            label = ''
            if it['type'] == 'tool' and it['value'] == 'ERASER':
                label = 'E'
            elif it['type'] == 'brush':
                # mapear nombres de pincel a letra clara
                brush_label_map = {
                    'LINEA': 'L',
                    'DAB': 'D',
                    'ERASER': 'E'
                }
                label = brush_label_map.get(it['value'], it['value'][0])
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

        # Mostrar estado de voz (discreto, parte inferior izquierda)
        try:
            vl = getattr(self, 'voice_listener', None)
            if vl is not None:
                if getattr(vl, 'state', 'passive') == 'active':
                    cv2.putText(img, "🎙 Lumi escuchando...", (10, self.canvas.height - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 220, 0), 2, cv2.LINE_AA)
                else:
                    cv2.putText(img, "🎙 Lumi", (10, self.canvas.height - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)
        except Exception:
            pass

        # Mensaje visual transitorio de confirmación por voz (3s)
        try:
            if getattr(self, '_last_voice_msg', None) and (time.time() - getattr(self, '_last_voice_time', 0)) < 3.0:
                msg = self._last_voice_msg
                # fondo semitransparente (simulado con rect opaco)
                (tw, th), _ = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                pad = 12
                x2 = self.canvas.width - 10
                y2 = 30
                x1 = x2 - (tw + pad)
                y1 = y2 - (th + pad//2)
                # rectángulo de fondo
                cv2.rectangle(img, (x1, 5), (x2, y2 + 6), (30, 30, 30), -1)
                cv2.putText(img, msg, (x1 + 8, y2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 220, 220), 2, cv2.LINE_AA)
        except Exception:
            pass

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
            # pinch liberado -> confirmar selección del candidato guardado (si existe)
            if self._pinch_candidate is not None:
                self._apply_selection(self._pinch_candidate)
            self._pinch_candidate = None

        # actualizar estado
        self._prev_pinch = current_pinch

    def _on_voice_command(self, text):
        """Handler de comandos reconocidos por voz.

        Recibe el texto y aplica acciones: color, herramienta, tamaño, limpiar, salir.
        Debe devolver un string con la respuesta que se hablará (o None).
        """
        if not text:
            return None
        t = text.lower()

        # mapa sencillo de colores
        color_map = {
            'azul': 'AZUL', 'verde': 'VERDE', 'rojo': 'ROJO', 'amarillo': 'AMARILLO',
            'negro': 'NEGRO', 'blanco': 'BLANCO', 'púrpura': 'PURPURA', 'purpura': 'PURPURA', 'morado': 'PURPURA', 'naranja': 'NARANJA'
        }

        for k, cname in color_map.items():
            if f"color {k}" in t or t.strip() == k or (t.startswith('cambiar a') and k in t):
                try:
                    idx = COLOR_NAMES.index(cname)
                    self.canvas.set_color(idx)
                    resp = f"Color {k} activado"
                    self._last_voice_msg = resp
                    self._last_voice_time = time.time()
                    return resp
                except ValueError:
                    resp = f"No encuentro el color {k}"
                    self._last_voice_msg = resp
                    self._last_voice_time = time.time()
                    return resp

        # herramientas
        if 'borrador' in t or 'eraser' in t:
            if 'ERASER' in self.brush_manager.brush_types:
                self.brush_manager.current_type_index = self.brush_manager.brush_types.index('ERASER')
                resp = 'Modo borrador activado'
                self._last_voice_msg = resp
                self._last_voice_time = time.time()
                return resp
        if 'línea' in t or 'linea' in t:
            if 'LINEA' in self.brush_manager.brush_types:
                self.brush_manager.current_type_index = self.brush_manager.brush_types.index('LINEA')
                resp = 'Pincel línea activado'
                self._last_voice_msg = resp
                self._last_voice_time = time.time()
                return resp
        if 'dab' in t or 'punteado' in t:
            if 'DAB' in self.brush_manager.brush_types:
                self.brush_manager.current_type_index = self.brush_manager.brush_types.index('DAB')
                resp = 'Pincel punteado activado'
                self._last_voice_msg = resp
                self._last_voice_time = time.time()
                return resp

        # grosores
        if 'peque' in t or 'fino' in t:
            self.brush_manager.current_size_index = 0
            resp = 'Grosor fino'
            self._last_voice_msg = resp
            self._last_voice_time = time.time()
            return resp
        if 'medio' in t or 'mediano' in t:
            self.brush_manager.current_size_index = 1 if len(self.brush_manager.brush_sizes) > 1 else 0
            resp = 'Grosor medio'
            self._last_voice_msg = resp
            self._last_voice_time = time.time()
            return resp
        if 'grande' in t or 'gordo' in t or 'grueso' in t:
            self.brush_manager.current_size_index = max(0, len(self.brush_manager.brush_sizes) - 1)
            resp = 'Grosor grande'
            self._last_voice_msg = resp
            self._last_voice_time = time.time()
            return resp

        # limpiar / salir
        if 'limpiar' in t or 'borrar todo' in t or 'borrar lienzo' in t:
            self.canvas.clear()
            resp = 'Lienzo borrado'
            self._last_voice_msg = resp
            self._last_voice_time = time.time()
            return resp
        if 'salir' in t or 'cerrar' in t or 'terminar' in t:
            self.running = False
            resp = 'Cerrando la aplicación'
            self._last_voice_msg = resp
            self._last_voice_time = time.time()
            return resp

        resp = 'No entendí el comando'
        self._last_voice_msg = resp
        self._last_voice_time = time.time()
        return resp

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
        # detener voice listener si existe
        try:
            if getattr(self, 'voice_listener', None):
                try:
                    self.voice_listener.stop()
                except Exception:
                    pass
            if getattr(self, 'voice_feedback', None):
                try:
                    self.voice_feedback.stop()
                except Exception:
                    pass
        except Exception:
            pass
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
