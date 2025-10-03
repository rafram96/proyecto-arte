"""
Detector de gestos usando MediaPipe Hands.
"""

import mediapipe as mp
from .config import FLEXIBILITY_THRESHOLD


class GestureDetector:
    """Detecta gestos específicos de la mano usando landmarks de MediaPipe."""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.5
        )
    
    def process_frame(self, rgb_frame):
        """
        Procesa un frame RGB y retorna los resultados de detección de manos.
        
        Args:
            rgb_frame: Frame en formato RGB
            
        Returns:
            Resultado de la detección de MediaPipe
        """
        return self.hands.process(rgb_frame)
    
    @staticmethod
    def is_drawing_gesture(landmarks):
        """
        Detecta el gesto de dibujo: índice extendido, otros dedos flexionados.
        
        Args:
            landmarks: Landmarks de la mano detectada
            
        Returns:
            bool: True si se detecta el gesto de dibujo
        """
        mp_hands = mp.solutions.hands
        
        def get_y(landmark_idx):
            return landmarks[landmark_idx].y
        
        # 1. Dedo índice extendido
        index_extended = (
            get_y(mp_hands.HandLandmark.INDEX_FINGER_TIP) < 
            get_y(mp_hands.HandLandmark.INDEX_FINGER_PIP) - FLEXIBILITY_THRESHOLD
        ) and (
            get_y(mp_hands.HandLandmark.INDEX_FINGER_PIP) < 
            get_y(mp_hands.HandLandmark.INDEX_FINGER_MCP) - FLEXIBILITY_THRESHOLD
        )
        
        # 2. Dedos corazón, anular y meñique flexionados
        middle_flexed = (
            get_y(mp_hands.HandLandmark.MIDDLE_FINGER_TIP) > 
            get_y(mp_hands.HandLandmark.MIDDLE_FINGER_PIP) + FLEXIBILITY_THRESHOLD
        )
        ring_flexed = (
            get_y(mp_hands.HandLandmark.RING_FINGER_TIP) > 
            get_y(mp_hands.HandLandmark.RING_FINGER_PIP) + FLEXIBILITY_THRESHOLD
        )
        pinky_flexed = (
            get_y(mp_hands.HandLandmark.PINKY_TIP) > 
            get_y(mp_hands.HandLandmark.PINKY_PIP) + FLEXIBILITY_THRESHOLD
        )
        
        return index_extended and middle_flexed and ring_flexed and pinky_flexed
    
    @staticmethod
    def get_index_tip_position(landmarks):
        """
        Obtiene la posición normalizada de la punta del dedo índice.
        
        Args:
            landmarks: Landmarks de la mano detectada
            
        Returns:
            tuple: (x, y) coordenadas normalizadas (0-1)
        """
        mp_hands = mp.solutions.hands
        index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        return (index_tip.x, index_tip.y)
    
    def close(self):
        """Libera recursos de MediaPipe."""
        self.hands.close()
