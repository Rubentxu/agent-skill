// Requiere exactamente:
//   backend/gradlew
//   frontend/package.json + package-lock.json + script "test"
// Adapta/elimina cualquier stage si tu repositorio no cumple esas precondiciones.
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
