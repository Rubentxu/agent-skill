// Requiere: ./gradlew versionado y tasks check + assemble.
// Adapta el patrón de artefacto si tu proyecto no produce build/libs/*.jar.
pipeline {
    stages {
        stage("verify") {
            timeout(time = 20, unit = "MINUTES") {
                sh("./gradlew --no-daemon check")
            }
        }
        stage("package") {
            sh("./gradlew --no-daemon assemble")
            archiveArtifacts(
                artifacts = "build/libs/*.jar",
                allowEmptyArchive = false,
            )
        }
    }
}
