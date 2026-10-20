# Lente: UAT efímero y pertinente en navegador

Usar navegador/herramientas YA presentes. No instalar suites ni crear harness persistente por defecto. Crear escenarios UAT efímeros focalizados y borrarlos o promover solo la regresión más útil al terminar.

Para nueva app: entrar → actuar → recibir feedback de acierto y fallo → reintentar → completar → continuar/reiniciar. Para existing app añadir rutas afectadas.

Regresiones mínimas de Atlas Quest: (1) sesión diaria agotada → práctica libre con tarjeta real; (2) reinicio de ronda tras progreso sin borrado; (3) fallo marcado + recuperación no desaparece por simple flip; (4) respuesta escrita errónea guarda fallo; (5) export/import/migración y reapertura; (6) mapa usable con ratón/touch/teclado.

- Confirmar efecto, no solamente que `click()` no lanza excepción. Aserciones a estado/dom y persistencia visible.
- Test de resolución pequeña y media; foco, sin red, `prefers-reduced-motion` cuando relevante.
- Separar `PASSED|FAILED|NOT_RUN|BLOCKED`, con revisión/archivo y entorno. Un `SKIP` nunca se convierte en PASS.
- Mantener únicamente pruebas que detecten garantías críticas y fallos que ya ocurrieron; UAT visual/exploratorio efímero puede descartarse tras evidencia.

[Plantilla UAT](../../assets/uat-scenarios.md).
