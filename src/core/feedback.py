"""
Visualización de retroalimentación de gestos.
"""

import cv2
import mediapipe as mp
from .config import (
    FEEDBACK_COLOR_MET, 
    FEEDBACK_COLOR_NOT_MET,
    FEEDBACK_FONT,
    FEEDBACK_TEXT_SCALE,
    FEEDBACK_TEXT_THICKNESS,
    FEEDBACK_LINE_THICKNESS,
    FEEDBACK_CIRCLE_RADIUS,
    FLEXIBILITY_THRESHOLD
)


class GestureFeedback:
    """Proporciona retroalimentación visual sobre la detección de gestos."""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
    
    def draw(self, frame, landmarks, is_gesture_active):
        """
        Dibuja retroalimentación visual en el frame.
        
        Args:
            frame: Frame donde dibujar
            landmarks: Landmarks de la mano
            is_gesture_active: Si el gesto está activo
        """
        h, w, _ = frame.shape
        
        def to_pixel(landmark_coord):
            return (int(landmark_coord.x * w), int(landmark_coord.y * h))
        
        def get_y(landmark_idx):
            return landmarks[landmark_idx].y
        
        feedback_text_lines = []
        
        # --- Dedo Índice ---
        self._draw_index_finger(frame, landmarks, to_pixel, get_y, feedback_text_lines)
        
        # --- Dedos Corazón, Anular y Meñique ---
        self._draw_flexed_fingers(frame, landmarks, to_pixel, get_y, feedback_text_lines)
        
        # --- Estado general del gesto ---
        self._draw_gesture_status(frame, is_gesture_active, feedback_text_lines)
    
    def _draw_index_finger(self, frame, landmarks, to_pixel, get_y, feedback_text_lines):
        """Dibuja retroalimentación para el dedo índice."""
        index_tip_px = to_pixel(landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP])
        index_dip_px = to_pixel(landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_DIP])
        index_pip_px = to_pixel(landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_PIP])
        index_mcp_px = to_pixel(landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_MCP])
        
        index_extended_y_check_1 = (
            get_y(self.mp_hands.HandLandmark.INDEX_FINGER_TIP) < 
            get_y(self.mp_hands.HandLandmark.INDEX_FINGER_PIP) - FLEXIBILITY_THRESHOLD
        )
        index_extended_y_check_2 = (
            get_y(self.mp_hands.HandLandmark.INDEX_FINGER_PIP) < 
            get_y(self.mp_hands.HandLandmark.INDEX_FINGER_MCP) - FLEXIBILITY_THRESHOLD
        )
        index_condition_met = index_extended_y_check_1 and index_extended_y_check_2
        
        color_index = FEEDBACK_COLOR_MET if index_condition_met else FEEDBACK_COLOR_NOT_MET
        
        cv2.line(frame, index_mcp_px, index_pip_px, color_index, FEEDBACK_LINE_THICKNESS)
        cv2.line(frame, index_pip_px, index_dip_px, color_index, FEEDBACK_LINE_THICKNESS)
        cv2.line(frame, index_dip_px, index_tip_px, color_index, FEEDBACK_LINE_THICKNESS)
        cv2.circle(frame, index_tip_px, FEEDBACK_CIRCLE_RADIUS, color_index, -1)
        cv2.circle(frame, index_dip_px, FEEDBACK_CIRCLE_RADIUS, color_index, -1)
        cv2.circle(frame, index_pip_px, FEEDBACK_CIRCLE_RADIUS, color_index, -1)
        cv2.circle(frame, index_mcp_px, FEEDBACK_CIRCLE_RADIUS, color_index, -1)
        
        status = "EXTENDIDO" if index_condition_met else "NO EXTENDIDO"
        feedback_text_lines.append(f"Indice: {status}")
    
    def _draw_flexed_fingers(self, frame, landmarks, to_pixel, get_y, feedback_text_lines):
        """Dibuja retroalimentación para dedos que deben estar flexionados."""
        finger_data = [
            (self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP, 
             self.mp_hands.HandLandmark.MIDDLE_FINGER_DIP,
             self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP, 
             self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP, 
             "Corazon"),
            (self.mp_hands.HandLandmark.RING_FINGER_TIP, 
             self.mp_hands.HandLandmark.RING_FINGER_DIP,
             self.mp_hands.HandLandmark.RING_FINGER_PIP, 
             self.mp_hands.HandLandmark.RING_FINGER_MCP, 
             "Anular"),
            (self.mp_hands.HandLandmark.PINKY_TIP, 
             self.mp_hands.HandLandmark.PINKY_DIP, 
             self.mp_hands.HandLandmark.PINKY_PIP,
             self.mp_hands.HandLandmark.PINKY_MCP, 
             "Meñique"),
        ]
        
        for tip_idx, dip_idx, pip_idx, mcp_idx, name in finger_data:
            tip_px = to_pixel(landmarks[tip_idx])
            dip_px = to_pixel(landmarks[dip_idx])
            pip_px = to_pixel(landmarks[pip_idx])
            mcp_px = to_pixel(landmarks[mcp_idx])
            
            flexed_condition = get_y(tip_idx) > get_y(pip_idx) + FLEXIBILITY_THRESHOLD
            color_finger = FEEDBACK_COLOR_MET if flexed_condition else FEEDBACK_COLOR_NOT_MET
            
            cv2.line(frame, mcp_px, pip_px, color_finger, FEEDBACK_LINE_THICKNESS)
            cv2.line(frame, pip_px, dip_px, color_finger, FEEDBACK_LINE_THICKNESS)
            cv2.line(frame, dip_px, tip_px, color_finger, FEEDBACK_LINE_THICKNESS)
            cv2.circle(frame, tip_px, FEEDBACK_CIRCLE_RADIUS, color_finger, -1)
            cv2.circle(frame, dip_px, FEEDBACK_CIRCLE_RADIUS, color_finger, -1)
            cv2.circle(frame, pip_px, FEEDBACK_CIRCLE_RADIUS, color_finger, -1)
            cv2.circle(frame, mcp_px, FEEDBACK_CIRCLE_RADIUS, color_finger, -1)
            
            status = "FLEXIONADO" if flexed_condition else "NO FLEXIONADO"
            feedback_text_lines.append(f"{name}: {status}")
    
    def _draw_gesture_status(self, frame, is_gesture_active, feedback_text_lines):
        """Dibuja el estado general del gesto."""
        if is_gesture_active:
            cv2.putText(frame, "GESTO OK - DIBUJANDO", (10, 30), 
                       FEEDBACK_FONT, 0.7, FEEDBACK_COLOR_MET, 2, cv2.LINE_AA)
        else:
            cv2.putText(frame, "GESTO NO DETECTADO", (10, 30), 
                       FEEDBACK_FONT, 0.7, FEEDBACK_COLOR_NOT_MET, 2, cv2.LINE_AA)
            for line_num, text_feedback in enumerate(feedback_text_lines):
                cv2.putText(frame, text_feedback, (10, 60 + line_num * 25), 
                           FEEDBACK_FONT, FEEDBACK_TEXT_SCALE, FEEDBACK_COLOR_NOT_MET, 
                           FEEDBACK_TEXT_THICKNESS, cv2.LINE_AA)
