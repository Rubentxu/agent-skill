# Credentials y Secret Providers extensibles

PipelineK separa **consumo de credenciales** de **backend que las resuelve**.

## Modelo de uso

```text
credentialsId
→ withCredentials(binding)
→ CredentialProvider
→ projection/materialization
→ env/file temporal
→ body
→ cleanup
```

El pipeline no necesita conocer dónde vive el secreto.

## Hoy: provider local

La composición actual del CLI usa el provider local sobre el store de PipelineK.

```bash
pipelinek credentials add --kind secret-text registry-token
pipelinek credentials list
```

En DSL:

```kotlin
withCredentials(
    StepSpec.CredentialsBinding.string("registry-token", "REGISTRY_TOKEN")
) {
    sh("./scripts/publish.sh")
}
```

El body conoce `REGISTRY_TOKEN`, no el material del store.

## SPI existente

El runtime ya tiene un port provider-neutral `CredentialProvider` con responsabilidades equivalentes a:

```text
providerId
resolve(CredentialsId) -> SecretHandle
resolveToCredential(CredentialsId) -> Credential
close()
```

y una separación adicional para materialización de credenciales file-based.

`WithCredentialsExecutor` depende del SPI, no de `LocalSecretStore`.

## Importante: extensión externa actual

No asumas que Vault/AWS/etc. son hoy enchufables simplemente con `--plugin-jar`.

En el estado observado actual, el composition root del CLI sigue construyendo `LocalCredentialProvider` directamente. El propio SPI documenta discovery/selección genéricos como evolución posterior.

Por tanto:

```text
provider-neutral architecture = SÍ
generic user-selectable provider plugin = NO afirmar todavía
```

## Dirección correcta para providers plugin

Cuando PipelineK exponga hosting genérico, la forma debe preservar:

```text
CredentialProvider plugin
→ provider discovery/selection
→ capability declaration
→ WithCredentialsExecutor
→ existing projections/events/redaction
```

No debe requerir cambiar:

- domain;
- DSL de `withCredentials`;
- coordinator;
- cada Step consumidor;
- semántica durable.

## Providers candidatos

Como plugins/adapters externos:

- HashiCorp Vault;
- AWS Secrets Manager;
- Azure Key Vault;
- GCP Secret Manager;
- Kubernetes Secret/ServiceAccount/CSI;
- workload identity/OIDC;
- Jenkins Credentials adapter.

No todos requieren materializar bytes. Workload identity/CSI puede proyectar una capability sin que el control plane reciba el valor.

## Invariantes de seguridad

Todo provider debe mantener:

- referencias, nunca secretos, en event/provenance graphs;
- redaction antes de persistir/loggear;
- scopes/TTL mínimos cuando existan;
- cleanup de materialización temporal;
- errores fail-closed;
- nada de secretos en argv;
- auditoría de referencia/uso, nunca valor;
- linked secrets resueltos por el port común, no por lookups duplicados.

## Capabilities futuras

El modelo ya contempla capacidades como lease, revocation y ACL. No las simules si el provider no las implementa.

## Consecuencia para la skill

Cuando un proyecto pide secretos:

1. usa primero el provider soportado por la instalación;
2. si se pide backend externo, identifica si la instalación expone hosting de provider;
3. si no lo expone, marca la integración como capability gap de PipelineK;
4. no sustituyas silenciosamente el modelo por `sh("vault read ...")` o equivalente que exponga secretos.