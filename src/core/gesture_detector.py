"""
Detector de gestos usando MediaPipe Hands.
"""

import mediapipe as mp
from .config import (
    FLEXIBILITY_THRESHOLD,
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    LANDMARK_SMOOTHING_ALPHA,
)


class GestureDetector:
    """Detecta gestos específicos de la mano usando landmarks de MediaPipe."""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )
        # Para suavizar la posición de la punta del índice y reducir jitter
        self._last_index_tip = None
    
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
        # Requerimos que corazón y anular estén flexionados; el meñique se ignora
        middle_flexed = (
            get_y(mp_hands.HandLandmark.MIDDLE_FINGER_TIP) > 
            get_y(mp_hands.HandLandmark.MIDDLE_FINGER_PIP) + FLEXIBILITY_THRESHOLD
        )
        ring_flexed = (
            get_y(mp_hands.HandLandmark.RING_FINGER_TIP) > 
            get_y(mp_hands.HandLandmark.RING_FINGER_PIP) + FLEXIBILITY_THRESHOLD
        )

        return index_extended and middle_flexed and ring_flexed
    
    @staticmethod
    def get_index_tip_position(landmarks):
        """
        Obtiene la posición normalizada de la punta del dedo índice.
        
        Args:
            landmarks: Landmarks de la mano detectada
            
        Returns:
            tuple: (x, y) coordenadas normalizadas (0-1)
        """
        # Nota: este método fue estático; lo convertimos a instancia para aplicar suavizado
        raise RuntimeError("Use instance method get_index_tip_position on GestureDetector instance")

    def get_index_tip_position(self, landmarks):
        """
        Obtiene la posición normalizada de la punta del dedo índice con suavizado temporal.
        """
        mp_hands = mp.solutions.hands
        index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        x, y = (index_tip.x, index_tip.y)

        if self._last_index_tip is None:
            self._last_index_tip = (x, y)
            return (x, y)

        alpha = LANDMARK_SMOOTHING_ALPHA
        last_x, last_y = self._last_index_tip
        sm_x = last_x * (1 - alpha) + x * alpha
        sm_y = last_y * (1 - alpha) + y * alpha
        self._last_index_tip = (sm_x, sm_y)
        return (sm_x, sm_y)

    def is_pinch(self, landmarks):
        """
        Detecta si índice y medio están juntos (pinch) independientemente de la mano (izq/der).

        Args:
            landmarks: Landmarks de la mano detectada

        Returns:
            bool: True si la distancia normalizada entre punta índice y punta medio < umbral
        """
        mp_hands = mp.solutions.hands
        idx = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        mid = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

        dx = idx.x - mid.x
        dy = idx.y - mid.y
        dist = (dx * dx + dy * dy) ** 0.5
        from .config import PINCH_DISTANCE_THRESHOLD
        return dist < PINCH_DISTANCE_THRESHOLD
    
    def close(self):
        """Libera recursos de MediaPipe."""
        self.hands.close()
