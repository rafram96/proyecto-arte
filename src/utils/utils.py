"""
Utilidades y herramientas auxiliares para el proyecto.
"""

import cv2
import numpy as np
from datetime import datetime
import json
import os


class ImageExporter:
    """Exporta imágenes del canvas con diferentes opciones."""
    
    @staticmethod
    def save_png(image, filename=None, directory="output"):
        """
        Guarda la imagen en formato PNG.
        
        Args:
            image: Imagen a guardar
            filename: Nombre del archivo (opcional)
            directory: Directorio de salida
            
        Returns:
            str: Path del archivo guardado
        """
        # Crear directorio si no existe
        os.makedirs(directory, exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"artwork_{timestamp}.png"
        
        filepath = os.path.join(directory, filename)
        cv2.imwrite(filepath, image)
        return filepath
    
    @staticmethod
    def save_with_metadata(image, filename=None, directory="output", metadata=None):
        """
        Guarda imagen con metadatos en archivo JSON separado.
        
        Args:
            image: Imagen a guardar
            filename: Nombre base del archivo
            directory: Directorio de salida
            metadata: Diccionario con metadatos
        """
        # Guardar imagen
        filepath = ImageExporter.save_png(image, filename, directory)
        
        # Guardar metadatos
        if metadata is not None:
            metadata_filepath = filepath.replace('.png', '_metadata.json')
            with open(metadata_filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return filepath


class ArtisticFilters:
    """Filtros artísticos para aplicar a las imágenes."""
    
    @staticmethod
    def apply_vintage(image):
        """Aplica efecto vintage/sepia."""
        kernel = np.array([
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189]
        ])
        return cv2.transform(image, kernel)
    
    @staticmethod
    def apply_neon(image):
        """Aplica efecto neón (bordes brillantes)."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        colored_edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return cv2.addWeighted(image, 0.7, colored_edges, 0.3, 0)
    
    @staticmethod
    def apply_sketch(image):
        """Convierte la imagen en un boceto."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inv_gray = 255 - gray
        blur = cv2.GaussianBlur(inv_gray, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    
    @staticmethod
    def apply_oil_painting(image, size=7, dynRatio=1):
        """Efecto de pintura al óleo."""
        return cv2.xphoto.oilPainting(image, size, dynRatio)
    
    @staticmethod
    def apply_cartoon(image):
        """Efecto cartoon/comic."""
        # Bilateral filter para suavizar manteniendo bordes
        color = cv2.bilateralFilter(image, 9, 300, 300)
        
        # Detección de bordes
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            9, 2
        )
        
        # Combinar
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        cartoon = cv2.bitwise_and(color, edges)
        return cartoon


class PerformanceMonitor:
    """Monitor de rendimiento de la aplicación."""
    
    def __init__(self):
        self.fps_start_time = datetime.now()
        self.fps_counter = 0
        self.current_fps = 0
    
    def update(self):
        """Actualiza el contador de FPS."""
        self.fps_counter += 1
        elapsed = (datetime.now() - self.fps_start_time).total_seconds()
        
        if elapsed >= 1.0:
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = datetime.now()
    
    def get_fps(self):
        """Retorna el FPS actual."""
        return self.current_fps
    
    def draw_fps(self, frame, position=(10, 30)):
        """Dibuja el FPS en el frame."""
        fps_text = f"FPS: {self.current_fps:.1f}"
        cv2.putText(frame, fps_text, position,
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


class ColorPalette:
    """Generador y gestor de paletas de colores."""
    
    @staticmethod
    def generate_complementary(base_color):
        """
        Genera color complementario.
        
        Args:
            base_color: Color BGR
            
        Returns:
            Color BGR complementario
        """
        # Convertir a HSV
        bgr_pixel = np.uint8([[base_color]])
        hsv = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV)[0][0]
        
        # Rotar Hue 180 grados
        hsv[0] = (hsv[0] + 90) % 180
        
        # Convertir de vuelta a BGR
        bgr = cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2BGR)[0][0]
        return tuple(int(x) for x in bgr)
    
    @staticmethod
    def generate_analogous(base_color, count=3):
        """
        Genera colores análogos.
        
        Args:
            base_color: Color BGR base
            count: Cantidad de colores a generar
            
        Returns:
            Lista de colores BGR análogos
        """
        bgr_pixel = np.uint8([[base_color]])
        hsv = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV)[0][0]
        
        colors = []
        step = 30  # Grados de separación
        
        for i in range(count):
            new_hsv = hsv.copy()
            new_hsv[0] = (hsv[0] + i * step) % 180
            bgr = cv2.cvtColor(np.uint8([[new_hsv]]), cv2.COLOR_HSV2BGR)[0][0]
            colors.append(tuple(int(x) for x in bgr))
        
        return colors
    
    @staticmethod
    def get_pastel_version(color):
        """Convierte un color a su versión pastel."""
        # Mezclar con blanco
        pastel = tuple(int((c + 255) / 2) for c in color)
        return pastel


class SessionRecorder:
    """Graba sesiones de dibujo en video."""
    
    def __init__(self, filename=None, fps=30.0, size=(1280, 720)):
        """
        Inicializa el grabador.
        
        Args:
            filename: Nombre del archivo de video
            fps: Frames por segundo
            size: Tamaño del video (width, height)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{timestamp}.mp4"
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(filename, fourcc, fps, size)
        self.is_recording = False
    
    def start(self):
        """Inicia la grabación."""
        self.is_recording = True
    
    def stop(self):
        """Detiene la grabación."""
        self.is_recording = False
    
    def write_frame(self, frame):
        """Escribe un frame al video si está grabando."""
        if self.is_recording:
            self.writer.write(frame)
    
    def release(self):
        """Libera el escritor de video."""
        self.writer.release()


class StrokeAnalyzer:
    """Analiza estadísticas de los trazos."""
    
    @staticmethod
    def calculate_total_length(strokes):
        """
        Calcula la longitud total de todos los trazos.
        
        Args:
            strokes: Diccionario de trazos por color
            
        Returns:
            float: Longitud total en píxeles
        """
        total_length = 0
        
        for color_name, color_strokes in strokes.items():
            for stroke in color_strokes:
                for i in range(1, len(stroke)):
                    p1 = stroke[i - 1]
                    p2 = stroke[i]
                    if p1 is not None and p2 is not None:
                        distance = np.sqrt(
                            (p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2
                        )
                        total_length += distance
        
        return total_length
    
    @staticmethod
    def get_color_distribution(strokes):
        """
        Obtiene la distribución de colores usados.
        
        Args:
            strokes: Diccionario de trazos por color
            
        Returns:
            dict: Diccionario con porcentaje por color
        """
        color_counts = {}
        total_points = 0
        
        for color_name, color_strokes in strokes.items():
            count = sum(len(stroke) for stroke in color_strokes)
            color_counts[color_name] = count
            total_points += count
        
        if total_points == 0:
            return {color: 0 for color in color_counts.keys()}
        
        return {
            color: (count / total_points) * 100
            for color, count in color_counts.items()
        }
    
    @staticmethod
    def get_session_stats(strokes, duration_seconds=None):
        """
        Obtiene estadísticas completas de la sesión.
        
        Args:
            strokes: Diccionario de trazos
            duration_seconds: Duración de la sesión en segundos
            
        Returns:
            dict: Estadísticas de la sesión
        """
        total_length = StrokeAnalyzer.calculate_total_length(strokes)
        color_dist = StrokeAnalyzer.get_color_distribution(strokes)
        
        total_strokes = sum(len(color_strokes) for color_strokes in strokes.values())
        
        stats = {
            'total_length_px': total_length,
            'total_strokes': total_strokes,
            'color_distribution': color_dist,
            'timestamp': datetime.now().isoformat()
        }
        
        if duration_seconds:
            stats['duration_seconds'] = duration_seconds
            stats['avg_stroke_length'] = total_length / max(1, total_strokes)
        
        return stats


# Ejemplo de uso
if __name__ == "__main__":
    print("Módulo de utilidades cargado.")
    print("\nComponentes disponibles:")
    print("- ImageExporter: Exportación de imágenes")
    print("- ArtisticFilters: Filtros artísticos")
    print("- PerformanceMonitor: Monitor de FPS")
    print("- ColorPalette: Generación de paletas")
    print("- SessionRecorder: Grabación de sesiones")
    print("- StrokeAnalyzer: Análisis de trazos")
