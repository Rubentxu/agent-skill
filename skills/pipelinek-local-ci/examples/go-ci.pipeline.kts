// Requiere: go.mod. Añade build tags/race/options sólo si son contrato del repo.
pipeline {
    stages {
        stage("checks") {
            parallel {
                branch("vet") {
                    sh("go vet ./...")
                }
                branch("test") {
                    sh("go test ./...")
                }
            }
        }
        stage("build") {
            sh("go build ./...")
        }
    }
}
