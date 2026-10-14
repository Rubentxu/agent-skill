# Escaneos previos y evaluación de preparación

## Elección mínima de trabajo

| Perfil | Necesidad | Escaneo justificado | Preparación |
|---|---|---|---|
| `quick` | Identificar lenguajes, estructura y símbolos | `project_overview` / `project_insights`, índice `lightweight` si es útil | Navegación; aún no hay modelo semántico corroborado |
| `architecture` | Arquitectura C1/C2/C3 basada en código | Índice + grafo + consultas de dependencias; inspección de manifiestos e IaC | la lente C4 puede comenzar, sujeto a cobertura |
| `focused` | Actualizar una vista de un subárbol o símbolo | `index query`, `index outline`, `graph per-file` o MCP de impacto / subgrafo | Preparación limitada al área estudiada |

No ejecutar `analyze .` indiscriminadamente, especialmente si faltan LSP o hay monorepos grandes. Tras `doctor`, decidir si hace falta. Para la lente C4, analizar también manifiestos (`Cargo.toml`, `package.json`, Dockerfiles, deployment YAML, etc.) mediante lectura autorizada; CogniCode informa relaciones de código, no certifica contenedores desplegados.

## CLI — interfaz estable

```bash
# Identidad para poder reevaluar frescura (en un repositorio Git):
git -C /ruta/al/proyecto rev-parse HEAD
git -C /ruta/al/proyecto status --porcelain

# Comprobar la interfaz realmente instalada:
cognicode --version
cognicode index build --help
cognicode graph full --help

# Inventario de símbolos económico:
cognicode --format json index build /ruta/al/proyecto --strategy lightweight

# Grafo cuando la pregunta necesita dependencias entre símbolos:
cognicode --format json graph full /ruta/al/proyecto

# Investigaciones acotadas de bajo coste:
cognicode index outline /ruta/al/proyecto/src/archivo.rs
cognicode index query NombreDeSimbolo /ruta/al/proyecto
```

**Matiz importante:** `cognicode --format json ...` sitúa el formato a nivel global, que es el contrato del binario actual para `index`/`graph`; evitar asumir que `graph full --format json` produce el mismo resultado. La ejecución de `graph full` entrega `status`, `skipped_files`, contadores y coste; comprobarlos antes de declarar `READY`.

`index build` puede informar éxito sin haber creado una base de conocimiento durable compartida entre procesos. La ficha posterior contiene el resultado comprobado, no una afirmación de persistencia.

## MCP — interfaz para exploración agent-first

1. Establecer el servidor conectado `cognicode-mcp`; comprobar handshake, `tools/list` **completo**, incluida paginación cuando exista, y esquemas de cada herramienta.
2. Realizar una consulta económica como `project_overview` o `project_insights`, si el catálogo la anuncia.
3. Para relaciones, invocar `build_graph`, por ejemplo con argumentos `{"directory":"/ruta/al/proyecto"}` si coincide con el esquema instalado.
4. En **la misma conexión**, ejecutar una consulta dependiente del grafo, por ejemplo `graph_communities` o `graph_query`. Confirmar que la consulta no falla por `graph not built` y devuelve los datos esperables en un fixture no vacío.
5. Revisar el estado de la construcción. Si informa errores parciales, tiempos agotados, símbolos no resueltos, aristas incompletas o archivos omitidos, declarar cobertura `PARTIAL`.

No confundir `export_mermaid` del call graph con una salida C4. `project_overview`/`project_insights` no sustituyen la comprobación de despliegues y fronteras runtime. No llamar a `explorer-mcp`.

## Errores que requieren discriminación

- **No existe `cognicode-mcp`**: comprobar perfil `reviewer` y rutas resueltas antes de reinstalar.
- **No existe tool anunciada en un documento**: seguir `tools/list` de la instalación; no suponer versiones ni tool count.
- **`graph not built` tras reinicio**: caché no demostrada para la sesión actual; reconstruir/revalidar una vez, sin bucles.
- **`status=partial` o archivos omitidos**: conservar lista y no concluir "no existe relación" fuera de cobertura.
- **Repo cambiado desde el escaneo**: refrescar alcance afectado. Dirty working tree significa que el SHA por sí solo no identifica el contenido exacto.
- **Escaneo demasiado costoso**: detener nuevas fases, registrar lo obtenido y negociar alcance sin inventar certificados.
- **Sin manifest de despliegue**: la lente C4 deberá pedir verificación humana de contenedores reales.

## Ficha mínima para un handoff a cualquier lente

No se pretende materializar toda la base de conocimiento: la autoridad son el código y las consultas disponibles. Producir un pequeño fichero Markdown fuera del repo, con ubicación autorizada, cuyo formato está en `../assets/READINESS-template.md`. Las fuentes han de poder comprobarse otra vez. Las inferencias se separan de los hechos observados y **nunca** se consideran persistencia canónica del grafo.
