# Publicar la colección en Rubentxu/agent-skill

Repositorio público existente: <https://github.com/Rubentxu/agent-skill>.

## Validar localmente

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m unittest discover -s skills/code-quality-evidence-review/tests -p 'test_*.py' -v
```

## Clonar y actualizar (repositorio existente)

```bash
git clone https://github.com/Rubentxu/agent-skill.git
cd agent-skill
# Incorporar cambios por PR (rama feature) y ejecutar validaciones.
git switch -c feat/nueva-skill
git add .
git commit -m 'feat: add skill'
git push -u origin feat/nueva-skill
```

Abre una PR hacia `main`, verifica las comprobaciones del nuevo SHA y fusiona sin `--force`. Evita sobrescribir cambios remotos.

## Instalar solo la skill de calidad

```bash
npx skills add Rubentxu/agent-skill --list
npx skills add Rubentxu/agent-skill --skill code-quality-evidence-review --agent opencode
```

Publicar en GitHub no garantiza que skills.sh indexe inmediatamente la skill. Comprueba por separado el descubrimiento del CLI y, más tarde, el catálogo.
