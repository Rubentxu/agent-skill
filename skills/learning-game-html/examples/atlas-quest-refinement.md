# Ejemplo UAT de mejora real: Atlas Quest 3.1

Observación del archivo aportado: HTML autocontenido ~247 KB, un `<script>` y un `<style>`, SVG con geometrías, estados de repaso, logros, mini-siluetas, `localStorage`, modo libre y reinicio. Esta es evidencia estática, **no test dinámico**.

**No romper**: filtros de continentes, pasaporte, pistas mnemotécnicas, estados de fallo y `marked`, sesiones diarias y libres, export/import, progreso previo.

**Arte**: conservar escena central de globo/mapa y convertirla en narrativa (zoom breve, ruta iluminada, capital revelada después de respuesta) y feedback visual. Evitar rehacer un dashboard por gusto.

**Prueba funcional real**: agotar cuota diaria → click «Práctica libre» → cola no vacía y nueva tarjeta; luego «Reiniciar» → misma modalidad reinicia ronda sin borrar mastery. Comprobar reabrir y exportar. Una captura estática no verifica este contrato.

**Arquitectura**: extraer durante desarrollo `countries/data`, `session/reducer`, `storage/migrate`, `scene/svg`, `ui/events`; si el usuario quiere una sola página, empaquetar en un HTML con fuentes inline. No crear un motor de juegos ni pipeline CI nuevo.
