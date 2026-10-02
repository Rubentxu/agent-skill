# retrospective-cycle-audit

Audita un ciclo de desarrollo ya escrito antes de continuar sobre él.

**Cuándo:** al retomar trabajo de otro agente, tras una pausa, o cuando un ciclo
terminó "en verde" y nadie sabe si algo se rompió de verdad.

**Qué produce:** una lista de hallazgos clasificados, cada uno con la
observación que lo falsaría, y un apartado `siguiente` accionable.

**El caso que la justifica:** un ciclo anterior cerró dos hallazgos de seguridad
y una release con el CI completamente verde. La auditoría posterior encontró que
tres de las trece acciones de la política nunca llegaban al motor — y que un
comentario en el código afirmaba por escrito que sí llegaban. Ese comentario era
la única garantía del invariante, y por eso no había nada que revisar.

Empieza por [`SKILL.md`](SKILL.md).
