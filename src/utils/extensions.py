"""
Ejemplo de extensión del sistema con nuevos pinceles artísticos.

Este archivo demuestra cómo extender el sistema añadiendo nuevos tipos de pinceles
sin modificar el código existente (Open/Closed Principle).
"""

import cv2
import numpy as np
import random
from core.brushes import Brush


class SprayBrush(Brush):
    """Pincel tipo spray/aerosol."""
    
    def draw(self, canvas, p1, p2, color):
        if p1 is None or p2 is None:
            return
        
        canvas_height, canvas_width = canvas.shape[:2]
        
        # Generar partículas de spray alrededor del punto
        for _ in range(20):  # 20 partículas por aplicación
            angle = random.uniform(0, 2 * np.pi)
            distance = random.uniform(0, self.size * 2)
            
            spray_x = int(p2[0] + distance * np.cos(angle))
            spray_y = int(p2[1] + distance * np.sin(angle))
            
            # Verificar límites
            if 0 <= spray_x < canvas_width and 0 <= spray_y < canvas_height:
                # Color con variación para efecto orgánico
                color_var = tuple([
                    max(0, min(255, c + random.randint(-30, 30))) 
                    for c in color
                ])
                cv2.circle(canvas, (spray_x, spray_y), 1, color_var, -1)


class CalligraphyBrush(Brush):
    """Pincel caligráfico con grosor variable según velocidad."""
    
    def draw(self, canvas, p1, p2, color):
        if p1 is None or p2 is None:
            return
        
        # Calcular "presión" basada en la distancia (velocidad del movimiento)
        distance = np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
        pressure = min(2.0, max(0.5, distance / 10))
        
        # Ajustar grosor según la presión
        thickness = int(max(1, min(self.size * 2, self.size * pressure)))
        
        cv2.line(canvas, p1, p2, color, thickness)


# ============================================================================
# CÓMO USAR ESTOS NUEVOS PINCELES
# ============================================================================

"""
Para usar estos nuevos pinceles, simplemente:

1. Importa las nuevas clases en brushes.py:
   
    from extensions import SprayBrush, CalligraphyBrush

2. Añádelas al diccionario de BrushManager._brushes:
   
   self._brushes = {
       'LINEA': LineBrush,
       'DAB': DabBrush,
       'SPRAY': SprayBrush,
          'CALIGRAFIA': CalligraphyBrush
   }

3. Actualiza BRUSH_TYPES en config.py:
   
    BRUSH_TYPES = ["LINEA", "DAB", "SPRAY", "CALIGRAFIA"]

¡Eso es todo! El sistema automáticamente los incluirá en la rotación.
"""


# ============================================================================
# EJEMPLO DE NUEVO GESTO
# ============================================================================

class ExtendedGestureDetector:
    """
    Ejemplo de cómo extender el detector de gestos con nuevas funciones.
    """
    
    @staticmethod
    def is_erase_gesture(landmarks):
        """
        Detecta gesto de borrado: puño cerrado (todos los dedos flexionados).
        
        Args:
            landmarks: Landmarks de la mano
            
        Returns:
            bool: True si se detecta el gesto de borrado
        """
        import mediapipe as mp
        from core.config import FLEXIBILITY_THRESHOLD
        
        mp_hands = mp.solutions.hands
        
        def get_y(landmark_idx):
            return landmarks[landmark_idx].y
        
        # Todos los dedos principales deben estar flexionados
        fingers_flexed = [
            get_y(mp_hands.HandLandmark.INDEX_FINGER_TIP) > 
            get_y(mp_hands.HandLandmark.INDEX_FINGER_PIP),
            
            get_y(mp_hands.HandLandmark.MIDDLE_FINGER_TIP) > 
            get_y(mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
            
            get_y(mp_hands.HandLandmark.RING_FINGER_TIP) > 
            get_y(mp_hands.HandLandmark.RING_FINGER_PIP),
            
            get_y(mp_hands.HandLandmark.PINKY_TIP) > 
            get_y(mp_hands.HandLandmark.PINKY_PIP)
        ]
        
        return all(fingers_flexed)
    
    @staticmethod
    def is_peace_gesture(landmarks):
        """
        Detecta gesto de paz: índice y corazón extendidos, otros flexionados.
        Útil para función de "deshacer".
        
        Args:
            landmarks: Landmarks de la mano
            
        Returns:
            bool: True si se detecta el gesto de paz
        """
        import mediapipe as mp
        from core.config import FLEXIBILITY_THRESHOLD
        
        mp_hands = mp.solutions.hands
        
        def get_y(landmark_idx):
            return landmarks[landmark_idx].y
        
        # Índice y corazón extendidos
        index_extended = (
            get_y(mp_hands.HandLandmark.INDEX_FINGER_TIP) < 
            get_y(mp_hands.HandLandmark.INDEX_FINGER_PIP) - FLEXIBILITY_THRESHOLD
        )
        
        middle_extended = (
            get_y(mp_hands.HandLandmark.MIDDLE_FINGER_TIP) < 
            get_y(mp_hands.HandLandmark.MIDDLE_FINGER_PIP) - FLEXIBILITY_THRESHOLD
        )
        
        # Anular y meñique flexionados
        ring_flexed = (
            get_y(mp_hands.HandLandmark.RING_FINGER_TIP) > 
            get_y(mp_hands.HandLandmark.RING_FINGER_PIP)
        )
        
        pinky_flexed = (
            get_y(mp_hands.HandLandmark.PINKY_TIP) > 
            get_y(mp_hands.HandLandmark.PINKY_PIP)
        )
        
        return index_extended and middle_extended and ring_flexed and pinky_flexed
    
    @staticmethod
    def is_ok_gesture(landmarks):
        """
        Detecta gesto OK: pulgar e índice formando círculo.
        Útil para guardar la imagen.
        
        Args:
            landmarks: Landmarks de la mano
            
        Returns:
            bool: True si se detecta el gesto OK
        """
        import mediapipe as mp
        
        mp_hands = mp.solutions.hands
        
        # Obtener posiciones del pulgar e índice
        thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        
        # Calcular distancia entre las puntas
        distance = np.sqrt(
            (thumb_tip.x - index_tip.x) ** 2 + 
            (thumb_tip.y - index_tip.y) ** 2
        )
        
        # Si están muy cerca, es un gesto OK
        return distance < 0.05  # Umbral ajustable
