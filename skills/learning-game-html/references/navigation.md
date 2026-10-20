# Router HATEOAS-like — observar → descubrir → actuar → reobservar

`_links: [{rel,href,why}]` apunta a **playbooks locales**, no a HTTP ni comandos que el agente ejecuta automáticamente. El helper no inspecciona el repo ni acredita el estado recibido. Sin helper se aplica manualmente la misma secuencia.

Intentos `create|improve|repair|polish|audit|catalog`; campos observados (sin valores inferidos):

```json
{
  "intent":"create", "brief":"ready", "art":"missing", "scene":"missing",
  "state":"missing", "storage":"missing", "access":"missing",
  "visual_review":"not_run", "browser_check":"not_run", "package":"missing"
}
```

`baseline,brief,art,scene,state,storage,access,package` = `ready|missing|unknown`. `visual_review,browser_check` = `passed|failed|not_run|blocked`. Para `create` no se exige `baseline` previo. Nunca tratar `not_run`/`blocked` como aprobados.

Rutas por intención:

- `create`: brief → art → scene → state → storage → access → visual review → navegador → package.
- `improve`: baseline → brief → state → art → scene → storage → access → visual review → navegador → package.
- `repair`: baseline → brief → state → navegador → (storage si `storage_affected=true`) → package.
- `polish`: baseline → brief → art → scene → access → visual review → navegador → package.
- `audit`: baseline → navegador → visual review, sin modificar el checkout.
- `catalog`: descubrir lentes; no crear archivos.

`baseline` inspecciona HTML/handlers/almacenamiento; `art` define dirección visual; `scene` define interacción; `state` define transiciones; `storage` protege migración. Un intento `repair` no se convierte en rediseño sin solicitarlo.

Para `repair` sobre un bug sensible a progreso, usar `storage_affected=true` (si se conoce) y probar antes y después. Para `improve` se permite combinar sin imponer nuevo framework. Los `ready` declarados no son pruebas por sí solos.

Cierre: `deliver-artifact` solo si evidencia de navegador/visual `passed` y empaquetado `ready`. Si herramientas faltan, informar `blocked`, entregar con estado parcial y trabajo pendiente, no fingir certificado.

`python3 scripts/affordances.py examples/session-create.json` devuelve **una** siguiente affordance.
