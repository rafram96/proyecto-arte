"""
Tests unitarios para los componentes de la aplicación.
"""

import unittest
import numpy as np
import sys
import os

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.brushes import LineBrush, DabBrush, BrushManager
from core.canvas import Canvas
from core.config import COLORS, COLOR_NAMES, BRUSH_TYPES, BRUSH_SIZES


class TestBrushes(unittest.TestCase):
    """Tests para el sistema de pinceles."""
    
    def setUp(self):
        self.canvas = np.zeros((100, 100, 3), dtype=np.uint8) + 255
    
    def test_line_brush_draws(self):
        """Verifica que LineBrush dibuja correctamente."""
        brush = LineBrush(size=2)
        p1 = (10, 10)
        p2 = (50, 50)
        color = (255, 0, 0)
        
        brush.draw(self.canvas, p1, p2, color)
        
        # Verificar que el canvas cambió
        self.assertFalse(np.all(self.canvas == 255))
    
    def test_dab_brush_draws(self):
        """Verifica que DabBrush dibuja correctamente."""
        brush = DabBrush(size=5)
        p1 = (10, 10)
        p2 = (50, 50)
        color = (0, 255, 0)
        
        brush.draw(self.canvas, p1, p2, color)
        
        # Verificar que el canvas cambió
        self.assertFalse(np.all(self.canvas == 255))
    
    def test_brush_manager_switches_type(self):
        """Verifica que BrushManager cambia de tipo correctamente."""
        manager = BrushManager(BRUSH_TYPES, BRUSH_SIZES)
        
        initial_type = manager.get_current_type_name()
        self.assertEqual(initial_type, "LINEA")
        
        next_type = manager.next_type()
        self.assertEqual(next_type, "DAB")
    
    def test_brush_manager_switches_size(self):
        """Verifica que BrushManager cambia de tamaño correctamente."""
        manager = BrushManager(BRUSH_TYPES, BRUSH_SIZES)
        
        initial_size = manager.get_current_size()
        self.assertEqual(initial_size, 2)
        
        next_size = manager.next_size()
        self.assertEqual(next_size, 5)


class TestCanvas(unittest.TestCase):
    """Tests para el Canvas."""
    
    def setUp(self):
        self.canvas = Canvas(640, 480, COLORS)
    
    def test_canvas_initializes_white(self):
        """Verifica que el canvas inicia blanco."""
        image = self.canvas.get_image()
        self.assertTrue(np.all(image == 255))
    
    def test_add_point(self):
        """Verifica que se pueden añadir puntos."""
        self.canvas.add_point(0.5, 0.5)
        
        current_color = self.canvas.get_current_color_name()
        strokes = self.canvas.strokes[current_color]
        
        self.assertGreater(len(strokes[0]), 0)
    
    def test_clear_canvas(self):
        """Verifica que clear() limpia el canvas."""
        self.canvas.add_point(0.5, 0.5)
        self.canvas.clear()
        
        image = self.canvas.get_image()
        self.assertTrue(np.all(image == 255))
    
    def test_change_color(self):
        """Verifica que se puede cambiar de color."""
        initial_color = self.canvas.get_current_color_name()
        self.assertEqual(initial_color, "AZUL")
        
        new_color = self.canvas.set_color(1)
        self.assertEqual(new_color, "VERDE")
    
    def test_break_stroke(self):
        """Verifica que break_current_stroke crea nuevo trazo."""
        self.canvas.add_point(0.5, 0.5)
        current_color = self.canvas.get_current_color_name()
        
        initial_stroke_count = len(self.canvas.strokes[current_color])
        
        self.canvas.break_current_stroke()
        
        new_stroke_count = len(self.canvas.strokes[current_color])
        self.assertEqual(new_stroke_count, initial_stroke_count + 1)


if __name__ == '__main__':
    unittest.main()
