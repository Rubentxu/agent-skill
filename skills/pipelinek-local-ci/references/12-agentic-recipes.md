# Recetas agentic

## 1. Adoptar PipelineK en un repo nuevo

```text
preflight
→ discover-ci-context
→ leer scripts/wrappers
→ diseñar stages
→ crear pipeline.kts
→ validate
→ positivo real
→ negativo discriminante
→ documentar qué CI remoto queda
```

## 2. Monorepo/poliglota

No fuerces una toolchain única. Ejemplo de forma:

```kotlin
pipeline {
    stages {
        stage("backend") {
            dir("backend") {
                sh("./gradlew --no-daemon check")
            }
        }
        stage("frontend") {
            dir("frontend") {
                sh("npm ci")
                sh("npm test")
            }
        }
    }
}
```

Sólo úsalo si existen exactamente `backend/gradlew` y `frontend/package.json`.

## 3. Feedback rápido

Durante edición:

```text
test afectado
→ consumidor afectado
→ stage focal si existe
```

En integración:

```text
pipelinek validate
→ pipeline completa
```

En release: delega matrices/certificación al release harness si el proyecto separa fast/slow lane.

## 4. Flaky real

Antes de retry:

1. reproduce;
2. identifica que la causa es transitoria;
3. fija máximo de intentos;
4. conserva eventos de cada intento.

No uses retry para conseguir verde sobre un fallo determinista.

## 5. Credencial

```text
credentials store
→ typed binding
→ env/file materialization temporal
→ command consumes
→ redacted events
→ cleanup
```

Nunca conviertas un token en literal del pipeline.

## 6. Migración desde CI alojado

Conserva sólo lo que no puede/conviene ejecutar localmente:

```text
remote trigger / OS matrix / distribution / deploy
```

La política de build/tests/gates vive en PipelineK para evitar dos CI divergentes.

## 7. Auto-fix con eventos

```text
StepFailed
→ classify
→ reproduce command
→ smallest fix
→ focused check
→ PipelineK gate
```

No arregles el último texto del log si el primer evento causal apunta a otra cosa.
