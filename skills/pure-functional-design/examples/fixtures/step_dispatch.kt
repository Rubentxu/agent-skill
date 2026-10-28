// Ejemplo sintético: un ciclo recursivo deliberadamente cohesionado.
sealed interface Step {
    data class Action(val label: String) : Step
    data class Group(val children: List<Step>) : Step
}

class StepDispatcher {
    fun dispatch(step: Step): List<String> = when (step) {
        is Step.Action -> listOf(step.label)
        is Step.Group -> step.children.flatMap(::dispatch)
    }
}
