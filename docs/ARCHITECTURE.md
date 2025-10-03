"""
Diagrama de arquitectura del sistema.

┌─────────────────────────────────────────────────────────────┐
│                        PAINT APP                            │
│                   (Orquestador Principal)                   │
└────────────┬────────────────────────────────────┬───────────┘
             │                                    │
             │                                    │
    ┌────────▼─────────┐                 ┌───────▼────────┐
    │  GESTURE         │                 │   BRUSH        │
    │  DETECTOR        │                 │   MANAGER      │
    │                  │                 │                │
    │ - MediaPipe      │                 │ - LineBrush    │
    │ - Detección      │                 │ - DabBrush     │
    │   gestos         │                 │ - Tamaños      │
    └──────────────────┘                 └────────────────┘
             │                                    │
             │                                    │
             │                                    │
    ┌────────▼─────────┐                 ┌───────▼────────┐
    │  GESTURE         │                 │   CANVAS       │
    │  FEEDBACK        │                 │                │
    │                  │                 │ - Lienzo       │
    │ - Visualización  │◄────────────────┤ - Trazos       │
    │   landmarks      │    Renderiza    │ - Colores      │
    │ - Estado gesto   │                 │ - Puntos       │
    └──────────────────┘                 └────────────────┘
             │                                    │
             │                                    │
             └────────────┬───────────────────────┘
                          │
                          │
                  ┌───────▼────────┐
                  │    CONFIG      │
                  │                │
                  │ - Constantes   │
                  │ - Parámetros   │
                  │ - Colores      │
                  └────────────────┘

FLUJO DE DATOS:

1. Camera Frame → GestureDetector
2. GestureDetector → Landmarks + Gesture Status
3. Gesture Status → Canvas (add points)
4. Landmarks → GestureFeedback (visual feedback)
5. Canvas + BrushManager → Render strokes
6. Rendered Canvas → Display

PRINCIPIOS DE DISEÑO:

✓ Separación de responsabilidades
✓ Alta cohesión, bajo acoplamiento
✓ Inyección de dependencias
✓ Patrón Strategy (Brushes)
✓ Patrón Facade (PaintApp)
✓ Single Responsibility Principle
✓ Open/Closed Principle

VENTAJAS:

+ Fácil de testear (cada componente es independiente)
+ Fácil de extender (añadir nuevos pinceles, gestos, etc.)
+ Fácil de mantener (cambios aislados)
+ Reutilizable (componentes pueden usarse en otros proyectos)
+ Legible (código organizado y documentado)
"""
