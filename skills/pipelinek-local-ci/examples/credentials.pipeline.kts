// Requiere que exista la credencial local "registry-token".
// Crear/rotar el valor con: pipelinek credentials add|rotate --kind secret-text registry-token
pipeline {
    stages {
        stage("credential-smoke") {
            withCredentials(
                StepSpec.CredentialsBinding.string("registry-token", "REGISTRY_TOKEN")
            ) {
                sh("test -n \"${'$'}REGISTRY_TOKEN\"")
                echo("credential binding present")
            }
        }
    }
}
