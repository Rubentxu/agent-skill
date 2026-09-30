# Credenciales y seguridad

## Principio

Los secretos deben entrar como capacidades/bindings, no como literales, argumentos visibles o texto de logs.

Antes de elegir mecanismo, decide qué propiedad necesitas:

```text
¿el child puede poseer temporalmente el secreto?
  sí -> PipelineK withCredentials
  no -> Agent Secretless Vault signer/proxy/session
```

No mezcles ambas garantías bajo el mismo nombre.

## PipelineK `withCredentials`

La CLI actual soporta store local y lifecycle de credenciales:

```text
pipelinek credentials add [--kind <kind>] <id>
pipelinek credentials list
pipelinek credentials remove <id>
pipelinek credentials rotate [--kind <kind>] <id>
```

La entrada de valores es interactiva/segura según el kind. No automatices pegando secretos en la línea de comandos.

Si el proyecto usa store alternativo, respeta `PIPELINE_CREDENTIALS_STORE` según su gobernanza.

Ejemplo secret text:

```kotlin
withCredentials(
    StepSpec.CredentialsBinding.string("registry-token", "REGISTRY_TOKEN")
) {
    sh("./scripts/publish-using-env.sh")
}
```

El script debe leer `REGISTRY_TOKEN` desde entorno y **no imprimirlo**.

Otros bindings existen para username/password, SSH key, secret file, certificate, zip y username-colon-password; usa sólo el kind requerido.

PipelineK aporta:

- referencia tipada por id/kind;
- scope limitado;
- eventos `CredentialBound/Used/Unbound`;
- redacción de eventos/free text;
- wipe/cleanup al salir del scope.

Pero el proceso hijo que consume el env/file puede poseer los bytes. Esto es protección y lifecycle de secretos, no non-disclosure fuerte frente al proceso.

## Agent Secretless Vault

Si el threat model dice “el agente no debe recibir el secreto”, consulta `09-agent-secretless.md`.

Patrón preferido:

```bash
asv run -- pipelinek run --workspace . pipeline.kts
```

Para integraciones fuertes el child obtiene handles no secretos:

- `SSH_AUTH_SOCK`;
- endpoint/proxy local;
- surrogate sin autoridad remota;
- capability/session id;
- operación semántica brokered.

El broker conserva el secreto real.

No implementes un adapter ASV que simplemente haga:

```text
get secret -> SecretHandle -> env child
```

y lo llames secretless.

## KeePassXC / Secret Service

KeePassXC, GNOME Keyring o KWallet pueden ser buenos almacenes para el **operador**.

No permitas que el agente use directamente `secret-tool lookup`, `keepassxc-cli show` o D-Bus Secret Service para recuperar valores: la API Secret Service está diseñada para devolver secretos a aplicaciones cliente.

Si se integra KeePassXC con ASV:

```text
human unlock
→ trusted ingest/import
→ ASV vault/broker
→ capability/session para agent
```

La frontera real es ASV + aislamiento/policy, no el hecho de que el secreto estuviera guardado en KeePassXC.

## Anti-patrones

- `sh("tool --token=SECRET")`;
- `echo("token=$TOKEN")`;
- persistir variables secretas en artifacts;
- escribir el store dentro del repo;
- desactivar redacción para depurar;
- convertir fallo de credencial en `|| true`;
- llamar “secretless” a un token temporal sólo porque caduca;
- usar Secret Service como backend accesible por el mismo agente y asumir non-disclosure.

## Observabilidad segura

Para inspeccionar uso de credenciales, filtra sólo metadata:

```bash
jq -c '
  select(
    .kind == "CredentialBound"
    or .kind == "CredentialUsed"
    or .kind == "CredentialUnbound"
  )
  | {sequence, kind, credentialsId, purpose}
' "$events"
```

Consulta `10-event-filters.md` para preservar el stream completo y proyectar vistas agentic.

## Revisión agentic

Ante un fallo de credencial, el agente puede reportar:

- credential/capability id;
- kind/purpose;
- postura de seguridad;
- evento de lifecycle;
- destino/acción autorizada;
- error tipado.

Nunca valor materializado.

Si necesita comprobar presencia en el store PipelineK usa `credentials list`, no lectura directa del fichero cifrado. En ASV usa sólo metadata/control que la CLI instalada exponga; nunca inventes un comando de reveal.
