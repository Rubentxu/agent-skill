# Providers de credenciales y proyecciones no exportables

## Objetivo

PipelineK puede incorporar las ideas viables de un modelo secretless sin convertirse en otro producto ni duplicar un vault completo.

Conserva la DSL Jenkins-familiar y evoluciona el modelo ya previsto:

```text
CredentialRef
  -> CredentialProvider plugin
  -> CredentialLease
  -> CredentialProjection
  -> child process
```

La proyección determina la exposición real.

## Estado real

- `withCredentials {}` es superficie estable.
- `CredentialProvider` existe como port SPI.
- `ProviderCapabilities` ya modela lease/revocation/ACL.
- el diseño V2 ya define `CredentialRef -> CredentialLease -> CredentialProjection`.
- la spec enumera `SshAgentProjection`, `OidcTokenProjection`, env/file/volume/CSI.
- `ContributedBindingFactory` ya usa `ServiceLoader` para ampliar binding kinds.
- el provider de producción actual se compone directamente con `LocalCredentialProvider`; discovery dinámico de `CredentialProvider` todavía no es realidad.

No afirmes que un provider KeePassXC/Secret Service/SSH-agent existe si la instalación no lo ofrece.

## Posturas

| Proyección | Secreto real en child | Postura |
|---|---:|---|
| SSH-agent / signer socket | no | `NON_EXPORTABLE` |
| proxy/socket autenticado | no | `NON_EXPORTABLE` |
| workload identity | no o mínimo | `NON_EXPORTABLE` / provider-native |
| token corto | sí | `SHORT_LIVED_EXPOSURE` |
| env | sí | `SCOPED_SECRET` |
| fichero temporal | sí | `SCOPED_SECRET` |
| argv/literal | sí | prohibido por defecto |

## No romper la DSL

Mantén:

```kotlin
withCredentials(...) {
    sh(...)
}
```

No añadas un top-level DSL distinto por proveedor. La selección debe ocurrir debajo:

```text
binding DSL
  -> projection factory
  -> provider seleccionado por config/profile
  -> lease
  -> projection sobre el body context
```

El provider local actual se adapta a `Environment/File`. Providers nuevos pueden aportar otras proyecciones sin branches por id en core.

## Evolución del SPI

El `CredentialProvider` actual devuelve `SecretHandle`/`Credential`, por lo que está centrado en bytes. No lo rompas: añade un SPI versionado de leases/proyecciones y un adapter legacy.

Conceptualmente:

```kotlin
interface CredentialLeaseProvider {
    val providerId: String
    val capabilities: ProviderCapabilities
    fun acquire(ref: CredentialRef, context: CredentialContext): CredentialLease
}

sealed interface CredentialRuntimeProjection {
    data class Environment(/*...*/) : CredentialRuntimeProjection
    data class File(/*...*/) : CredentialRuntimeProjection
    data class SshAgent(/*...*/) : CredentialRuntimeProjection
    data class UnixSocket(/*...*/) : CredentialRuntimeProjection
    data class ShortLivedToken(/*...*/) : CredentialRuntimeProjection
}
```

El nombre exacto debe evitar colisiones con tipos existentes.

## Plugins

Extiende providers por `ServiceLoader`/descriptor igual que otras SPI del proyecto. Un plugin declara provider id, credential kinds, projection kinds, lease/revocation/ACL, plataformas, requisitos y schema de configuración.

El core nunca contiene `if (providerId == "keepassxc")`.

`ContributedBindingFactory` actual devuelve `EnvEntry(SecretHandle)`: sirve para bindings materializados, pero no para sockets/signers. Añade un sibling versionado para proyecciones; no sobrecargues el SPI viejo con hacks.

## KeePassXC en PipelineK

### SSH Agent — primera vertical recomendada

KeePassXC puede cargar claves de su base en un agente OpenSSH existente y retirarlas al bloquear la base. El consumidor usa `SSH_AUTH_SOCK`; PipelineK sólo necesita proyectar el socket. Esto permite Git/SSH sin materializar la private key.

Objetivo futuro del plugin:

```text
withCredentials(ssh-agent binding)
  -> acquire lease
  -> verify socket/fingerprint
  -> overlay SSH_AUTH_SOCK
  -> run body
  -> release lease
```

La sintaxis exacta del binding sólo se documenta cuando el plugin esté implementado y certificado. Mientras tanto, PipelineK puede usar un `SSH_AUTH_SOCK` ya provisionado por el entorno mediante un `sh` normal.

### Freedesktop Secret Service

KeePassXC también puede exponer credenciales vía `org.freedesktop.secrets`. Un plugin PipelineK podría resolver ids desde KeePassXC, GNOME Keyring o KWallet. Si luego el valor entra por env/file, es `SCOPED_SECRET`, no `NON_EXPORTABLE`.

Es útil para storage externo, unlock humano y providers intercambiables.

## Linux: mecanismos útiles

- **OpenSSH agent**: P0; Git/SSH lo consumen directamente; ideal para proyección no exportable.
- **Secret Service**: P1 para tokens/passwords; recupera valor, por tanto scoped exposure.
- **OIDC/workload identity**: P2; preferible cuando el upstream lo soporta; token entregado al child = short-lived exposure.
- **systemd credentials**: útil para materialización efímera; si el child puede leerla sigue siendo scoped exposure.
- **Linux keyrings**: `user` es legible por userspace autorizado; `logon` no es legible por userspace, pero sólo sirve si existe un consumidor kernel compatible. No es backend universal para Git/curl.

## Eventos

Las integraciones deben emitir sólo metadata: providerId, credentialsId, projectionKind, purpose, leaseId, expiry y destino no secreto.

Eventos objetivo: `CredentialLeaseAcquired`, `CredentialProjectionApplied`, `CredentialUsed`, `CredentialProjectionReleased`, `CredentialLeaseRevoked`. Conserva `CredentialBound/Used/Unbound` por compatibilidad.

Nunca token, password, private-key bytes ni Authorization headers.

## Certificación de plugin

Todo provider/projection plugin debe probar discovery sin cambios core, unsupported fail-closed, acquire/release balanceado, cleanup ante fallo, cero secretos en events/journal/transcript, canary que realmente haga RED si se rompe la frontera, replay seguro, error tipado y removal sin reinterpretación.

Para SSH-agent además: socket válido, operación Git/SSH real, cero private-key materialization y fingerprint/policy incorrecta fail-closed.

## Regla para la skill

1. Detecta qué mecanismo necesita la herramienta.
2. Inspecciona providers/plugins realmente instalados.
3. Elige la proyección de menor exposición disponible.
4. Si sólo existe env/file, usa `withCredentials` y clasifícalo como scoped exposure.
5. Nunca inventes providers/proyecciones no presentes.

Fuentes externas útiles: KeePassXC documenta tanto Secret Service como integración SSH Agent; Linux documenta que las keyrings `user` son legibles por userspace y `logon` sólo por kernel.