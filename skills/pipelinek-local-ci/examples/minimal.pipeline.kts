pipeline {
    stages {
        stage("Build") {
            sh("./project-wrapper build")
        }

        stage("Tests") {
            sh("./project-wrapper test")
        }
    }
}
