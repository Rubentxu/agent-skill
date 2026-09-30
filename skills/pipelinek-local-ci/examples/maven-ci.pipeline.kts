// Requiere: ./mvnw versionado. Ajusta target/*.jar si el packaging es distinto.
pipeline {
    stages {
        stage("verify") {
            timeout(time = 20, unit = "MINUTES") {
                sh("./mvnw -B -ntp verify")
            }
        }
        stage("package") {
            archiveArtifacts(
                artifacts = "target/*.jar",
                allowEmptyArchive = false,
            )
        }
    }
}
