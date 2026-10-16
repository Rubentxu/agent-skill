# `render-likec4` — el agente crea LikeC4 `.c4`, el visor solo lo proyecta

**CogniCode CLI/MCP proporciona evidencias; el agente interpreta C4 y ESCRIBE el DSL.** LikeC4 no inspecciona el repositorio, no descubre arquitectura ni decide relaciones. Esta ruta amplía las salidas C4 sin cambiar CogniCode ni introducir otro MCP. Consulta la [lente C4](../lenses/c4.md), el [contrato de evidencia](../evidence.md) y la [guía de proyectores](../projectors.md).

## Creación

1. El agente obtiene afirmaciones C1/C2/C3 **solo** mediante consultas CogniCode CLI/MCP sobre código implementado y solicita por CogniCode los fragmentos corroborantes. No usa lectura directa ni documentos/ADR/manifiestos. Mantiene `OBSERVED_CODE`, `INFERRED`, `UNKNOWN` con `query_id` por elemento/arista en el informe externo.
2. El agente escribe `~/.cognicode-diagrams/workspaces/<repo>--<id>/lenses/c4/sources/model.c4` o distribuye los `.c4` en un subdirectorio de `sources/`. LikeC4 encuentra recursivamente `.c4`/`.likec4`.
3. `specification` declara tipos (actor, system, container, component); `model` los elementos y relaciones; `views` las vistas. Identificadores estables y fronteras fieles a la lente; un crate/librería NO se convierte en contenedor desplegable por convención.
4. Crear vistas con `view index`, `view of <sistema>`, y otras con nombres explícitos. Las vistas pueden agregar automáticamente relaciones: estas agregaciones **no** se consideran nueva evidencia ni se reinyectan a CogniCode.
5. No hacer conversión DSL Structurizr→LikeC4 mediante búsqueda/reemplazo. El agente reconstruye la misma intención de modelo a partir de afirmaciones justificadas y compara entidades/relaciones en las dos salidas.

## Ejemplo mínimo sintético (no corresponde al código del usuario)

```likec4
specification {
  element actor
  element system
  element container
}
model {
  customer = actor 'Customer'
  platform = system 'Platform' {
    ui = container 'Web UI'
    api = container 'API'
    ui -> api 'requests via HTTPS'
  }
  customer -> platform.ui 'uses in browser'
}
views {
  view index {
    include *
  }
  view of platform {
    include *
  }
}
```

> Etiquetas/tecnologías son del ejemplo; en un proyecto real nunca inventarlas. La compatibilidad con el parser de la versión instalada se comprueba, no se presupone.

## Verificación y proyección

Con el directorio `sources/` ya existente, validar **únicamente sintaxis y vistas**:

```bash
# Ejecutar expresamente, usando Podman con la carpeta externa de sources
podman run --rm -v "$SOURCES:/data:ro,z" likec4/likec4:latest validate
```

Si la imagen necesita cachés escribibles, usar un directorio de validación desechable **dentro de `~/.cognicode-diagrams/`**, nunca en Git. No desactivar validación por fallos no explicados. Abrir la interfaz local con [el proyector LikeC4](../projectors/likec4.md) para revisión visual. `validate PASS` verifica el DSL, NO la fidelidad de los límites y relaciones al código.

Fuentes oficiales: https://likec4.dev/tutorial/ ; https://likec4.dev/dsl/intro/ ; https://likec4.dev/tooling/cli/.

## Error frecuente: kinds no declarados

Si se declara una `specification` explícita, declarar cada `element kind` usado, incluidos `actor`, `system`, `container`, `component` cuando aparezcan en el modelo. No suponer que un kind base está implícito al declarar otros. Validar contra la versión instalada, ver [ejemplo mínimo y diagnóstico](likec4-kinds.md).
