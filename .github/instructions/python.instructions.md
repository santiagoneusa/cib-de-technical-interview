---
applyTo: "**/*.py"
description: Código limpio para el proceso recurrente en Python
---

# Código Python

- **Una responsabilidad por función.** El nombre dice qué hace: `normalizar_codigo_equipo`, `imputar_frente`, `excluir_meta_vacia`. Prefijos: `normalizar_`, `corregir_`, `imputar_`, `excluir_`, `agrupar_`, `calcular_`, `construir_`.
- **Funciones de módulo antes que clases.** Es el idioma de pandas y cada función se explica sola.
- **Sin docstrings de módulo y con pocos comentarios.** El código debe leerse solo; un comentario solo explica un *porqué* que el código no puede decir.
- **Que el código respire:** una línea en blanco entre preparar, calcular y devolver, y antes del `return` cuando la función tiene varios bloques.
- **Nombres homogéneos** en `snake_case` y en español: `cod_equipo`, `cod_indicador`, `cumplimiento_original` / `cumplimiento_procesado`. Si dos columnas significan cosas distintas, el nombre lo dice.
- **Reglas de negocio como datos** en `etl/reglas.py` (patrones, homologaciones, sentido de cada indicador, descripción y tratamiento de cada regla). La lógica no lleva valores mágicos.
- **Cada regla de limpieza** es una función `(datos) -> (datos, traza)` y se registra en orden en `limpiar()`. Las auxiliares privadas empiezan con `_`.
- **Sin artefactos opacos:** nada de `.pkl` para reglas deterministas; las reglas viven en código versionado.
- **Fallar en voz alta:** si el esquema o una validación falla, no se publica nada, se escribe en el log y el proceso termina con código 1.
- **Reproducible:** el mismo archivo crudo produce exactamente las mismas salidas.
