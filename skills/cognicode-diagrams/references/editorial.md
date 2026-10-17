# Proyección editorial C4 — principios de diagram-design, evidencia CogniCode

## Decisión

CogniCode CLI/MCP conserva la **autoridad exclusiva** sobre investigación. Claims, queries y manifiestos de vistas del workspace externo conservan la autoridad factual. [diagram-design](https://github.com/cathrynlavery/diagram-design) inspira el **diseño de presentación**: presupuestos de complejidad, rutas ortogonales, estilo editorial sobrio, SVG accesible y HTML autónomo. No se instala diagram-design ni se crean nuevos analizadores o bases de datos.

## Router semántico mínimo

1. **Topología implementada:** lente C4 actual, con Mermaid/Structurizr/LikeC4 como formatos técnicos.
2. **Explicación editorial de la misma topología:** ejecutar editorial.py sobre la selección ya investigada; no reconsultar código sólo para cambiar el aspecto.
3. **Dependencias y ciclos:** usar capacidades estructuradas de CogniCode. No declarar una lente dependency preparada sin evidencia; si C4 resulta inadecuada, cerrar PARTIAL.
4. **Clases, casos de uso o flujo temporal:** sus lentes siguen planned hasta validarlas en el lenguaje y runtime reales.
5. **Tabla o texto suficiente:** no dibujar.
6. **Relaciones sin evidencia gráfica o procedencia incompleta:** no presentarlas como aristas corroboradas.

El significado manda sobre el formato. No crear una segunda figura si la primera ya resuelve la pregunta.

## Patrones útiles incorporados de diagram-design

La elección es **semántica antes que estética**. Solo tres patrones son proyecciones preparadas, todos sobre la **misma lente C4** y los **mismos claims estructurados de CogniCode**; no registrar nuevas lentes ni copiar diagram-design.

| Pregunta | `--pattern` | Evidencia permitida | Qué añade la proyección |
|---|---|---|---|
| ¿Qué estructura está implementada? | `topology` | Entidades + `graph_edge` seleccionadas | Vista C4 sobria y estable |
| ¿De qué depende este componente? | `dependencies` | Las mismas relaciones demostradas | Grados IN/OUT de **esta vista**, nunca centralidad global |
| ¿Qué evidencia respalda cada bloque? | `traceability` | Claims, query IDs, símbolos corroborados | Identificadores de claim visibles y metadata por elemento |

`--focus <symbol_id>` marca un nodo observado sin cambiar topología ni evidencia (marco discontinuo además de color). `--profile` configura apariencia con perfiles externos y contraste controlado. **No se permite reducir el alcance sin hacerlo explícito:** 2–9 nodos, 12 relaciones, 5 puertos incidentes; excederlo implica dividir la vista, no borrar aristas.

Otros patrones evaluados: `lifecycle phase map` y `paired policy traces` aportan valor para retries, cancelación y gates, pero requieren transiciones y orden corroborados que hoy no garantiza C4 estático. `architecture delta` exige dos snapshots realmente observados y continuidad de identidad; **no** se genera a partir de nombres o commits supuestos. `secure paved road`, controles de gobernanza y defensa en capas requieren evidencia específica de fronteras/controles: nunca completar huecos a partir de documentación de seguridad. Se mantienen **NO READY**. Gráficos de negocio, Sankey y animaciones no aportan valor suficiente a la investigación arquitectónica actual.

### Preguntas y capacidades CogniCode

El agente formula una pregunta `change_impact`, `dependency_structure` o `traceable_decomposition` y usa los **roles semánticos** del `research_protocol.py`. Los roles no son comandos MCP: hay que descubrir tool real, schema, estabilidad, requisitos de grafo/persistencia y soporte/probe por lenguaje **en el CogniCode instalado**. Ejemplos de capacidades potenciales: análisis de impacto, comunidades, consultas de grafo, referencias, jerarquías, miembros y código acotado por símbolo. Si no se anuncian o no funcionan, usar otra herramienta **estructurada del propio CogniCode**, o terminar `PARTIAL/UNKNOWN`. No usar archivos, grep, GitHub, shell, web, docs del checkout ni análisis por un segundo agente para rellenar el diagrama.

## Uso inmediato

Precondiciones: workspace y lente C4 preparados; consultas de CogniCode registradas en evidence/claims.json y evidence/queries.json. Debe existir un informe de vista que seleccione las entidades y relaciones:

~~~json
{
  "schema_version": 1,
  "plane": "implementation",
  "label": "Arquitectura C4",
  "claim_ids": ["C-1", "C-2", "R-1"],
  "assets": ["lenses/c4/sources/context.mmd"]
}
~~~

Guardar como lenses/c4/reports/context.atlas.json. Su fuente debe provenir de consultas CogniCode anteriores. El operador/agente aporta **la ruta raíz explícita como identidad opaca**, no se escanea el checkout para encontrarla.

~~~bash
# 1. Comprobación sin escritura, sin nueva consulta de código.
python3 scripts/editorial.py --repo /raiz/explicita/del/checkout --view context --check --pattern dependencies

# 2. Render de la misma evidencia, foco opcional en symbol_id exacto.
#    Enlazar inmediatamente los dos outputs al informe de vista existente.
python3 scripts/editorial.py --repo /raiz/explicita/del/checkout \
  --view context --pattern dependencies --focus 'App::Api' --link-atlas

# 3. El integrador único sincroniza el índice, sin invocar CogniCode.
python3 scripts/atlas.py sync --repo /raiz/explicita/del/checkout
python3 scripts/atlas.py check --repo /raiz/explicita/del/checkout
~~~

Los paths de salida son `lenses/c4/renders/context.editorial.svg` y `lenses/c4/renders/context.editorial.html`. `--check` valida consulta, claims, extremos, límites de diseño, perfil/foco y seguridad **solo contra el ledger derivado**; NO acredita autenticidad del runtime o vigencia del código. `--link-atlas` actualiza únicamente el manifiesto del workspace externo, preserva la fuente técnica y evita edición manual repetitiva. Solo lo ejecuta **un integrador** si hay Agent Teams. El HTML contiene CSP sin scripts y el visor Markmap aplica CSP sandbox.

El atlas enlaza las dos salidas y crea miniaturas sólo para SVG/PNG/WebP. El proyector local de Markmap admite HTML editorial únicamente desde su ruta dedicada, con CSP sandbox (origen opaco). El generador no necesita Podman.

## Contrato HATEOAS (autodescubrimiento)

El `intent=editorial` de `affordances.py` es **presentación**, no nueva investigación. El siguiente ejemplo es **estado ilustrativo observado por el agente**, no una prueba de código:

~~~json
{
  "intent": "editorial",
  "workspace": "ready",
  "lens": "c4",
  "basis": "current",
  "claim_coverage": "partial",
  "editorial": {
    "view": "context",
    "question_kind": "dependency_structure",
    "pattern": "auto",
    "prepared": "ready",
    "render": "absent",
    "linked": false,
    "atlas_source": "stale",
    "visual_review": "not_run"
  }
}
~~~

Se ofrece `render-editorial` con inputs derivados `{view,pattern,profile,focus?}`. Las transiciones completas son:

`inspect-editorial-evidence → render-editorial → link-editorial-atlas → build-atlas → open-editorial → finish`.

- `prepared=ready` **solo** después de ejecutar `editorial.py --check` en un informe real. Si falla ⇒ `invalid` y se bloquea. El router puro no verifica él solo que un estado declarado sea veraz.
- `render=ready` tras generar ambas salidas. `linked=true` solo tras éxito del enlazado en el manifiesto. `atlas_source=ready` tras `atlas.py check` CURRENT.
- `visual_review=passed` requiere inspeccionar en navegador. No se inventa revisión. `finish` es `PARTIAL` cuando la base/cobertura CogniCode no está verificada.
- La ausencia de CogniCode **no** impide reproyectar evidencias históricas ya registradas, pero el resultado NO se presenta como código actual. No hay lectura alternativa ni nuevos hechos.
- Los tipos `class`, `use-case`, `vertical-slice` siguen `planned`: el router rechaza usar el render editorial como vía de escape.

## Evidencia y ontología

- Entidad: kind=entity, symbol_id, query_ids acreditados, provenance/status=OBSERVED_CODE, plane=static.
- Relación: kind=relation, from_symbol, to_symbol, relation_source=graph_edge, query_ids acreditados.
- Ambos extremos deben figurar como claims de entidad **en la misma vista**. Nada de nodos implícitos ni relation_id inventados.
- reference_link se rechaza como arista. No convertir llamadas estáticas en secuencias runtime.
- Las salidas transportan claim_id, query_ids, plane=static, coverage y símbolo original en metadata; la tabla HTML enumera aristas y su evidencia.
- Orden de nodos **alfabético y meramente visual**: no demuestra orden temporal o de despliegue.
- Cobertura parcial o desconocida queda visible; incluso una vista completa no confirma vigencia del código sin nueva consulta CogniCode.
- No se deducen categorías, protocolos o relaciones leyendo Mermaid o sus renders.

## Presupuesto de presentación

Hasta **9 nodos**, **12 aristas** y **5 conectores incidentes por nodo**. Con menos de dos nodos no aporta valor un diagrama. Exceso ⇒ dividir la selección de la vista y mantener el modelo técnico completo; nunca eliminar silenciosamente una entidad o relación.

El diseño usa tarjetas sobrias, texto legible, rutas ortogonales en carriles externos, sin sombras ni fuentes externas. La tabla de relaciones evita etiquetas flotantes y líneas superpuestas. SVG accesible (title + desc), HTML estático con scroll horizontal, CSS local y CSP sin JavaScript.

Se deja fuera de alcance deliberadamente: copiar los 45 tipos, incorporar plantillas externas, sistemas de perfiles adicionales, servicio persistente, PNG automático, comparaciones de versiones sin dos observaciones reales. Las reglas visuales pueden ampliarse sólo por necesidades demostradas.

## Perfiles de colores (sin dependencias)

Por defecto se utilizan seis tokens internos con contraste legible. Para un tema corporativo u oscuro crear (por autorización del usuario) un perfil en HOME, **nunca en el checkout**:

~~~json
{
  "paper": "#111827",
  "surface": "#1f2937",
  "ink": "#ffffff",
  "stroke": "#e5e7eb",
  "muted": "#cbd5e1",
  "connector": "#94a3b8"
}
~~~

Guardar como ~/.cognicode-diagrams/profiles/dark.json y ejecutar:

~~~bash
python3 scripts/editorial.py --repo /raiz/explicita/del/checkout --view context --profile dark
~~~

El perfil debe ser JSON cerrado con seis colores hexadecimales y contraste de texto de 4.5:1; se rechazan nombres arbitrarios, symlinks y colores con poco contraste. Cambia **sólo el aspecto** de la proyección, nunca claims, consultas, topología o atlas. Los perfiles son opcionales, reutilizables y no requieren servicio ni base de datos.

## Seguridad y pruebas delivery-first

- El script sólo lee ledgers y manifiestos derivados en ~/.cognicode-diagrams/, nunca el checkout ni documentación de producto.
- Rechazo de symlinks, rutas externas, traversal y artefactos ajenos en rutas de salida.
- Salidas idempotentes. No se reemplazan archivos sin marcador de propiedad.
- El atlas sólo indexa HTML editorial con marcador y CSP, nunca HTML arbitrario.
- El servidor del atlas sirve esos archivos con CSP sandbox, sin acceso a cookies/DOM de origen.
- Conservar pruebas de contratos críticos: queries existentes, edges acreditadas, XSS escapado, enlaces del atlas, archivos ajenos preservados.
- UAT visual real con navegador/Podman es **efímera**: ejecutar durante el ciclo y conservar recibo; la prueba unitaria no equivale a un render inspeccionado.

Se han adoptado ideas de diseño de diagram-design (MIT); no se copian sus fuentes, plantillas, assets ni scripts.
