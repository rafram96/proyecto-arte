"""
Canvas o lienzo digital para pintura.
"""

import cv2
import numpy as np
from collections import deque
from .config import MAX_POINTS_PER_STROKE


class Stroke:
    """Almacena las propiedades de un único trazo."""
    def __init__(self, color, brush):
        self.points = deque(maxlen=MAX_POINTS_PER_STROKE)
        self.color = color
        self.brush = brush

class Canvas:
    """Gestiona el lienzo de pintura y los trazos."""
    
    def __init__(self, width, height, colors):
        self.width = width
        self.height = height
        self.colors = colors
        self.color_names = list(colors.keys())
        self.current_color_index = 0
        
        # Canvas principal
        self.image = np.zeros((height, width, 3), dtype=np.uint8) + 255
        
        # Almacenamiento de trazos
        self.strokes = [Stroke(self.get_current_color_bgr(), None)] # El pincel se asignará en render
        self.current_stroke_index = 0

    def clear(self):
        """Borra todo el lienzo y reinicia los trazos."""
        self.image = np.zeros((self.height, self.width, 3), dtype=np.uint8) + 255
        self.strokes = [Stroke(self.get_current_color_bgr(), None)]
        self.current_stroke_index = 0

    def add_point(self, normalized_x, normalized_y, brush_manager=None):
        """
        Añade un punto al trazo actual. Si el trazo no tiene pincel asignado,
        lo toma del `brush_manager` (si se proporciona) para que cada trazo
        mantenga su estilo independiente.
        
        Args:
            normalized_x: Coordenada X normalizada (0-1)
            normalized_y: Coordenada Y normalizada (0-1)
            brush_manager: (opcional) instancia de BrushManager para obtener el pincel actual
        """
        paint_x = int(normalized_x * self.width)
        paint_y = int(normalized_y * self.height)
        point = (paint_x, paint_y)

        # Asignar pincel y color al trazo en cuanto empieza si se pasó el gestor
        current_stroke = self.strokes[self.current_stroke_index]
        if current_stroke.brush is None and brush_manager is not None:
            current_stroke.brush = brush_manager.get_current_brush()
            current_stroke.color = self.get_current_color_bgr()

        current_stroke.points.appendleft(point)

    def break_current_stroke(self):
        """Rompe el trazo actual para comenzar uno nuevo."""
        if len(self.strokes[self.current_stroke_index].points) > 0:
            new_stroke = Stroke(self.get_current_color_bgr(), None)
            self.strokes.append(new_stroke)
            self.current_stroke_index += 1

    def render(self, brush_manager):
        """
        Renderiza todos los trazos en el canvas.
        
        Args:
            brush_manager: Instancia de BrushManager para obtener los pinceles.
        """
        # Limpiar canvas
        self.image = np.zeros((self.height, self.width, 3), dtype=np.uint8) + 255
        
        # Asignar el pincel actual al trazo en curso si aún no lo tiene
        if self.strokes[self.current_stroke_index].brush is None:
            self.strokes[self.current_stroke_index].brush = brush_manager.get_current_brush()
            self.strokes[self.current_stroke_index].color = self.get_current_color_bgr()

        # Dibujar todos los trazos
        for stroke in self.strokes:
            brush = stroke.brush
            color = stroke.color
            
            # Si un trazo antiguo no tiene pincel, usar el actual
            if brush is None:
                brush = brush_manager.get_current_brush()

            if brush.style == 'eraser':
                color = (255, 255, 255) # Color de fondo para borrar

            for k in range(1, len(stroke.points)):
                p1 = stroke.points[k - 1]
                p2 = stroke.points[k]
                brush.draw(self.image, p1, p2, color)

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
