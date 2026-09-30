# Extender PipelineK mediante plugins

Esta guía es para **usar la arquitectura de extensión de PipelineK**, no para copiar el catálogo de otro CI.

## Principio

Core pequeño, ecosistema amplio:

```text
CORE
  universal execution semantics

OFFICIAL_PLUGIN
  capacidades first-party desacoplables

EXTERNAL_PLUGIN
  vendor/domain integrations
```

Una feature no universal debe intentarse primero mediante el SDK público.

## Step plugin

Golden path conceptual:

```text
typed Input/Output
→ codecs
→ StepDescriptor
→ StepContract
→ handler
→ StepDefinition
→ StepDefinitionContributor
→ plugin JAR
→ typed Kotlin DSL façade
→ registryStep/registryBlock
→ --plugin-jar
→ canonical durable spine
```

El plugin posee su StepKey, tipos, codecs, handler y façade. Core posee registry, admission, durable execution, replay y capabilities.

### MUST NOT

- añadir un `when(stepKey)` al coordinator;
- registrar el plugin en `CoreStepRegistryFactory`;
- crear una ruta durable especial;
- importar internals del engine;
- ejecutar I/O durante construcción DSL;
- solicitar un contexto omnipotente;
- saltarse capability admission.

Si el plugin necesita algo no expuesto, trátalo como **SDK gap** y mejora una capability genérica.

## External plugin runtime

Cuando el plugin JAR es compatible:

```bash
pipelinek run \
  --workspace "$PWD" \
  --plugin-jar /absolute/path/plugin.jar \
  pipeline.kts
```

El mismo plugin debe ser visible a compilación y runtime. Ausencia/incompatibilidad debe fallar cerrado.

## Directivas extensibles

Las directivas no son Steps disfrazados. Una directiva aporta política/estructura al Stage y el interpreter genérico consume esa política.

```text
DirectiveDefinition/plugin
→ typed/opaque carrier
→ DirectiveRegistry
→ generic admission/interpreter
```

Nunca:

```text
if directive.key == "vendor.foo" inside core
```

## Familias apropiadas para plugins

Buenas candidatas:

- SCM;
- testing/reporting;
- utilidades JSON/YAML/zip/hash;
- HTTP;
- containers;
- notifications;
- locks/input local;
- toolchains;
- vendor integrations;
- credential/secret providers.

La decisión no depende de popularidad o de paridad con otra herramienta, sino de universalidad y de si el SDK puede expresarlo sin privilegios.

## Certificación

Un plugin sólo es product-ready cuando demuestra como mínimo:

- identidad;
- codec round-trip;
- capability admission;
- success/failure tipados;
- durable fresh/replay/divergence;
- observabilidad;
- arquitectura sin core-specific branch;
- ejecución real desde distribución/plugin JAR.