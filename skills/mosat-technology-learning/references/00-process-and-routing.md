# Proceso y routing MOSAT

## Objetivo

MOSAT separa el **modelo de productos** (qué conocimiento/artefactos se generan) del **modelo de procesos** (cómo se aprende). Mantén ambas cosas visibles: un proceso sin productos verificables deriva en lectura; productos sin proceso derivan en documentación arbitraria.

## Ciclo operativo

```text
recopilar
  ↓
organizar
  ↓
analizar y seleccionar
  ↓
leer activamente
  ↓
elaborar fichas
  ↓
elaborar modelos
  ↓
validar descripción
  ↓
¿requiere mejora? ── sí ──↺ investigación dirigida
        │
        no
        ↓
      cerrar
```

No esperes a “terminar de leer” para modelar. La elaboración de fichas y modelos debe empezar pronto porque revela preguntas nuevas.

## Routing por estado observable

| Estado | Evidencia | Siguiente acción |
|---|---|---|
| objetivo difuso | el usuario pide “investiga X a fondo” sin decisión ni audiencia | delimitar goal/depth/deliverable |
| bibliografía ruidosa | muchas fuentes, pocas preguntas concretas | clasificar por perspectiva y autoridad |
| notas narrativas | párrafos sin claim/evidence/question | convertir en fichas |
| conceptos aislados | nombres definidos pero relaciones inciertas | modelo conceptual |
| arquitectura opaca | componentes conocidos pero responsabilidades/autoridad dudosas | modelo estructural |
| comportamiento opaco | capacidades conocidas pero no su secuencia o workflow | modelo funcional |
| semántica temporal opaca | no se sabe qué evento cambia qué estado | modelo dinámico |
| contradicción | dos fuentes fiables no coinciden | acotar versión/contexto y mantener disputa abierta |
| investigación infinita | nuevas fuentes no cambian modelos/decisión | aplicar stop condition |

## Perspectivas

### Disciplina

Pregunta por esencia y conocimiento: definición, clase, diferencias, problema, propósito, fundamentos, conceptos, estándares, evolución y clasificación.

### Proceso

Pregunta por creación y ciclo de vida: cómo se diseña, construye, despliega, opera, mantiene, mejora y retira; roles, prácticas y dependencias de ingeniería.

### Producto

Pregunta por el sistema resultante: componentes, arquitectura, tecnologías base, funciones, servicios, casos de uso, estados, eventos, atributos de calidad y restricciones.

Son complementarias, no una secuencia obligatoria. Pondera según el objetivo.
