# Credenciales y seguridad

## Principio

Los secretos deben entrar como capacidades/bindings, no como literales, argumentos visibles o texto de logs.

Antes de elegir mecanismo, decide qué propiedad necesita el pipeline:

```text
NON_EXPORTABLE      -> socket/signer/workload identity
SHORT_LIVED_EXPOSURE -> token temporal
SCOPED_SECRET       -> env/file dentro de withCredentials
```

La postura la determina la proyección real. No llames secretless a env/file.

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

## Providers y proyecciones de PipelineK

Consulta `09-credential-providers.md`.

El objetivo evolutivo es que `withCredentials` siga siendo la fachada DSL y que providers/plugins puedan resolver una credencial como lease + proyección:

- env/file para compatibilidad Jenkins;
- SSH-agent/socket para claves no exportables;
- workload identity/OIDC cuando el servicio lo soporte;
- tokens cortos cuando no exista una integración mejor.

El `CredentialProvider` actual materializa `SecretHandle`/`Credential`; no inventes soporte de sockets/signers hasta que el SPI y el plugin correspondiente existan.

KeePassXC puede aportar dos rutas distintas:

- SSH Agent: la private key puede permanecer detrás del agente OpenSSH y PipelineK sólo necesitar `SSH_AUTH_SOCK`;
- Secret Service: un provider puede recuperar el valor y usar el lifecycle existente de PipelineK, pero eso sigue siendo `SCOPED_SECRET`.

## Anti-patrones

- `sh("tool --token=SECRET")`;
- `echo("token=$TOKEN")`;
- persistir variables secretas en artifacts;
- escribir el store dentro del repo;
- desactivar redacción para depurar;
- convertir fallo de credencial en `|| true`;
- llamar “secretless” a un token temporal sólo porque caduca;
- asumir que Secret Service/Keyring implica no exportabilidad;
- hardcodear providers concretos dentro de core.

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

Si necesita comprobar presencia en el store PipelineK usa `credentials list`, no lectura directa del fichero cifrado. Para providers externos, usa sólo la superficie realmente instalada y documentada; nunca inventes un comando de reveal.