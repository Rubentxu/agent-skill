# Patrón: atlas vivo / mapa interactivo

Acción: explorar, localizar, comparar vecindad/distancias y recordar; evidencia: identifica sin marcador después de la explicación. Render: SVG de geometría válida con zoom, tooltips accesibles, estados visitado/desconocido/dominado y alternativa en lista. Un vuelo, halo o foco en capital **muestra una relación espacial**.

Desafío: mapa oculta respuesta y pide elegir región; error resalta zona general como pista, después la persona intenta de nuevo. Microestados: seleccionar, foco, descubrir, fallar, volver, completar. No probar dominio si la respuesta permanece visible.

Tener en cuenta países ambiguos, microestados, licencias y límites de geometría. Evitar tap targets minúsculos en móvil; usar accesos alternativos por lista/selector.
