"""
Sistema de pinceles para diferentes efectos artísticos.
"""

import cv2
import numpy as np
import random
from abc import ABC, abstractmethod


class Brush(ABC):
    """Clase base abstracta para pinceles."""
    
    def __init__(self, size):
        self.size = size
    
    @abstractmethod
    def draw(self, canvas, p1, p2, color):
        """
        Dibuja en el canvas desde p1 hasta p2.
        
        Args:
            canvas: Imagen donde dibujar
            p1: Punto inicial (x, y)
            p2: Punto final (x, y)
            color: Color BGR
        """
        pass


class LineBrush(Brush):
    """Pincel de línea continua."""
    
    def draw(self, canvas, p1, p2, color):
        if p1 is None or p2 is None:
            return
        cv2.line(canvas, p1, p2, color, self.size)


class DabBrush(Brush):
    """Pincel con efecto impresionista (dabs)."""
    
    def draw(self, canvas, p1, p2, color):
        if p1 is None or p2 is None:
            return
        
        distance = np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
        num_dabs = max(1, int(distance / (self.size * 1.5)))
        
        canvas_height, canvas_width = canvas.shape[:2]
        
        for step in range(num_dabs):
            alpha = step / num_dabs if num_dabs > 0 else 0
            dab_x = int(p1[0] * (1 - alpha) + p2[0] * alpha)
            dab_y = int(p1[1] * (1 - alpha) + p2[1] * alpha)
            
            offset_x = random.randint(-self.size // 2, self.size // 2)
            offset_y = random.randint(-self.size // 2, self.size // 2)
            
            random_radius_offset = random.randint(-self.size // 3, self.size // 3)
            dab_radius = max(1, self.size + random_radius_offset)
            
            final_dab_x = max(0, min(canvas_width - 1, dab_x + offset_x))
            final_dab_y = max(0, min(canvas_height - 1, dab_y + offset_y))
            
            cv2.circle(canvas, (final_dab_x, final_dab_y), dab_radius, color, -1)


class EraserBrush(Brush):
    """Pincel borrador — no dibuja, el borrado se maneja a nivel de Canvas.

    Implementamos un draw no-op para compatibilidad con la interfaz.
    """

    def draw(self, canvas, p1, p2, color):
        # El borrador no pinta aquí; la lógica de eliminación la gestiona Canvas
        return


class BrushManager:
    """Gestiona los diferentes tipos de pinceles."""
    
    def __init__(self, brush_types, brush_sizes):
        self.brush_types = brush_types
        self.brush_sizes = brush_sizes
        self.current_type_index = 0
        self.current_size_index = 0
        self._brushes = {
            'LINEA': LineBrush,
            'DAB': DabBrush
        }

        # Registrar borrador si está declarado en tipos
        if 'ERASER' in self.brush_types:
            self._brushes['ERASER'] = EraserBrush
    
    def get_current_brush(self):
        """Retorna el pincel actual configurado."""
        brush_type = self.brush_types[self.current_type_index]
        brush_size = self.brush_sizes[self.current_size_index]
        brush_class = self._brushes.get(brush_type, LineBrush)
        return brush_class(brush_size)

    def get_brush_by_name(self, brush_type, brush_size):
        """Retorna una instancia de pincel por nombre y tamaño."""
        brush_class = self._brushes.get(brush_type, LineBrush)
        return brush_class(brush_size)
    
    def next_type(self):
        """Cambia al siguiente tipo de pincel."""
        self.current_type_index = (self.current_type_index + 1) % len(self.brush_types)
        return self.get_current_type_name()
    
    def next_size(self):
        """Cambia al siguiente tamaño de pincel."""
        self.current_size_index = (self.current_size_index + 1) % len(self.brush_sizes)
        return self.get_current_size()
    
    def get_current_type_name(self):
        """Retorna el nombre del tipo de pincel actual."""
        return self.brush_types[self.current_type_index]
    
    def get_current_size(self):
        """Retorna el tamaño actual del pincel."""
        return self.brush_sizes[self.current_size_index]
