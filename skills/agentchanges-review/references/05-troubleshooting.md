# 05 — Diagnóstico

## El servidor MCP no aparece

1. **¿Está `agc` en el PATH del cliente?** No asumas que sí: un cliente lanzado
   desde el escritorio tiene un `PATH` distinto al de tu terminal.
   ```bash
   command -v agc
   ```
   Si no aparece, invócalo por ruta absoluta en `command`.
2. **¿El cliente espera otro formato?** La clave es `mcpServers` en unos y `mcp` en
   otros, y el tipo es `stdio` o `local` según cuál. Un `type` mal puesto no da
   error de sintaxis: simplemente no arranca.
3. **¿El fichero quedó válido?** Un JSON inválido rompe el cliente entero.
   ```bash
   python3 -c "import json,sys;json.load(open(sys.argv[1]))" <fichero>
   ```
4. **Reinicia el cliente.** La configuración se lee al arrancar.

## El servidor muere al primer error

Síntoma: la primera tool call que topa con un error deja al cliente sin tools para
el resto de la sesión.

Es exactamente lo que pasaba antes de que `fail()` lanzara una `CliError` en vez de
llamar a `process.exit()`. En la CLI, `process.exit()` es lo correcto; por MCP es
fatal. Si ves esto, estás contra un build antiguo: reconstruye el paquete y reinstala.

Diagnóstico rápido: mira el `stderr` del servidor. Si el último mensaje es un `✖`
seguido de muerte del proceso, es ese bug.

## "No hay revisiones para este repo todavía"

No es un error del servidor: es que ese repo no tiene ninguna revisión abierta.

```text
agc -C <repo> init
agc -C <repo> open --base main --head <tu-rama>
```

Si la rama se llama con barras (`feat/auth`), el id de revisión lleva barras. El
producto lo sanea, pero revisa que la revisión aparezca en `agc repo list` después de
crearla: una revisión invisible suele ser un id mal formado.

## El ancla sale `content-changed`

El código que el revisor vio ya no es el que hay. **No lo fuerces.**

Reancla la nota sobre el código actual y vuelve a juzgarlo: puede que el defecto ya
no exista, o que sea otro distinto. Lo que no puedes hacer es aplicar el parche
"porque se parece".

## El parche se rechaza

`patch_preview` te dice el motivo. Los tres casos habituales:

- ancla no `valid`/`moved` → ver arriba;
- la `suggestion` está vacía o es sólo un fragmento → envía la línea **completa**
  con su sangría;
- ya se aplicó → no es un error; comprueba el estado de la nota.

Si el motivo es que el fichero en disco cambió **después** de que la GUI mostrara el
diff, es el motor haciendo su trabajo: alguien escribió código por debajo. Mira el
fichero antes de seguir.

## La GUI no carga

```bash
AGC_DEBUG_GUI=1 agc -C <repo> serve
```

Imprime las rutas candidatas que ha probado y cuál ha elegido. El fallo típico es que
gane la plantilla de desarrollo de Vite en vez del build: por eso se exige que la
carpeta tenga `assets/` y no sólo `index.html`.

Sin GUI compilada el servidor no se cae: sirve una página con el comando exacto
para regenerarla.

## Verificar notas importadas

Las checks importadas llegan en `skipped`. Ver `status` de la nota para ver cuál es.
Actívalas sólo tras leer el comando, y recuerda que se ejecutan con el shell del
sistema, en el repo, con tus permisos. Ver
[`04-mcp-and-install.md`](04-mcp-and-install.md).