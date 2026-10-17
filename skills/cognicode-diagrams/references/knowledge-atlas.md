# Atlas de conocimiento incremental — CogniCode Diagrams

**Objetivo:** que cada descubrimiento y proyección útil contribuya **inmediatamente** al mapa navegable sin crear otra base de datos ni volver a inspeccionar código. `claims.json` y `queries.json` de CogniCode son las evidencias; `*.atlas.json` solo vinculan vistas a claims; el atlas es una **proyección regenerable**.

## Secuencia obligatoria para el agente

1. Formular pregunta acotada y obtener símbolos/relaciones mediante CogniCode CLI/MCP exclusivamente. Registrar nuevas observaciones y queries bajo `evidence/claims.json` y `evidence/queries.json` con IDs estables. Solo hechos observados pueden decir `OBSERVED_CODE`. Desconocidos e inferencias se distinguen; no sustituir por textos extraídos del checkout.
2. **Después de cada observación útil consolidada**, ejecutar `python3 scripts/atlas.py sync --repo /raiz/explicita`. Ya aparece el concepto y su evidencia antes del primer diagrama. Es idempotente si no cambió el ledger.
3. Tras crear una vista y sus fuentes/renders, producir **solo** `lenses/<lente>/reports/<vista>.atlas.json` con IDs de los claims efectivamente representados y rutas de assets existentes. Volver a ejecutar `atlas.py sync`. El atlas enlaza tanto las fuentes DSL/Mermaid/LikeC4 como los SVG/PNG correspondientes, sin inferir nuevas relaciones desde las imágenes.
4. **Agent Teams**: investigadores y proyectores trabajan en preguntas y vistas independientes; **un agente integrador** serializa cambios al ledger compartido, asocia manifests por vista y sincroniza el atlas tras cada entrega. No editar simultáneamente `claims.json`/ `queries.json` ni publicar simultáneamente `atlas.md`. Ningún equipo necesita crear otro estado persistente.
5. Al solicitar revisión visual o cerrar el bloque, renderizar `atlas.html` con Markmap instalado/autorizado. **No reconstruir HTML ni arrancar Podman tras cada pregunta**; el Markdown incremental ya es navegable, y `atlas.py check` detecta cuándo refrescarlo. `CURRENT` confirma hashes **de artefactos**, nunca vigencia del código; para esta última hace falta evidencia CogniCode actual.

## Vincular una vista concreta (ejemplo sintético)

Fichero `lenses/c4/reports/contexto.atlas.json`:

```json
{
  "schema_version": 1,
  "label": "C4 — entrada de solicitudes",
  "claim_ids": ["C-1", "R-2"],
  "assets": [
    "lenses/c4/sources/entrada.mmd",
    "lenses/c4/renders/entrada.svg"
  ]
}
```

Requisitos: los claims existen en `claims.json`, cada asset existe entre las fuentes/renders de **esa misma lente**, rutas relativas al workspace externo, sin symlinks/traversal, JSON válido. Asociar solo las afirmaciones representadas por esa vista. Cuando no haya vínculo preciso, el recurso seguirá accesible desde el inventario por lente pero **no** se asociará arbitrariamente a un símbolo.

### Render editorial de una vista existente

Cuando la vista C4 ya tiene claims y fuentes técnicas, ejecutar `scripts/editorial.py --repo <raíz> --view <nombre>`, incorporar los **dos** ficheros `*.editorial.svg` y `*.editorial.html` a `assets` del mismo manifiesto `*.atlas.json`, y sincronizar. El atlas registra sus hashes, enlaza el HTML y no lo usa como miniatura. No se crea otro tipo de claim ni se analiza SVG/HTML como evidencia. La vista HTML generada es estática y el servidor Markmap la sirve con CSP sandbox. [Guía editorial](editorial.md).

## Acceso y seguridad

Solo archivos **derivados** bajo `~/.cognicode-diagrams/workspaces/<id>/`; nada de Git, shell sobre checkout, consultas directas al repositorio ni otro indexador. El atlas jamás convierte una referencia `find_usages` en arista de grafo ni una llamada estática en protocolo HTTP. Markmap es un árbol interactivo: para relaciones cruzadas, generar enlaces por claim y vistas, **no un nuevo grafo persistente**.

## Límites que evitan morralla

Sin DB, sin daemon, sin segundo MCP, sin inferencia a partir de nombres de ficheros, sin indexar imágenes. Probar con fixtures pequeños y conservar solo contratos críticos: idempotencia, stale al añadir evidencia, vista→claim→asset, rechazo de falso claim/enlaces externos. UAT de agente y render real se ejecutan en el ciclo y se retiran tras guardar recibo, si no cubren nueva garantía permanente.

[Markmap](projectors/markmap.md) · [evidencia](evidence.md) · [workspace](workspace.md)

## Semántica tipada

Cada rama procede de `claim.category` explícito, no de los nombres de archivo. El atlas muestra `query_ids`, `plane`, `coverage`, `provenance`, y únicamente los atributos de relación observados. `CODE_DOC`/`CURATED_INTENT` se ubican en intención; la asociación de una vista de implementación a un claim de intención se rechaza. Véase [contrato de procedencia](visual-evidence.md).
