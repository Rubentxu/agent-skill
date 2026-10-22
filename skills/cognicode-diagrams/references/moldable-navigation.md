# Navegación moldable M3 — guía operativa

**Disponible:** una vista contextual por símbolo, en HTML para personas y JSON para agentes. Usa el mismo ledger de CogniCode, el pasaporte de símbolo, el vocabulario DDD por contexto y las vistas C4 ya existentes. No crea otro motor, índice o repositorio de conocimiento.

## Qué hace

Seleccionar un símbolo acreditado permite ver su nombre común (o ID técnico si hay homónimos), su contexto y estado del lenguaje, y elegir entre perspectivas que **existen realmente**: Term Card, Symbol Passport, diagrama C4 editorial y referencias a claims/queries. Si no existe un informe, propone su renderización como pendiente; jamás inventa el fichero ni reinterpreta una búsqueda textual como grafo.

**Principio Moldable Development:** la vista se adapta al objeto y a las evidencias disponibles; no se generan veinte diagramas ni un glosario universal. Dos contextos DDD con el mismo término permanecen separados. Un término accepted requiere curador y solo confirma lenguaje humano, no la implementación.

## Uso tras investigar con CogniCode

La investigación previa sobre el proyecto objetivo se hace únicamente por CogniCode CLI/MCP; no por read_file, grep, Git, GitHub, IDE, documentación del checkout ni agentes exploradores. Los scripts siguientes consultan solo los artefactos derivados bajo HOME. --repo identifica el proyecto, no autoriza leerlo.

```bash
python3 scripts/moldable_views.py --repo /raiz/explicita --symbol 'App::StepExecutor' --context orquestacion --check
python3 scripts/moldable_views.py --repo /raiz/explicita --symbol 'App::StepExecutor' --context orquestacion
python3 scripts/atlas.py sync --repo /raiz/explicita
python3 scripts/atlas.py check --repo /raiz/explicita
```

El proyector almacena navigation/moldable/symbol-<digest>.moldable.json y .moldable.html en el workspace externo. HTML estático con CSP, sin scripts. El atlas incorpora una sección de navegación por símbolo y enlaza los dos formatos. La navegación solo enlaza informes propios actuales y diagramas cuyo manifiesto C4 incluya el claim del símbolo y cuyo modelo pueda validar editorial.model. Si la vista todavía no está renderizada, se anuncia render-editorial como siguiente acción, **sin ejecutar nada**.

Cuando cambia vocabulario, queries, claims o los manifiestos de vista, las páginas pueden quedarse desactualizadas. El atlas compara la vista generada con el modelo derivado actual y exige regeneración si no coincide. CURRENT significa sincronía de artefactos, no que CogniCode haya verificado el SHA actual.

## Router HATEOAS

Ruta ejecutable intent=moldable con moldable.symbol (symbol_id exacto), moldable.context opcional y estados declarados prepared, render, atlas_source, visual_review. Secuencia: inspect-moldable → render-moldable → build-atlas → open-moldable → finish. La preinspección invoca moldable_views.py --check sin escribir. Un origen distinto de CogniCode, un símbolo sin prueba o workspace inseguro bloquea la ejecución sin fallback. El router nunca certifica por sí solo la procedencia de una query.

## Para novatos

La página muestra **qué nombre usamos**, **en qué contexto**, **qué código identifica**, **cómo lo sabemos**, **qué representación podemos abrir ahora** y **qué falta por investigar**. Los nombres humanos no sustituyen el symbol_id; una llamada estática no demuestra ejecución temporal. Los enlaces a evidence/claims.json y evidence/queries.json son a pruebas **derivadas**, no al checkout.

## Cierre y límites

Se han añadido pruebas focalizadas de identidad, contexto ambiguo, trazabilidad, enlaces C4, ausencia de artefactos, actualización del atlas y rutas HATEOAS. La UAT con una instalación real de CogniCode y revisión visual en navegador se certifican únicamente si se ejecutan; no se infieren de unit tests con fixtures.

**Navegación inversa implementada**: cada nodo C4 editorial que disponga de ficha moldable actual enlaza de vuelta a ella. El SVG muestra etiqueta DDD contextual (o `propuesto`); el identificador técnico persiste en tooltip y `data-symbol-id`. Sin ficha vigente, no hay enlace. **Disponible M4:** una página moldable enlaza [Change Impact Briefs](change-impact.md) generados previamente para el mismo símbolo/contexto, exclusivamente mientras el contenido coincide con las evidencias actuales. **M5 disponible:** las páginas contextualizadas descubren [cápsulas agenticas](context-capsules.md) ya generadas y vigentes del mismo símbolo/contexto, con contrato CogniCode-only para agentes receptores. Siguen pendientes las búsquedas moldables automáticas y la generación automática de páginas faltantes.
