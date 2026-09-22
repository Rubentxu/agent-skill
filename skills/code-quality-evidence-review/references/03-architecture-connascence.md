# Arquitectura, SOLID, diseño funcional y connascence (métodos)

## 1. Primero descubre la arquitectura **real**

Traza actores/entradas → casos de uso → dominio/contratos → adaptadores/efectos → integración. Si el repositorio no declara arquitectura hexagonal, no la impongas: identifica límites que efectivamente importan a estabilidad, pruebas y despliegue. Si sí se declara, enumera los puertos y qué dependencias permite **la versión vigente** de la arquitectura.

Verifica dos grafos diferentes: (a) dependencias declaradas en package managers/build por módulo, incluido `test/runtime`, (b) referencias semánticas entre símbolos, interfaces, herencia, anotaciones, generación de código y registro/DI. Una flecha de build sola no demuestra que el código la usa; un `import` ausente no descarta tipos fully qualified, reflexión, SPI/DI, templates, metaprogramación o código generado. Dibuja aristas explícitas `origen → destino`, explica reglas `permitida/prohibida/desconocida` y proporciona par de archivos/manifest con su SHA.

Para hexagonal investiga: ¿un caso de uso conoce `HttpClient`, ORM, UI, CLI, SDK cloud o runtime específico? ¿un port expone tipos de framework que dificultan un segundo adaptador? ¿un adaptador implementa contratos internos o el dominio debe importarlo para compilar? ¿dónde se decide la composición? ¿se filtra I/O a funciones aparentemente puras? No califiques de defectuosa una excepción documentada sin analizar su impacto.

## 2. SOLID y tipado funcional aplicados, no rituales

| Criterio | Evidencia necesaria | Antipatrón de auditoría |
|---|---|---|
| SRP/cohesión | Cambios de distinta naturaleza obligan a editar el mismo componente; identificar razones de cambio y dependencias reales. | «Clase grande = varias responsabilidades» sin probarlas. |
| OCP/DIP | Añadir implementación requiere modificar núcleo o introducir dependencia externa; comparar camino de extensión vigente. | Exigir interfaces para objetos locales estables. |
| LSP | Un consumidor falla al sustituir implementación según contratos/pre-postcondiciones; pruebas contractuales cruzadas. | Equiparar toda excepción en una subclase con violación LSP. |
| ISP | Consumidor debe depender de métodos/efectos que no usa y ello genera cambio/carga. | Dividir cualquier interfaz en unidades minúsculas. |
| ADTs y errores | Estados semánticamente distintos representados indistinguiblemente causan rama insegura o caso omitido. | Pedir `sealed` en lenguajes sin constructo equivalente o por estética. |
| Inmutabilidad/pureza | Entrada → salida reproducible, efectos y estado mutante localizados; tests/inspección. | Declarar “impuro” un adaptador de I/O cuyo papel es precisamente producir efectos. |

Examinar nulls, Any/casts, strings mágicos y boolean flags **en contratos relevantes**, no contar apariciones indiscriminadamente. Null puede representar ausencia legítima; un enum/ADT puede agregar complejidad cuando no hay estados ilegales ni evolutivos. Un `else` en un `match/when` exhaustivo puede esconder nuevas variantes, pero puede ser legítimo en protocolos abiertos.

## 3. Connascence: unidad de análisis = relación

Para cada hallazgo documenta **elemento A**, **elemento B**, qué acuerdo comparten, qué cambio en A obliga a cambiar B, distancia entre ambos (mismo método, paquete, servicio, despliegue), mecanismo de acoplamiento y test que lo expone.

- **Nombre:** dos partes deben conocer identificador literal; ¿compilador/contrato lo protege o hay key strings dispersos?
- **Tipo:** hay acuerdo sobre representación; tipos expresivos pueden hacer el acuerdo más seguro, pero no lo eliminan. Identifica conversión/compatibilidad.
- **Significado:** mismo valor simbólico/significado implícito (ej. `"2"` interpretado de forma diferente); identifica quién define la semántica.
- **Posición:** orden de args/campos/eventos importa; posiciones fijadas y validadas pueden ser un protocolo legítimo, no un defecto automático.
- **Algoritmo:** ambas partes replican algoritmo/conversión compatible; captura versión o vector de prueba de referencia.

Si se examina connascence *dinámica*, señalar por separado (ej. orden, ejecución, timing, identidad); un análisis de repositorio puramente estático no acredita comportamiento temporal. No existe una métrica de connascence universal ni un umbral válido para todos los lenguajes. **SCIJ**: emplear solo una herramienta existente comprobada, con definición matemática, alcance, versión y ejecución; si no, «no medido», sin proponer un comando inventado.

## 4. Evidencia de acoplamiento

- Analiza ciclos por componente/módulo, fan-out directo e indirecto y cambios históricos conjuntos, normalizando el grafo según el mismo conjunto de nodos; no sumes archivos generados indiscriminadamente.
- Para duplicación, distingue clones textuales de duplicación de responsabilidad/semántica: dos implementaciones pueden estar previstas por compatibilidad; intenta demostrar divergencia real en inputs o reglas de negocio.
- Para deuda, separa violación del diff actual, legado, propuesta de migración y coste de retirada. Prefiere reglas arquitectónicas ejecutables que expresen el límite demostrado, no un diagrama sin enforcement.
