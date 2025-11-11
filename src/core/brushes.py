"""
Sistema de pinceles para diferentes efectos artísticos.
"""

import cv2
import numpy as np
import random
from abc import ABC, abstractmethod
from .config import DAB_JITTER_ENABLED


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

    def __init__(self, size, jitter=True):
        super().__init__(size)
        self.jitter = jitter

    def _rng(self, p1, p2, step):
        if self.jitter:
            return random
        seed = f"{p1[0]}_{p1[1]}_{p2[0]}_{p2[1]}_{step}_{self.size}"
        return random.Random(seed)

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
            
            rng = self._rng(p1, p2, step)
            offset_x = rng.randint(-self.size // 2, self.size // 2)
            offset_y = rng.randint(-self.size // 2, self.size // 2)

            random_radius_offset = rng.randint(-self.size // 3, self.size // 3)
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

        self._last_paint_type_index = self._find_first_paint_index()
        self.dab_jitter_enabled = DAB_JITTER_ENABLED

        default_size = 10
        if default_size in self.brush_sizes:
            self.current_size_index = self.brush_sizes.index(default_size)
        else:
            self.current_size_index = 0
        self._brushes = {
            'LINEA': LineBrush,
            'DAB': DabBrush
        }

        # Registrar borrador si está declarado en tipos
        if 'ERASER' in self.brush_types:
            self._brushes['ERASER'] = EraserBrush

    def _find_first_paint_index(self):
        for idx, name in enumerate(self.brush_types):
            if name != 'ERASER':
                return idx
        return 0
    
    def get_current_brush(self):
        """Retorna el pincel actual configurado."""
        brush_type = self.brush_types[self.current_type_index]
        brush_size = self.brush_sizes[self.current_size_index]
        brush_class = self._brushes.get(brush_type, LineBrush)
        if brush_class is DabBrush:
            return brush_class(brush_size, jitter=self.dab_jitter_enabled)
        return brush_class(brush_size)

    def get_brush_by_name(self, brush_type, brush_size):
        """Retorna una instancia de pincel por nombre y tamaño."""
        brush_class = self._brushes.get(brush_type, LineBrush)
        if brush_class is DabBrush:
            return brush_class(brush_size, jitter=self.dab_jitter_enabled)
        return brush_class(brush_size)
    
    def next_type(self):
        """Cambia al siguiente tipo de pincel."""
        self.current_type_index = (self.current_type_index + 1) % len(self.brush_types)
        if self.get_current_type_name() != 'ERASER':
            self._last_paint_type_index = self.current_type_index
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

    def set_type_by_name(self, brush_type):
        """Selecciona un tipo de pincel específico por nombre."""
        if brush_type in self.brush_types:
            self.current_type_index = self.brush_types.index(brush_type)
            if brush_type != 'ERASER':
                self._last_paint_type_index = self.current_type_index
        return self.get_current_type_name()

    def ensure_paint_brush(self):
        """Garantiza que el pincel activo sea uno que pinte (no borrador)."""
        if self.get_current_type_name() == 'ERASER':
            self.current_type_index = self._last_paint_type_index
        return self.get_current_type_name()

    def set_dab_jitter(self, enabled: bool):
        """Permite activar/desactivar el jitter aleatorio del pincel DAB."""
        self.dab_jitter_enabled = bool(enabled)
