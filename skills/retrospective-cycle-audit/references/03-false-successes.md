# Falsos éxitos y tests ciegos

Un falso éxito es una operación que devuelve el resultado que se le pidió **sin haber cumplido el objetivo para el que se pidió**. Es peor que un fallo: consume el presupuesto de confianza del sistema, y un sistema cuyo verde no significa nada acaba con un verde que nadie mira.

## Los cuatro patrones

### 1. El `match` incompleto

```rust
// CEGA: también pasa con un éxito.
if let Response::Error { code, .. } = &response {
    assert_ne!(code, ErrorCode::Upstream);
}

// VE. Requiere el camino exacto.
match response {
    Response::Error { code, message } => {
        assert_eq!(code, ErrorCode::Denied);
        assert!(message.contains("wrong class"), "razón: {message}");
    }
    other => panic!("se esperaba el rechazo y llegó {other:?}"),
}
```

El patrón `if let` + `assert_ne` sobre el código de error tiene una forma de fallo característica: **una respuesta de éxito la satisface sin ejecutar una sola aserción**. Se丝 ha visto en la vida real en un test que llevaba meses en verde.

### 2. El default que concede

Si el permiso por defecto concede, la política por defecto permite, o el flag por defecto está activo, **toda prueba a través de esa puerta pasa exista o no**. Se detecta borrando la implementación:

```bash
# ¿esta prueba really depende de esta puerta?
# neutraliza la puerta y mira
git stash
# ejecuta la prueba
```

Sigue verde ⇒ la prueba no dependía de la puerta. Eso es un hallazgo, no un detalle.

### 3. El no-op que devuelve éxito

Una función que devuelve `Ok` sin hacer nada satisface cualquier contrato que sólo compruebe el código de retorno. Un esqueleto que "funciona" y un esqueleto que no hace nada son indistinguibles desde el llamador. **Un no-op que devuelve éxito no puede cumplir un requisito de "fail-closed" ni de "comportamiento fiable"**, y su presencia en un criterio de aceptación es la señal de que el criterio no se ha cumplido.

Pruébalo preguntando: *¿qué valor devuelve esto si todo lo demás falla?* Si la respuesta es "el mismo", no hay puerta.

### 4. La herramienta que informa sin hacer

El patrón fuera del código: un comando que imprime `status: OPEN`, devuelve exit 0, y no escribe ningún fichero. Nadie lo nota porque el contrato del comando es "imprime el estado", y lo cumple.

Cómo cazarlo: **mira el sistema de ficheros, no la salida.**

```bash
antes=$(find ~/.cache ~/.local/share /tmp -maxdepth 4 -newermt "-5 minutes" 2>/dev/null | sort -u)
comando_que_afirma_haber_escrito_algo
despues=$(find ~/.cache ~/.local/share /tmp -maxdepth 4 -newermt "-5 minutes" 2>/dev/null | sort -u)
diff <(echo "$antes") <(echo "$despues")
```

Y el segundoSymptoms: si el comando **incrementa un contador** (eventos, registros) pero **no cambia el hash encadenado** que dice verificar, entonces los eventos nuevos no están en la cadena que verifica. Eso es un falso éxito en la propia capa de autoridad.

## La gate que se vigila a sí misma

Un buen signo es un gate que te atrapa a ti. Si un validador del repo señala un defecto **en el fichero que acabas de escribir**, funciona. Si nunca te ha señalado nada, comprueba tú si tiene algún caso que debería cazarte.

Y el test que más valor da a un gate: **quitarle la cosa que vigila y comprobar que falla**. Un gate que sigue verde cuando le quitan la mitad de su poder no es un gate.

## Checklist de falsos éxitos

Antes de declarar cerrado cualquier trabajo, pasa esto:

- [ ] ¿Alguna aserción se puede saltar con una respuesta de éxito?
- [ ] ¿Hay un control que demuestra que el fixture puede llegar al final en el camino que se afirma negar?
- [ ] ¿El caso negativo tiene un caso positivo gemelo con el mismo fixture?
- [ ] ¿Algún código de error se afirma por exclusión y no por valor?
- [ ] ¿Algún `unwrap`/`expect` de un valor de configuración convierte un default en un panic en vez de una negación?
- [ ] ¿Alguna función devuelve `Ok` sin haber hecho el trabajo?
- [ ] ¿Alguna herramienta que afirma haber escrito algo no cambió nada en disco?
- [ ] ¿Algún número de un documento se afirma sin derivarlo del repositorio?
