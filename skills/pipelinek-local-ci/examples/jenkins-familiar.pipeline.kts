// Demo Jenkins-familiar usando sólo superficies actualmente estables.
// Requiere ejecutarse en un checkout Git con README.md.
pipeline {
    stages {
        stage("scoped-verify") {
            withEnv(listOf("CI=true", "PIPELINEK_DEMO=1")) {
                timeout(time = 2, unit = "MINUTES") {
                    retry(count = 2) {
                        sh("test -f README.md")
                    }
                }
            }
        }

        stage("parallel-checks") {
            parallel {
                branch("git") {
                    sh("git status --short")
                }
                branch("filesystem") {
                    sh("test -d .")
                }
            }
        }

        stage("artifact") {
            sh("mkdir -p build")
            writeFile(file = "build/pipelinek-demo.txt", text = "pipelinek-demo-ok\n")
            stash(name = "demo-output", includes = "build/pipelinek-demo.txt")
            archiveArtifacts(
                artifacts = "build/pipelinek-demo.txt",
                allowEmptyArchive = false,
            )
        }
    }
}
