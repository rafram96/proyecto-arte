"""
Canvas o lienzo digital para pintura.
"""

import cv2
import numpy as np
from collections import deque
from .config import MAX_POINTS_PER_STROKE, SMOOTHING_ALPHA, ERASER_DISTANCE_THRESHOLD
import math


class Canvas:
    """Gestiona el lienzo de pintura y los trazos."""
    
    def __init__(self, width, height, colors):
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
        # Vista (offset en coordenadas normalizadas y escala)
        # view_offset describe la esquina superior izquierda en coordenadas normalizadas
        self.view_offset = (0.0, 0.0)
        self.view_scale = 1.0
    
    def clear(self):
        """Borra todo el lienzo y reinicia los trazos."""
        self.image = np.zeros((self.height, self.width, 3), dtype=np.uint8) + 255
        self.strokes = []
        self.current_stroke = None
    
    def add_point(self, normalized_x, normalized_y):
        """
        Añade un punto al trazo actual.
        
        Args:
            normalized_x: Coordenada X normalizada (0-1)
            normalized_y: Coordenada Y normalizada (0-1)
        """
        paint_x = int(normalized_x * self.width)
        paint_y = int(normalized_y * self.height)
    # Nota: almacenamos puntos en coordenadas del mundo (normalizadas), no en píxeles
        
        # Si no hay trazo actual, crear uno con las propiedades actuales
        if self.current_stroke is None:
            # Crear trazo con propiedades por defecto (será completado por start_stroke si es necesario)
            color_name = self.color_names[self.current_color_index]
            self.start_stroke(color_name, 'LINEA', self.width // 200 or 2)

        # Guardar en coordenadas de mundo (normalizadas) y aplicar suavizado simple
        pts = self.current_stroke['points']
        world_point = (float(normalized_x), float(normalized_y))
        if len(pts) > 0:
            last = pts[0]
            smoothed_x = last[0] * (1 - SMOOTHING_ALPHA) + world_point[0] * SMOOTHING_ALPHA
            smoothed_y = last[1] * (1 - SMOOTHING_ALPHA) + world_point[1] * SMOOTHING_ALPHA
            smoothed = (smoothed_x, smoothed_y)
            pts.appendleft(smoothed)
        else:
            pts.appendleft(world_point)
    
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
        self.current_stroke = None
    
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
            # Mapear puntos de mundo (normalizados) a coordenadas de pantalla
            screen_pts = []
            ox, oy = self.view_offset
            s = self.view_scale
            for p in pts:
                sx = int((p[0] - ox) * s * self.width)
                sy = int((p[1] - oy) * s * self.height)
                screen_pts.append((sx, sy))

            for k in range(1, len(screen_pts)):
                p1 = screen_pts[k - 1]
                p2 = screen_pts[k]
                brush.draw(self.image, p1, p2, color_bgr)

        # Visualizar la marca del borrador: dibujar círculos semi-transparentes donde pasaron los trazos de borrador
        if eraser_strokes:
            overlay = self.image.copy()
            ox, oy = self.view_offset
            s = self.view_scale
            for es in eraser_strokes:
                radius = max(1, int(es.get('brush_size', 8)))
                for p in es['points']:
                    # Mapear punto mundo->pantalla
                    x = int((p[0] - ox) * s * self.width)
                    y = int((p[1] - oy) * s * self.height)
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

        # Convertir puntos de mundo a pantalla para medir en píxeles
        ox, oy = self.view_offset
        s = self.view_scale
        thr2 = threshold * threshold
        for p1 in pts1:
            x1 = (p1[0] - ox) * s * self.width
            y1 = (p1[1] - oy) * s * self.height
            for p2 in pts2:
                x2 = (p2[0] - ox) * s * self.width
                y2 = (p2[1] - oy) * s * self.height
                dx = x1 - x2
                dy = y1 - y2
                if dx * dx + dy * dy <= thr2:
                    return True
        return False

    # Métodos de vista: pan y zoom
    def pan(self, delta_world_x, delta_world_y):
        """Mueve la vista en coordenadas del mundo (normalizadas)."""
        ox, oy = self.view_offset
        self.view_offset = (ox + float(delta_world_x), oy + float(delta_world_y))

    def zoom(self, factor, center_world=None, min_scale=0.2, max_scale=6.0):
        """Hace zoom respecto a un punto del mundo (center_world en coordenadas normalizadas).

        factor > 1 -> zoom in; factor < 1 -> zoom out
        """
        if factor <= 0:
            return
        if center_world is None:
            center_world = (self.view_offset[0] + 0.5 / self.view_scale, self.view_offset[1] + 0.5 / self.view_scale)

        # Convertir para mantener el center_world fijo en pantalla
        ox, oy = self.view_offset
        cx, cy = center_world
        new_scale = max(min_scale, min(max_scale, self.view_scale * factor))
        # Ajustar offset para que el punto center_world permanezca en el mismo lugar de pantalla
        # pantalla = (world - ox) * s -> ox' = world - pantalla / s'
        self.view_offset = (
            cx - (cx - ox) * (self.view_scale / new_scale),
            cy - (cy - oy) * (self.view_scale / new_scale)
        )
        self.view_scale = new_scale
