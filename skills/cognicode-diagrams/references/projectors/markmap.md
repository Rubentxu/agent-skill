# Markmap — atlas interactivo derivado de diagramas existentes

> **Entrada exclusivamente derivada del workspace en HOME.** No leer, buscar, montar ni inspeccionar el checkout, tampoco mediante Git; `--repo` es un identificador de ruta explícita. [Contrato](../investigation-contract.md).

**Contrato:** Markmap es un proyector de navegación, nunca una lente que analice código. CogniCode CLI/MCP es la única interfaz de exploración de código; el agente crea/contrasta los `.dsl`, `.mmd`, `.c4` y otros protocolos. Este proyector indexa ficheros derivados y, cuando existen, claims/queries y asociaciones explícitas entre vistas y evidencia. Transforma `atlas.md` a HTML; no infiere arquitectura. No ejecuta CogniCode, no monta Git ni consulta repositorios.

## Visor local gestionado (opcional)

Tras `atlas.py sync` y `render_markmap.py`, el mismo gestor que LikeC4 ofrece:

```bash
python3 scripts/projectors.py status --repo /raiz/proyecto --projector markmap --engine podman
python3 scripts/projectors.py start --repo /raiz/proyecto --projector markmap --engine podman --port 4173
python3 scripts/projectors.py status --repo /raiz/proyecto --projector markmap --engine podman --check-http
python3 scripts/projectors.py stop --repo /raiz/proyecto --projector markmap --engine podman
python3 scripts/projectors.py remove --repo /raiz/proyecto --projector markmap --engine podman
```

Visor en `http://127.0.0.1:4173/navigation/atlas.html`. `start` es explícito y se rechaza sin HTML gestionado por la skill. La imagen Python mínima sirve solo rutas permitidas, con montaje del workspace derivado **solo lectura**, puerto en loopback y sin listado de directorios; no monta el checkout. **Los ledgers de queries y claims quedan accesibles localmente al abrir sus enlaces: eliminar secretos de esos archivos.** El servidor no tiene autenticación multiusuario: no exponer fuera de loopback. El estado HTTP no equivale a revisión visual real. Usar `atlas.py check` antes de servir; si está obsoleto, sincronizar y renderizar de nuevo.

Para renderizar con Podman rootless, `render_markmap.py` usa `--userns=keep-id`. Solo los artefactos generados de navegación se publican con modo 0644; no se hace chmod general de las evidencias ni del checkout.

## Preparación y ciclo completo

1. Resolver `scripts/workspace.py inspect --repo /ruta/proyecto`; inicializar el workspace si hace falta. El contenido reside **solo** en `~/.cognicode-diagrams/workspaces/<repo>--<id>/`.
2. Pedir a las lentes sus diagramas y, si procede, renderizarlos con Kroki. No generar entidades ni relaciones nuevas desde las imágenes.
3. **Sincronizar durante la investigación**, después de cada observación útil y después de cada nueva proyección. Registrar `lenses/<lens>/reports/<vista>.atlas.json` con claims concretos; un integrador único coordina la escritura del ledger. [Guía incremental](../knowledge-atlas.md).

4. Generar el índice desde los ficheros existentes:

   ```bash
   python3 scripts/atlas.py sync --repo /ruta/proyecto
   python3 scripts/atlas.py check --repo /ruta/proyecto
   ```

   Se crean `navigation/atlas.md` y `navigation/atlas.manifest.json`. El Markdown enlaza fuentes editables, renders SVG/PNG/WebP y contiene **una miniatura embebida por lente** para evitar mapas gigantes; `--no-images` deja solo enlaces. El manifiesto registra SHA-256 y ruta de cada artefacto, pero **no certifica su vigencia respecto al código**. Un archivo nuevo, ausente o modificado devuelve `STALE` en `check`.
4. Opcionalmente incluir enlaces a visores reales con `--viewers --engine podman` (o `docker`). Este flag inspecciona **solo contenedores del workspace controlados por** `scripts/projectors.py`, comprueba HTTP loopback y solo enlaza `ready`: no inicia nada. URLs dinámicas pueden quedar inactivas al detener el contenedor; los enlaces SVG locales siguen funcionando.
5. Renderizar a HTML interactivo mediante CLI Markmap preinstalada **o** contenedor OCI efímero. El usuario autoriza por separado construir la imagen e instalar herramientas. La skill no los instala automáticamente.
6. Abrir `navigation/atlas.html` en navegador local; **revisar de verdad** nodos, zoom, expansión, miniatura y enlaces. Un HTML generado no equivale a inspección visual ni verificación arquitectónica.
7. Al cambiar una fuente o un render, repetir `atlas.py check` → `build` → render HTML → inspección. No es necesario volver a invocar CogniCode si solo cambió la disposición/imagen; sí cuando la petición requiere contrastar la arquitectura con un nuevo commit.

## Podman y Docker (sin daemon permanente)

Preparación explícita una vez, con descarga de dependencias npm **solo al construir la imagen**:

```bash
podman build -f assets/markmap.Containerfile -t cognicode-markmap:0.18.12 assets/
```

Proyección por ejecución efímera:

```bash
python3 scripts/render_markmap.py --repo /ruta/proyecto --engine podman
# o: --engine docker
```

No se expone puerto HTTP. El contenedor recibe el workspace completo en **solo lectura** y un montaje adicional de `navigation/` en escritura, para producir el HTML; SELinux usa etiquetas `:z`. Nunca se monta el checkout. Por defecto `--network none`. **Advertencia verificable:** `markmap-cli --offline` incorpora JS/CSS, pero ciertas versiones pueden intentar obtener dependencias de un CDN *al construir* el HTML; si el comando falla por falta de red, detenerse y registrar el error. El flag opt-in `--allow-asset-network` permite descargar recursos durante el render si el usuario lo autoriza y entiende el riesgo; no implica enviar el Markdown deliberadamente. La disponibilidad de un HTML completamente aislado y el funcionamiento de `:z` requieren UAT en Podman real.

Alternativa si ya tienes la CLI Node instalada:

```bash
python3 scripts/render_markmap.py --repo /ruta/proyecto --engine native
```

Esta alternativa hereda la configuración de red del proceso nativo y no ofrece aislamiento de red del contenedor. El comando ejecuta `markmap ... --offline --no-open --output <temporal>` y sustituye el HTML final **solo** si la salida es válida. Si falla, conserva el HTML anterior. Los enlaces a imágenes siguen siendo archivos separados: `--offline` empaqueta recursos de Markmap, **no incrusta ni distribuye los SVG del workspace**.

## Navegación e interoperabilidad

- `navigation/atlas.md` y `navigation/atlas.html` viven juntos: sus enlaces relativos `../lenses/<lente>/renders/...` deben abrirse con acceso al workspace completo. No mover solo el HTML sin los assets.
- Miniaturas SVG en Markmap: representación de imágenes Markdown; algunos SVG pueden ocupar mucho espacio, limitar una por lente y comprobar render real. Los SVG deben provenir de un proyector local y ser considerados contenido no confiable al abrirlos.
- `LikeC4` y `Structurizr Local` mantienen sus propios formatos y navegación; Markmap **enlaza** sus UIs pero no los incrusta mediante iframes, no accede a sus MCP ni modela relaciones.
- `atlas.md` es salida **generada**: para cambiar su contenido, corregir primero la fuente/diagrama o las reglas de proyección y regenerar. No introducir un atlas como base de conocimiento paralela.

## UAT/AAT pendiente para entorno real

- Verificar `markmap-cli@0.18.12` sobre la imagen OCI y Podman rootless con SELinux.
- Construir HTML con y sin red: declarar si la versión instalada exige descargas de assets en modo `--offline`; nunca dar por probada la ejecución sin red.
- Abrir HTML local y comprobar miniaturas SVG, Markdown anidado y enlaces internos (rutas y codificación de espacios/paréntesis).
- Levantar LikeC4/Structurizr en el workspace; comprobar que el atlas enlaza al puerto real. Detenerlos y conservar navegación por SVG.
- Comprobar regeneración por hashes, rechazo de enlaces simbólicos/traversal, nombres adversarios y ausencia total de escrituras en Git.

Documentación oficial: https://markmap.js.org/docs/packages--markmap-cli
