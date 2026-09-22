# Contribuir a agent-skill

## Diseño de una skill

1. Crear `skills/<slug>/SKILL.md` con front matter `name` y `description` y un objetivo delimitado; el `name` debe coincidir exactamente con `<slug>`.
2. Mantener la entrada breve y operativa. Las recetas por lenguaje, catálogos, plantillas y casos extensos pertenecen a `references/`, `assets/` y `examples/` **dentro de la propia skill**.
3. Definir criterios de cierre, evidencia mínima y límites operativos. Nunca atribuir ejecuciones, mediciones, permisos o verificaciones inexistentes.
4. No instalar herramientas, ejecutar cargas destructivas o enviar código/secretos a terceros sin autorización. Si hay scripts, deben describir sus efectos y tener tests aislados.
5. Añadir evaluaciones de activación y casos positivos, negativos y ambiguos; añadir tests para scripts. Los comandos de instalación de terceros son **sugerencias**, no prerequisitos implícitos.
6. Actualizar el catálogo del README raíz y, en su caso, el workflow para ejecutar los nuevos tests. Evitar referencias a rutas de otras skills.

## Flujo de cambios

Trabajar en una rama, ejecutar `python3 scripts/validate_skills.py` y los tests afectados. Abrir una PR con alcance, evidencias, limitaciones y efecto sobre compatibilidad. Antes de publicar una nueva versión, verificar instalación selectiva mediante el CLI `skills` en un entorno desechable y documentar los resultados; una ejecución local no acredita por sí sola que skills.sh haya indexado la skill.

No incorporar secretos, rutas personales, informes reales privados ni material de terceros sin permiso para redistribuirlo.
