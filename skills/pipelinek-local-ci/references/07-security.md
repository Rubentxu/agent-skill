# Credenciales y seguridad

## Principio

Los secretos deben entrar como capacidades/bindings, no como literales, argumentos visibles o texto de logs.

## Store local

La CLI actual soporta:

```text
pipelinek credentials add [--kind <kind>] <id>
pipelinek credentials list
pipelinek credentials remove <id>
pipelinek credentials rotate [--kind <kind>] <id>
```

La entrada de valores es interactiva/segura según el kind. No automatices pegando secretos en la línea de comandos.

Si el proyecto usa store alternativo, respeta `PIPELINE_CREDENTIALS_STORE` según su gobernanza.

## Binding en pipeline

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

## Anti-patrones

- `sh("tool --token=SECRET")`;
- `echo("token=$TOKEN")`;
- persistir variables secretas en artifacts;
- escribir el store dentro del repo;
- desactivar redacción para depurar;
- convertir fallo de credencial en `|| true`.

## Revisión agentic

Ante un fallo de credencial, el agente puede reportar id/kind/binding/evento, pero nunca valor materializado. Si necesita comprobar presencia, usa `credentials list`, no lectura directa del fichero cifrado.
