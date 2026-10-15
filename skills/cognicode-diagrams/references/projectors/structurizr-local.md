# Structurizr Local — visor interactivo C4, no modelador autoritativo

El agente genera `workspace.dsl` desde CogniCode con la lente C4. Structurizr Local **solo interpreta ese DSL y muestra las vistas**; no recibe el checkout, ni ejecuta análisis de código, ni puede cambiar afirmaciones arquitectónicas por sí mismo.

## Inicio con Podman (recomendado)

```bash
python3 scripts/workspace.py init --repo /ruta/a/mi-proyecto
python3 scripts/workspace.py init-lens --repo /ruta/a/mi-proyecto --lens c4
# El agente ha escrito workspace.dsl en lenses/c4/sources/ del workspace externo.
python3 scripts/projectors.py start --repo /ruta/a/mi-proyecto --projector structurizr --engine podman
python3 scripts/projectors.py status --repo /ruta/a/mi-proyecto --projector structurizr --engine podman --check-http
```

Abrir `http://127.0.0.1:8080/` para navegar por las vistas del DSL. Docker es alternativa con `--engine docker`; cambiar con `--port` al crear. El gestor añade `STRUCTURIZR_EDITABLE=false`, `STRUCTURIZR_AUTOSAVEINTERVAL=0` y `STRUCTURIZR_AUTOREFRESHINTERVAL=2000` para priorizar **proyección** sobre edición del workspace. Por requisitos del contenedor, la carpeta externa se monta con permiso de escritura; todas las escrituras quedan fuera de Git. No confiar en variables si la versión efectiva no las acepta: comprobar comportamiento en UAT.

```
python3 scripts/projectors.py stop --repo /ruta/a/mi-proyecto --projector structurizr --engine podman
```

## Inspección y límites

Comprobar que el navegador muestra las vistas esperadas, los identificadores de contenedores, los límites C1/C2/C3 y las relaciones. El agente corrige las fuentes `.dsl`; el visor no se usa como autoridad de estructura. No activar el MCP de Structurizr ni `server` multiusuario: `local` es la opción apropiada. No utilizar `structurizr/lite`, sin evolución activa.

Fuentes: https://docs.structurizr.com/local/ , https://docs.structurizr.com/local/configuration/ .
