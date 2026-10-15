# Vista previa local con Kroki: adaptador de representación, no modelo

**Cargar solo cuando el usuario solicite previsualizar, exportar SVG/PNG o comprobar renderización.** CogniCode y la lente generan e interpretan el archivo fuente; Kroki convierte ese archivo en imagen. Una imagen visualmente correcta NO demuestra fidelidad al código, equivalencia entre lenguajes, completitud de la lente ni verificación arquitectónica.

## Capacidades verificadas en la documentación oficial

| Texto fuente | `diagram_type` Kroki | Gateway `yuzutech/kroki` | Dependencias | Observaciones |
| --- | --- | --- | --- | --- |
| `.dsl` Structurizr | `structurizr` | Sí | Ninguna adicional | `diagram_options.view-key` para elegir vista; `output=legend` opcional |
| `.puml` PlantUML/C4-PlantUML | `plantuml` o `c4plantuml` | Sí | Ninguna adicional | No confundir con Mermaid C4 |
| `.mmd` Mermaid, incluido C4 | `mermaid` | **No** | `yuzutech/kroki-mermaid` | C4 Mermaid sigue siendo una sintaxis experimental: verificar por render real |

Documentación: https://docs.kroki.io/kroki/setup/install/ ; https://docs.kroki.io/kroki/setup/usage/ ; https://docs.kroki.io/kroki/setup/diagram-options/ ; https://docs.kroki.io/kroki/setup/configuration/

## Operación de menor privilegio

1. Verificar si `http://127.0.0.1:8000` responde. No iniciar ni modificar contenedores automáticamente sin autorización. No recurrir a `kroki.io` ni a otro servidor externo (los diagramas pueden contener arquitectura privada).
2. Para **solo Structurizr**, instalación mínima explícita:

   ```bash
   docker run -d --name kroki -p 127.0.0.1:8000:8000 -e KROKI_SAFE_MODE=SECURE yuzutech/kroki
   ```

3. Para **Mermaid + Structurizr**, levantar el conjunto `assets/kroki-compose.yml` desde la raíz de la skill:

   ```bash
   docker compose -f assets/kroki-compose.yml up -d
   # docker compose -f assets/kroki-compose.yml down
   ```

   **No** lanzar Compose sobre el mismo puerto si el contenedor `kroki` anterior ya está arrancado. Respetar instalaciones existentes, no borrarlas automáticamente. `podman compose` también es posible si está disponible y es compatible con Compose.
4. Antes de declarar servicio preparado, probar **un render real por cada tipo solicitado**, no solo `/` o que el contenedor esté `running`.
5. Mantener modo `SECURE` (default): `Structurizr` restringe `!include`, `!docs` y `!adrs`. Si el DSL necesita `!include`, no rebajar el modo de seguridad en silencio ni concatenar fuentes sin política; declarar `BLOCKED` y ofrecer alternativas autorizadas.

## API y helper sin dependencias

Kroki admite POST JSON a `/`. Las imágenes se solicitan indicando `diagram_type`, `diagram_source` y `output_format`. Para Structurizr con varias vistas, **seleccionar explícitamente la clave de la vista**; nunca asumir la primera:

```bash
python3 scripts/render_kroki.py assets/example-workspace.dsl /tmp/c4-context.svg \
  --type structurizr --view-key Context --format svg

python3 scripts/render_kroki.py assets/example-workspace.dsl /tmp/c4-containers.png \
  --type structurizr --view-key Containers --format png

python3 scripts/render_kroki.py assets/example-c4.mmd /tmp/c4-mermaid.svg \
  --type mermaid --format svg
```

El script lee **solo** el fichero elegido, se conecta únicamente a localhost (no túneles ni servicio público), limita tamaños y timeout, verifica la cabecera/formato de respuesta, y escribe la imagen de forma atómica. Necesita únicamente Python estándar. No instala Kroki ni modifica CogniCode. Para otros lenguajes futuros hay que ampliar la lista permitida conscientemente, no inferir tipo por extensión sin comprobar el formato.

## Proyección, inspección y ciclo de trabajo

- **Fuentes editables** `.dsl` y `.mmd`: conservarlas siempre. Guardar `.svg`/`.png` como artefactos **derivados**; preferir SVG para zoom, revisiones, documentación y diff gráfico. PNG para adjuntos donde SVG no esté admitido.
- **Previsualizar**: abrir el SVG/PNG local con el visor habitual del agente/editor; no hace falta UI web adicional. `http://127.0.0.1:8000` ofrece interfaz básica de Kroki, pero el comando POST controla mejor la selección de vista y evita largas URLs que podrían registrar el DSL.
- **Iterar**: agente edita fuente → renderiza → inspecciona visualmente → detecta etiquetas cortadas, líneas cruzadas y fronteras mal situadas → corrige fuente → vuelve a renderizar. No inventar arreglos semánticos por decisiones de layout.
- **Vistas múltiples Structurizr**: una misma fuente `workspace.dsl`, múltiples imágenes `--view-key Context`, `--view-key Containers`, etc. Reportar la clave y el hash/revisión de fuente si se desea reproducibilidad.
- **Revisar**: un HTTP 2xx y una imagen válida acreditan renderización, NO calidad ni equivalencia de las relaciones. Validar formato y semántica con [validate.md](validate.md) y [evidence.md](evidence.md).

## Casos de error y estados

- Kroki ausente: `RENDERER_UNAVAILABLE` (el diagrama fuente sigue siendo entregable).
- Solo gateway y Mermaid pedido: `COMPANION_MISSING`; no reintentar en bucle.
- HTTP 400: `RENDER_FAILED` + diagnóstico; mantener fuente y cualquier imagen antigua intacta.
- SVG/PNG recibido: `RENDERED`, no `ARCHITECTURE_VERIFIED`.
- Imagen obsoleta respecto a fuente actual: `STALE_PREVIEW`; regenerar después de revisar la fuente.
- Si el agente no puede ver o abrir el archivo resultante: declarar `VISUAL_REVIEW_NOT_RUN`, aunque exista imagen.

**AAT**: gateway solo acepta Structurizr y rechaza Mermaid; Compose permite los dos; `!include` no se facilita eludiendo SECURE; fallo de render no machaca imagen previa; ningún POST sale de localhost; view-key selecciona cada vista; Mermaid C4 real produce imagen o se reporta limitación verificable. AAT requiere Docker/Podman y debe ejecutarse en un entorno autorizado.
