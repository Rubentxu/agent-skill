// Ejemplo autocontenido Kotlin: decisión pura y errores de dominio tipados.
sealed interface DocState {
    data class Draft(val id: String) : DocState
    data class Published(val id: String, val version: Long) : DocState
}

sealed interface DomainError {
    data object InvalidVersion : DomainError
    data object AlreadyPublished : DomainError
}

data class DomainEvent(val id: String, val version: Long)
data class Decision(val next: DocState, val events: List<DomainEvent>)

sealed interface DecisionResult {
    data class Accepted(val value: Decision) : DecisionResult
    data class Rejected(val reason: DomainError) : DecisionResult
}

fun decide(state: DocState, version: Long): DecisionResult = when {
    version <= 0L -> DecisionResult.Rejected(DomainError.InvalidVersion)
    else -> when (state) {
        is DocState.Draft -> DecisionResult.Accepted(
            Decision(DocState.Published(state.id, version), listOf(DomainEvent(state.id, version)))
        )
        is DocState.Published -> DecisionResult.Rejected(DomainError.AlreadyPublished)
    }
}

fun main() {
    val original = DocState.Draft("doc-1")
    val output = decide(original, 1L)
    check(output is DecisionResult.Accepted)
    check(output.value.next == DocState.Published("doc-1", 1L))
    check(original == DocState.Draft("doc-1"))
}
