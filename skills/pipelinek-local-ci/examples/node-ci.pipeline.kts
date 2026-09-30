// Requiere: package-lock.json y scripts npm reales: lint, test, build.
// Antes de usar: inspecciona package.json; elimina/renombra cualquier script inexistente.
pipeline {
    stages {
        stage("install") {
            sh("npm ci")
        }
        stage("checks") {
            parallel {
                branch("lint") {
                    sh("npm run lint")
                }
                branch("test") {
                    sh("npm test")
                }
            }
        }
        stage("build") {
            sh("npm run build")
        }
    }
}
