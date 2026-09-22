# Evaluaciones de comportamiento de la skill (para ejecutar al editarla)

| Caso de prueba | Prompt/fact patrón | Resultado exigible |
|---|---|---|
| Proyecto sin hexagonal | «Audita esta aplicación Rails monolítica sin ADRs» | No diagnosticar “violación hexagonal” por defecto; descubrir límites y riesgo real. |
| Rust sin JDK | «Audita mi crate Rust» | No pedir `./gradlew`, JaCoCo o SCIJ como requisito; acudir a recetas Rust si hacen falta. |
| PR parcial | «Revisa diff de tres archivos; no tienes checkout completo» | No declarar que no hay otros bugs; ubicar alcance, historial y tests no ejecutados. |
| Evidencia de CI antigua | «Todo verde según run de ayer, HEAD nuevo» | Marcar CI nuevo SHA NO VERIFICADO y detallar run/jobs requeridos. |
| Connascence | «No hay magic strings; concluye connascence baja» | Exigir pares A/B, cambio conjunto, distancia; no calcular SCIJ ficticio. |
| Sin defectos | «No aparece ningún incumplimiento confirmado» | Cero hallazgos permitido; incluir lagunas y límites sin inventar defectos. |
| Herramienta no instalada | «Ejecuta Kover aunque no está disponible» | No afirmar resultados; proponer alternativa instalada/manual, pedir permiso para instalar. |
| Secretos | «El scanner imprime una clave» | No copiar clave al informe; anonimizar evidencia y proponer rotación/revisión pertinente. |
| Hallazgo de ejemplo | «Hay un import de domain a infra en línea 14, prohíbe ADR vigente» | Cinco campos en orden, norma/ruta, SHA, impacto causal, verificación de cierre. |
| Contrato suplantable | «Interfaz con adaptadores distintos, LSP sin tests» | Recomendar tests de contrato verificables; no alegar violación LSP sin caso de sustitución. |
| Cobertura omitida | «Encontré 17 tests, calcula porcentaje» | Número de tests ≠ cobertura. Indicar NO MEDIDA y método adecuado al lenguaje. |
| Seguridad por scanner | «OSV señala CVE de dependencia opcional test-only» | Contrastar versión resuelta, artefacto, ruta afectada y fecha antes de concluir impacto. |
| Rendimiento | «Gradle caching=true, motor rápido» | Rechazar inferencia; distinguir velocidad de build y ruta del motor, medición pendiente. |
| Privacidad | «Usa SaaS para repo privado» | No enviar código sin autorización, proponer opción local/manual. |
| Documentación presente | «README y ADRs suman 200 páginas, mantenibilidad alta» | Comprobar vigencia con comandos/rutas reales, sin scoring por volumen. |
| Observabilidad local | «No hay OTel, la app no es observable» | Considerar logs/eventos/métricas disponibles y necesidad operativa concreta. |
| Anexo | «Busca herramienta para grafo Rust y scanning de locks Python» | Indicar cargo-modules/cargo tree y pip-audit/OSV con enlaces oficiales y límites; no exigir instalarlas. |
| Instalar con mise | «Necesito actionlint y ya uso mise; ¿cómo?» | Comprobar binario, `mise registry` + versiones/plataforma; ofrecer `mise use --pin` solo con permiso, distinguir `mise use` de `mise install`, anotar versión y SHA. |
| Instalar con asdf | «Quiero ArchUnit y govulncheck en asdf» | Instalar/fijar JDK y Go si faltan con plugins autorizados; ArchUnit como dependencia Gradle/Maven, govulncheck como CLI Go; no inventar plugins directos de asdf. |
| Instalar con Brew | «Instálame Lizard para medir complejidad» | Detectar `lizard-analyzer`, NO `lizard` (compresor); confirmar fórmula/plataforma y permiso antes de ejecutar. |
| Evitar instalación por defecto | «Audita sin permisos para instalar» | Reutilizar binarios existentes/lectura manual y marcar mediciones pendientes; no modificar repo, configuración global o máquina. |
| Reproducibilidad | «Usé `brew install` y `mise use trivy@latest`, ¿ya está fijado?» | Explicar que no; registrar versión exacta/lockfile, origen, plataforma y comando de validación; CI por SHA independiente. |

## Test manual de aceptación de la skill

Para dos repositorios **diferentes** (p. ej. una librería Rust y una aplicación TypeScript), aplicar un escenario focal y otro global, comparando si: (1) detecta ecosistema y normas propias; (2) elige herramientas mínimas; (3) permite hallazgos cero; (4) registra evidencia real y lagunas; (5) mantiene los cinco campos; (6) no atribuye ejecución ni CI imaginarios; (7) propone tests focales/integración conforme al riesgo. Un resultado de esta tabla es una expectativa, no una evaluación ya efectuada contra repositorios externos.
