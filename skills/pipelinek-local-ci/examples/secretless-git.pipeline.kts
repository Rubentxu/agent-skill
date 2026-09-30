// Secretless Git example.
//
// Intent:
//   - PipelineK orchestrates a normal Git command.
//   - Authentication, when required, is provided by the process environment
//     (for example SSH_AUTH_SOCK from `asv run -- pipelinek ...`).
//   - The pipeline never reads or prints a private key/token.
//
// Recommended invocation when Agent Secretless Vault is available:
//
//   asv run -- pipelinek validate examples/secretless-git.pipeline.kts
//   asv run -- pipelinek run --workspace . examples/secretless-git.pipeline.kts
//
// The command is read-only. Replace it with a mutating Git operation only when
// repository governance explicitly authorizes that operation.

pipeline {
    stages {
        stage("remote-auth-check") {
            sh("git remote -v")
            sh("git ls-remote --exit-code origin HEAD")
        }
    }
}
