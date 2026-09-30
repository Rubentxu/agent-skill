// Requiere: pyproject.toml + uv.lock y ruff/pytest declarados para el proyecto.
pipeline {
    stages {
        stage("install") {
            sh("uv sync --frozen")
        }
        stage("checks") {
            parallel {
                branch("lint") {
                    sh("uv run ruff check .")
                }
                branch("test") {
                    sh("uv run pytest")
                }
            }
        }
    }
}
