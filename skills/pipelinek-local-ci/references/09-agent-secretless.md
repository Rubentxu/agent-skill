# PipelineK + Agent Secretless Vault (ASV)

## Objetivo

Usa ASV cuando un pipeline necesite autenticar una operación pero el agente **no deba recibir el material secreto**.

La integración fuerte es:

```text
coding agent
   ↓
ASV session
   ↓
PipelineK
   ↓
normal sh/git/ssh/gh/curl command
   ↓
socket / signer / proxy / surrogate / semantic operation
   ↓
ASV broker
   ↓
real credential
```

El secreto permanece en el broker. PipelineK conserva su función: orquestar ejecución, durabilidad, eventos y outcomes.

## Regla de clasificación

No llames "secretless" a cualquier mecanismo que oculte el secreto en disco.

| Mecanismo | ¿bytes reales entran en el árbol del agente/proceso? | Postura |
|---|---:|---|
| ASV SSH signer / protocolo de firma | No | STRONG_SECRETLESS |
| ASV proxy/service connector | No | STRONG_SECRETLESS |
| ASV surrogate + broker-side replacement/signing | No | STRONG_SECRETLESS |
| token temporal entregado al proceso | Sí | SHORT_LIVED_EXPOSURE |
| worker aislado que recibe secreto | Sí, sólo worker | ISOLATED_PROCESS_EXPOSURE |
| PipelineK `withCredentials` env/file binding | Sí, proceso hijo | PROCESS_EXPOSURE con redacción/lifecycle |
| secret env/file directo | Sí | RAW_PROCESS_EXPOSURE |

`withCredentials` de PipelineK sigue siendo útil y mucho mejor que literales/argv: tipa bindings, limita scope, limpia material y redacta eventos. Pero no es equivalente a un signer/proxy ASV frente a un agente hostil.

## Patrón recomendado hoy: envolver PipelineK

Comprueba primero la CLI ASV instalada:

```bash
asv --help
asv status
```

No presupongas comandos de una spec futura. La build actual de ASV debe demostrar qué integraciones ofrece.

Para el vertical SSH ya implementado por `asv run`:

```bash
asv run -- pipelinek validate pipeline.kts

asv run -- pipelinek run \
  --workspace . \
  --db "$STATE/run.sqlite" \
  --control-root "$STATE/control" \
  pipeline.kts
```

`asv run` conserva el exit del hijo, elimina variables sensibles conocidas del entorno heredado y suministra un `SSH_AUTH_SOCK` de sesión.

Dentro de PipelineK los comandos siguen siendo normales:

```kotlin
stage("remote-read") {
    sh("git ls-remote --exit-code origin HEAD")
}
```

Para una operación mutadora como `git push`, mantén el mismo modelo pero aplica las reglas/operator gates del repositorio. ASV resuelve autenticación; no convierte una operación irreversible en preautorizada.

## Por qué NO crear un CredentialProvider ASV que devuelva secretos

El SPI actual de PipelineK `CredentialProvider` resuelve a `SecretHandle` / `Credential`. Un adapter:

```text
ASV -> CredentialProvider.resolve() -> SecretHandle -> child env
```

haría que PipelineK/proceso hijo poseyera los bytes. Eso rompe la propiedad fuerte de ASV.

Sólo sería aceptable como modo de compatibilidad explícitamente degradado.

La integración futura correcta entre ambos productos es operation/capability-oriented:

```text
PipelineK external step/directive
    -> ASV capability/session request
    -> non-secret handle/socket/surrogate
    -> normal process/proxy/signer
```

No `getSecret()`.

## Diseño futuro para Plugin SDK

Cuando el Plugin/Directive SDK de PipelineK lo permita, una integración oficial puede aportar:

- `asvSession(...){ }` o directiva equivalente que proyecte **sólo referencias no secretas**;
- capability admission antes del stage;
- eventos `SecretlessSessionStarted/Ended`, `CapabilityGranted/Denied` sin payload secreto;
- binding de `SSH_AUTH_SOCK`, proxy endpoint o surrogate;
- cleanup/revocation en `finally`;
- replay que nunca serialice bearer material.

No debe existir un step genérico "ejecuta shell arbitraria con este secreto". ASV prohíbe ese patrón por diseño.

## KeePassXC: dónde encaja

KeePassXC puede actuar como proveedor Freedesktop Secret Service en Linux. Eso es útil como **almacén humano / fuente de ingestión**, no como data plane para el agente.

Secret Service expone operaciones que devuelven secretos a clientes. Por tanto:

```text
agent -> secret-tool / D-Bus Secret Service -> raw secret
```

NO es strong-secretless.

Patrón aceptable:

```text
human unlocks KeePassXC
       ↓
trusted ASV ingest/import helper
       ↓
ASV vault/broker
       ↓
agent session gets capability, never value
```

Reglas:

- el agente no ejecuta `keepassxc-cli show`, `secret-tool lookup` ni equivalente para recuperar valores;
- no pases master password ni entry password por argv;
- preferir prompt/secure ingest del operador;
- si el agente corre bajo el mismo UID y puede conectar al bus de sesión, KeePassXC/Secret Service por sí solo NO es una frontera suficiente contra un agente hostil;
- una frontera fuerte requiere aislamiento adicional (por ejemplo broker dedicado/UID separado y políticas de proceso) o importar el secreto a ASV antes de lanzar el agente.

## Mecanismos Linux útiles

### SSH agent / PKCS#11 / FIDO2 / TPM

Son la referencia ideal cuando la operación puede expresarse como firma. El cliente solicita una operación criptográfica; la clave privada no necesita salir.

### Freedesktop Secret Service / GNOME Keyring / KWallet / KeePassXC

Buenos almacenes UX para el operador. No son por sí mismos secretless frente a un cliente que puede pedir `GetSecret/GetSecrets`.

### Linux kernel keyrings

Útiles para almacenamiento/control de acceso de kernel y sesiones. Los tipos `user` son legibles desde userspace con permisos adecuados; no los trates como frontera frente al mismo agente. Los `logon` keys son no-legibles desde userspace, pero sólo ayudan cuando un consumidor del kernel puede usar la clave: no sustituyen un broker HTTP/SSH genérico.

### systemd credentials

Útiles para arrancar **el broker** u otro servicio aislado con material protegido/encrypted-at-rest. Si se entregan a la carga de trabajo que ejecuta el agente, esa carga de trabajo termina poseyendo el secreto: clasificar como exposición, no strong-secretless.

## Elección rápida

```text
¿La operación puede usar firma?
  sí -> SSH agent / signer / PKCS#11-like
  no
  ↓
¿protocolo/API proxyable?
  sí -> ASV service/protocol proxy
  no
  ↓
¿provider ofrece identidad temporal?
  sí -> broker mint; si token entra en child = SHORT_LIVED_EXPOSURE
  no
  ↓
¿tool legacy debe recibir el valor?
  sí -> isolated exec + egress confinement
  no -> UNSUPPORTED
```

## Agentic preflight

Antes de ejecutar un pipeline con autenticación:

```bash
command -v asv || true
asv --help 2>/dev/null || true
asv status 2>/dev/null || true

printf 'PipelineK: '
pipelinek version
```

Después registra sólo:

```text
ASV available: yes/no
session mode: strict/degraded/none
integration: SSH signer / proxy / short-lived / isolated / PipelineK binding
credential id/capability id: metadata only
PipelineK runId/outcome
```

Nunca el valor secreto.

## Fuentes de diseño

- ASV: `Rubentxu/agent-secretless`, especialmente `04-SHELL-FIRST-INTEGRATION.md`, `05-CREDENTIAL-ACCESS-MODES.md`, `06-TRANSPARENT-BRIDGE-EBPF.md` y `10-CLI-MCP-API.md`.
- KeePassXC Secret Service: https://keepassxc.org/docs/KeePassXC_UserGuide#_secret_service_integration
- Freedesktop Secret Service: https://specifications.freedesktop.org/secret-service/latest/
