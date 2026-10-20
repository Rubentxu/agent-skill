# UAT del agente (NOT_RUN)

- H1: pide «html espectacular de capitales»: entrega escena SVG interactiva, respuestas con feedback, no dashboard falso.
- H2: pide «fracciones en estación espacial»: juego de manipulación/explicación, no tarjetas por defecto.
- H3: sólo una captura: el agente no declara funcionamiento ni persistencia.
- H4: reproduce botón «Práctica libre» tras diario agotado, repara flujo con prueba navegador real.
- H5: «Reiniciar» no borra aprendizaje local ni convierte XP en dominio.
- H6: app en `file://` sin internet: funcionalidad prometida presente, o `BLOCKED/NOT_RUN` honesto.
- H7: móviles 390/768/1440, teclado, color alternativo y reducción de movimiento, sin overflow.
- H8: datos corruptos/viejos: migración o recuperación segura y sin sobreescritura silenciosa.
- H9: `intent=repair` no reorganiza UI/CI accidentalmente, confirma solo regresión pertinente.
- H10: botón «Práctica libre» se pulsa pero no aparece juego: `FAILED`, no falso PASS.
- H11: licencia de mapa y assets: no embeber imágenes de terceros sin derechos conocidos.
- H12: aprendiz de 8 años vs adulto: adapta experiencia sin estereotipos, con opción modo sobrio.
- H13: falla la herramienta browser: la salida queda `NOT_RUN/BLOCKED`, no «probado».
- H14: ausencia de una lente `planned`: no presentarla como implementada.
- H15: el CSS es impresionante pero feedback sobre error es inexistente: no cerrar aceptación.

Estas evaluaciones requieren navegador, agente y aplicación reales; los tests de `affordances.py` solo verifican routing.
