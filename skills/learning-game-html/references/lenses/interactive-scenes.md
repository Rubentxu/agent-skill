# Lente: escenas con interacción real

Diseñar escena con `Input → Meaningful Action → Visible Consequence → Explanation → Next`. Un mapa donde únicamente se puede pasar el ratón es ornamental; uno donde se elige un país, recibe feedback, se ajusta el zoom y se aprende su relación espacial es interactivo.

Opciones según concepto (no usar todas):

- `SVG`: mapas, órbitas, disecciones, diagramas, líneas temporales, objetos manipulables; ideal para regiones con botones semánticos vinculados y fallback.
- `Canvas`: partículas/animación densa solo cuando SVG/DOM deja de ser apropiado. Añadir alternativa accesible; no necesita WebGL para algo simple.
- `DOM + CSS`: salas de escape, objetos, cartas, colecciones, puzzles, drag-and-drop **con alternativa de clic/teclado**.
- Simulación: modelo determinista pequeño, controles variables, predicción, visualización y comparación; la animación no reemplaza ecuaciones/contenido.

**Requisito**: ofrecer al menos una interacción primaria real y un caso de fallo explicado en la primera vertical. Separar representación de motor. Cargar bajo demanda [catálogo de patrones](../patterns/catalog.md).
