# delivery-first-testing

Skill única y portable con orquestador en `SKILL.md`, lentes consultadas a demanda, catálogo y navegación HATEOAS-like local. Adaptación del patrón de `cognicode-diagrams` de Rubentxu/agent-skill, centrada en rentabilidad de tests y UAT efímeros.

La skill **no** es un ejecutor de CI: ofrece lentes para selección, data-driven y mutation testing selectivo, además de una [plantilla de Harness Base](assets/test-harness-base/README.md) copiable a `test-harness/` o `v2/test-harness/`. Se versiona la base, no los escenarios efímeros. La plantilla proporciona ejecución aislada, timeout, evidencias locales y limpieza de procesos/contenedores registrados.

## Activación

«Desarrolla esta feature con pruebas rápidas», «los UAT se rompen al refactorizar», «qué conservar como regresión», «audita costes del harness», «prepara merge», «certifica release».

## Uso

```bash
python3 skills/delivery-first-testing/scripts/affordances.py \
  skills/delivery-first-testing/examples/session-feature.json
python3 -m unittest discover -s skills/delivery-first-testing/tests -p 'test_*.py' -v
```

El router **no ejecuta tests ni escribe en el repo**. La respuesta JSON solo anuncia acciones que el agente puede considerar según observaciones supplied. La ejecución real usa los comandos y políticas del repositorio elegido; ejemplos no autorizan cambios en otros repositorios.

## Regla de conservación

UAT temporal aceptado ≠ regresión automática. Conservar únicamente contratos públicos o riesgos cuya protección no esté cubierta con una prueba más simple. Seguridad, persistencia, durabilidad, concurrencia, privacidad y distribución requieren una garantía duradera, pero no necesariamente el E2E original.

## Instalación de la skill desde el repo publicado

```bash
npx skills add Rubentxu/agent-skill --skill delivery-first-testing --agent opencode
```

Probar la plantilla sin infraestructura externa:

```bash
bash skills/delivery-first-testing/tests/test_harness.sh
```

La publicación por PR y su descubrimiento por skills.sh son validaciones separadas. No se han ejecutado suites reales de CogniCode, PipelineK, Fabric o agentchanges como parte de esta skill; solo tests unitarios de navegación/catálogo.
