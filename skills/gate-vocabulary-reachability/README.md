# gate-vocabulary-reachability

Audita que cada elemento del vocabulario que un sistema de autorización declara
sea realmente construible desde el código de producción.

**Cuándo:** al diseñar o revisar una pasarela de autorización, un motor de
políticas, un catálogo de permisos, o cualquier sistema donde una regla sobre un
valor que nadie construye pretende ser un control.

**Qué produce:** una tabla `elemento | declarado en | construido en | veredicto`
y, para cada elemento inerte, el sitio donde debería construirse y qué podría
hacer un atacante que hoy no puede.

**El caso que la justifica:** tres de trece acciones declaradas no las construía
ningún punto de evaluación. La política por defecto las concedía, así que ningún
test podía detectarlo y el operador podía escribir una política que las negara
sin efecto. La misma auditoría, aplicada al camino de base de datos, encontró que
la petición aceptaba el **destino** al que se prestaba la contraseña y que la
política no tenía dónde saying.

Empieza por [`SKILL.md`](SKILL.md).
