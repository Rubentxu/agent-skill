# Lente: diseñar ADTs e invariantes que resistan estados ilegales

**Pregunta:** ¿qué combinaciones de datos y transiciones nunca deberían poder expresarse? **Señales:** `invalid-state`, `domain-ambiguity`, `duplicate-logic`.

## Procedimiento

1. Listar estados legales, estados ilegales, transiciones y errores **del caso de uso**; clasificar product types (campos simultáneos) y sum types (alternativas excluyentes).
2. Exponer tipos de valor (ids, cantidades, nombres) para impedir mezcla accidental; definir smart constructors que devuelvan `Result`/`Either`/`Raise` si fallan por datos del dominio.
3. Reemplazar, cuando exista mejora demostrable, `String status + Boolean isOpen + nullable payload` por variantes que solo contengan datos válidos por estado.
4. Decidir si tipestate con estados en el tipo aporta suficiente garantía para superar costes de serialización, eventos persistidos, APIs públicas y crecimiento del número de tipos; si no, usar enum/sealed y reducer exhaustivo.
5. Expresar transiciones como función total de `State × Command × Context` a éxito/error tipado. Cuando se rechaza una transición, mantener intacto el estado; nunca suprimir la causa.
6. Distinguir validación de entrada (`parse`) de construcción de un valor de dominio ya validado. Hacer imposibles estados ilegales **en el ámbito controlable**, no pretender que entrada externa o almacenamientos viejos sean válidos antes de validarlos.

**Criterios de cierre:** todas las variantes tratadas sin fallback silencioso; constructores controlados; errores y transiciones claras; migración/compatibilidad explícita. **No aplica:** value objects triviales que no aportan restricción o composición.

**Antipatrón:** enum de estados con ocho banderas adyacentes; entidad válida solo "si se llama primero a init"; usar `unwrap`/`!!` para esquivar un modelo incorrecto.
