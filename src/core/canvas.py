"""
Canvas o lienzo digital para pintura.
"""

import cv2
import numpy as np
from collections import deque
from .config import MAX_POINTS_PER_STROKE


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
        
        # Almacenamiento de trazos por color
        self.strokes = {color_name: [deque(maxlen=MAX_POINTS_PER_STROKE)] 
                       for color_name in self.color_names}
        self.stroke_indices = {color_name: 0 for color_name in self.color_names}
    
    def clear(self):
        """Borra todo el lienzo y reinicia los trazos."""
        self.image = np.zeros((self.height, self.width, 3), dtype=np.uint8) + 255
        self.strokes = {color_name: [deque(maxlen=MAX_POINTS_PER_STROKE)] 
                       for color_name in self.color_names}
        self.stroke_indices = {color_name: 0 for color_name in self.color_names}
    
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
        
        current_color = self.color_names[self.current_color_index]
        current_index = self.stroke_indices[current_color]
        self.strokes[current_color][current_index].appendleft(point)
    
    def break_current_stroke(self):
        """Rompe el trazo actual para comenzar uno nuevo."""
        for color_name in self.color_names:
            current_index = self.stroke_indices[color_name]
            if len(self.strokes[color_name][current_index]) != 0:
                self.strokes[color_name].append(deque(maxlen=MAX_POINTS_PER_STROKE))
                self.stroke_indices[color_name] += 1
    
    def render(self, brush):
        """
        Renderiza todos los trazos en el canvas usando el pincel especificado.
        
        Args:
            brush: Instancia de Brush para dibujar
        """
        # Limpiar canvas
        self.image = np.zeros((self.height, self.width, 3), dtype=np.uint8) + 255
        
        # Dibujar todos los trazos
        for color_name in self.color_names:
            color_bgr = self.colors[color_name]
            
            for stroke in self.strokes[color_name]:
                for k in range(1, len(stroke)):
                    p1 = stroke[k - 1]
                    p2 = stroke[k]
                    brush.draw(self.image, p1, p2, color_bgr)
    
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
