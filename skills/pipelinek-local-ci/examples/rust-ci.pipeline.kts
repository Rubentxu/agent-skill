// Requiere: Cargo.toml y componentes/tools usados abajo.
// En workspace complejo adapta --all-features/--workspace a su contrato real.
pipeline {
    stages {
        stage("checks") {
            parallel {
                branch("fmt") {
                    sh("cargo fmt --check")
                }
                branch("clippy") {
                    sh("cargo clippy --all-targets --all-features -- -D warnings")
                }
                branch("test") {
                    sh("cargo test --all-features")
                }
            }
        }
        stage("build") {
            sh("cargo build --release")
        }
    }
}
