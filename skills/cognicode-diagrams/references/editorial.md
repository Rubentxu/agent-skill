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

Guardar como lenses/c4/reports/context.atlas.json. Su fuente se debe haber generado previamente desde la evidencia de CogniCode.

~~~bash
python3 scripts/editorial.py --repo /raiz/explicita/del/checkout --view context
~~~

Salida bajo el mismo workspace:

- lenses/c4/renders/context.editorial.svg
- lenses/c4/renders/context.editorial.html

**Integrador:** añadir ambas rutas a la lista existente de assets del mismo context.atlas.json, sin eliminar la fuente técnica ni otros renders. Después:

~~~bash
python3 scripts/atlas.py sync --repo /raiz/explicita/del/checkout
python3 scripts/atlas.py check --repo /raiz/explicita/del/checkout
~~~

El atlas enlaza las dos salidas y crea miniaturas sólo para SVG/PNG/WebP. El proyector local de Markmap admite HTML editorial únicamente desde su ruta dedicada, con CSP sandbox (origen opaco). El generador no necesita Podman.

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

## Seguridad y pruebas delivery-first

- El script sólo lee ledgers y manifiestos derivados en ~/.cognicode-diagrams/, nunca el checkout ni documentación de producto.
- Rechazo de symlinks, rutas externas, traversal y artefactos ajenos en rutas de salida.
- Salidas idempotentes. No se reemplazan archivos sin marcador de propiedad.
- El atlas sólo indexa HTML editorial con marcador y CSP, nunca HTML arbitrario.
- El servidor del atlas sirve esos archivos con CSP sandbox, sin acceso a cookies/DOM de origen.
- Conservar pruebas de contratos críticos: queries existentes, edges acreditadas, XSS escapado, enlaces del atlas, archivos ajenos preservados.
- UAT visual real con navegador/Podman es **efímera**: ejecutar durante el ciclo y conservar recibo; la prueba unitaria no equivale a un render inspeccionado.

Se han adoptado ideas de diseño de diagram-design (MIT); no se copian sus fuentes, plantillas, assets ni scripts.
