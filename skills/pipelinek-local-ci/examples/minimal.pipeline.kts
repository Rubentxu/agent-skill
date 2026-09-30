// Smoke mínimo: no presupone ninguna herramienta del proyecto.
// Sirve para comprobar que la DSL compila y el runtime ejecuta un stage.
pipeline {
    stages {
        stage("preflight") {
            echo("PipelineK local CI is ready")
        }
    }
}
