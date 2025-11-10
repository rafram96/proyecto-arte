"""
Canvas o lienzo digital para pintura.
"""

import cv2
import numpy as np
from collections import deque
from .config import MAX_POINTS_PER_STROKE, SMOOTHING_ALPHA, ERASER_DISTANCE_THRESHOLD
import math
import json
import time
import os


class Canvas:
    """Gestiona el lienzo de pintura y los trazos."""
    
    def __init__(self, width, height, colors, auto_save_file="canvas_state.json"):
        self.width = width
        self.height = height
        self.colors = colors
        self.color_names = list(colors.keys())
        self.current_color_index = 0
        # Canvas principal
        self.image = np.zeros((self.height, self.width, 3), dtype=np.uint8) + 255

        # Almacenamiento de trazos como lista de objetos
        # Cada trazo: {'points': deque, 'color': str, 'brush_type': str, 'brush_size': int}
        self.strokes = []
        self.current_stroke = None
        
        # Auto-guardado en tiempo real
        self.auto_save_file = auto_save_file
        self._save_to_file()
    
    def clear(self):
        """Borra todo el lienzo y reinicia los trazos."""
        self.image = np.zeros((self.height, self.width, 3), dtype=np.uint8) + 255
        self.strokes = []
        self.current_stroke = None
        self._save_to_file()  # Guardar estado vacío
    
    def add_point(self, normalized_x, normalized_y):
        """
        Añade un punto al trazo actual.
        
        Args:
            normalized_x: Coordenada X normalizada (0-1)
            normalized_y: Coordenada Y normalizada (0-1)
        """
        paint_x = int(normalized_x * self.width)
        paint_y = int(normalized_y * self.height)
        point = (paint_x, paint_y)
        
        # Si no hay trazo actual, crear uno con las propiedades actuales
        if self.current_stroke is None:
            # Crear trazo con propiedades por defecto (será completado por start_stroke si es necesario)
            color_name = self.color_names[self.current_color_index]
            self.start_stroke(color_name, 'LINEA', self.width // 200 or 2)

        # Aplicar suavizado simple: promedio entre último punto y nuevo
        pts = self.current_stroke['points']
        if len(pts) > 0:
            last = pts[0]
            smoothed_x = int(last[0] * (1 - SMOOTHING_ALPHA) + point[0] * SMOOTHING_ALPHA)
            smoothed_y = int(last[1] * (1 - SMOOTHING_ALPHA) + point[1] * SMOOTHING_ALPHA)
            smoothed = (smoothed_x, smoothed_y)
            pts.appendleft(smoothed)
        else:
            pts.appendleft(point)
        
        # Guardar en tiempo real después de añadir punto
        self._save_to_file()
    
    def break_current_stroke(self):
        """Termina el trazo actual."""
        self.end_stroke()

    def start_stroke(self, color_name, brush_type, brush_size):
        """Comienza un nuevo trazo con propiedades específicas."""
        stroke = {
            'points': deque(maxlen=MAX_POINTS_PER_STROKE),
            'color': color_name,
            'brush_type': brush_type,
            'brush_size': brush_size
        }
        self.strokes.append(stroke)
        self.current_stroke = stroke

    def end_stroke(self):
        """Finaliza el trazo actual (si existe)."""
        if self.current_stroke is None:
            return

        if self.current_stroke.get('brush_type') == 'ERASER':
            eraser_stroke = self.current_stroke
            cleaned_strokes = []
            threshold = eraser_stroke.get('brush_size', 0) + ERASER_DISTANCE_THRESHOLD

            for stroke in self.strokes:
                if stroke is eraser_stroke:
                    continue
                if stroke.get('brush_type') == 'ERASER':
                    # Cualquier borrador previo ya debería haber actuado; omitirlo.
                    continue
                if self._stroke_intersects(stroke['points'], eraser_stroke['points'], threshold):
                    continue
                cleaned_strokes.append(stroke)

            self.strokes = cleaned_strokes
        else:
            # Asegurar que el trazo actual queda en la lista de trazos finales
            if self.current_stroke not in self.strokes:
                self.strokes.append(self.current_stroke)

        self.current_stroke = None
        self._save_to_file()  # Guardar al finalizar trazo
    
    def render(self, brush_manager):
        """
        Renderiza todos los trazos en el canvas usando los pinceles indicados por cada trazo.

        Args:
            brush_manager: Instancia de BrushManager para obtener pinceles por nombre y tamaño
        """
        # Limpiar canvas
        self.image = np.zeros((self.height, self.width, 3), dtype=np.uint8) + 255

        # Primero procesar borradores para eliminar trazos (si los hay)
        # Recorrer una copia porque podemos eliminar elementos
        remaining = []
        eraser_strokes = [s for s in self.strokes if s['brush_type'] == 'ERASER']
        normal_strokes = [s for s in self.strokes if s['brush_type'] != 'ERASER']

        # Si hay borradores, marcar qué trazos normales eliminar
        to_remove = set()
        for e_idx, es in enumerate(eraser_strokes):
            for n_idx, ns in enumerate(normal_strokes):
                if self._stroke_intersects(ns['points'], es['points'], es['brush_size'] + ERASER_DISTANCE_THRESHOLD):
                    to_remove.add(id(ns))

        for ns in normal_strokes:
            if id(ns) in to_remove:
                continue
            remaining.append(ns)

        # Mantener también los trazos de borrador (no se dibujan)
        # (Si quisieras visualizarlos, podrías pintarlos aquí con color de fondo.)

        # Dibujar trazos restantes
        for stroke in remaining:
            color_bgr = self.colors.get(stroke['color'], (0, 0, 0))
            brush = brush_manager.get_brush_by_name(stroke['brush_type'], stroke['brush_size'])
            pts = stroke['points']
            for k in range(1, len(pts)):
                p1 = pts[k - 1]
                p2 = pts[k]
                brush.draw(self.image, p1, p2, color_bgr)

        # Visualizar la marca del borrador: dibujar círculos semi-transparentes donde pasaron los trazos de borrador
        if eraser_strokes:
            overlay = self.image.copy()
            for es in eraser_strokes:
                radius = max(1, int(es.get('brush_size', 8)))
                for p in es['points']:
                    # Asegurar que el punto está dentro de la imagen
                    x, y = int(p[0]), int(p[1])
                    if 0 <= x < self.width and 0 <= y < self.height:
                        cv2.circle(overlay, (x, y), radius, (255, 255, 255), -1)

            # Mezclar overlay con la imagen para crear efecto semitransparente
            alpha = 0.75
            cv2.addWeighted(overlay, alpha, self.image, 1 - alpha, 0, self.image)
    
    def set_color(self, color_index):
        """
        Cambia el color actual.
        
        Args:
            color_index: Índice del color en la lista de colores
        """
        if 0 <= color_index < len(self.color_names):
            self.current_color_index = color_index
            return self.color_names[color_index]
        return None
    
    def get_current_color_name(self):
        """Retorna el nombre del color actual."""
        return self.color_names[self.current_color_index]
    
    def get_current_color_bgr(self):
        """Retorna el color BGR actual."""
        return self.colors[self.color_names[self.current_color_index]]
    
    def get_image(self):
        """Retorna la imagen del canvas."""
        return self.image

    def _stroke_intersects(self, pts1, pts2, threshold):
        """Comprueba si algún punto de pts1 está a distancia < threshold de algún punto de pts2.

        Args:
            pts1, pts2: deque u iterable de tuplas (x,y)
            threshold: distancia en píxeles

        Returns:
            True si hay intersección (cercanía), False en caso contrario.
        """
        if not pts1 or not pts2:
            return False

        thr2 = threshold * threshold
        for p1 in pts1:
            for p2 in pts2:
                dx = p1[0] - p2[0]
                dy = p1[1] - p2[1]
                if dx * dx + dy * dy <= thr2:
                    return True
        return False
    
    def _save_to_file(self):
        """Guarda el estado actual del canvas en tiempo real al archivo JSON."""
        strokes_data = []
        
        for stroke in self.strokes:
            # Convertir cada punto del trazo
            points = list(stroke['points'])
            for point in points:
                strokes_data.append({
                    'x': int(point[0]),
                    'y': int(point[1]),
                    'color': stroke['color'],
                    'brush_type': stroke['brush_type'],
                    'brush_size': stroke['brush_size'],
                    'time': time.time()
                })
        
        # Guardar en archivo
        data = {'strokes': strokes_data}
        try:
            with open(self.auto_save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error guardando estado: {e}")
    
    def delete_save_file(self):
        """Elimina el archivo de guardado automático al cerrar el programa."""
        try:
            if os.path.exists(self.auto_save_file):
                os.remove(self.auto_save_file)
        except Exception as e:
            print(f"Error eliminando archivo de guardado: {e}")
