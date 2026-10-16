# Diagnóstico rápido del DSL LikeC4

La sintaxis depende de la versión instalada de LikeC4; **validar con el CLI/container real** y leer su error antes de corregir. No arreglar un fallo de `kinds` alterando entidades o falsificando arquitectura.

Patrón seguro para los ejemplos de esta skill: declarar todos los `element` kinds que después se usan en `model`, incluidos los **tipos base** `actor`, `system`, `container` y `component` cuando aparezcan; declarar también `relationship` kinds personalizados antes de invocarlos, si la gramática instalada lo exige.

```likec4
specification {
  element actor
  element system
  element container
  element component
}
model {
  customer = actor 'Customer'
  platform = system 'Platform' {
    api = container 'API' {
      engine = component 'Engine'
    }
  }
  customer -> platform.api 'uses'
}
views {
  view index { include * }
}
```

No combinar aliases no registrados con kinds base. Si falla la primera validación, comprobar (1) versión, (2) declaración de cada kind usado, (3) relación/scope, (4) esquema de vista; corregir sintaxis de la fuente **derivada**, nunca tocar el checkout del código investigado.
