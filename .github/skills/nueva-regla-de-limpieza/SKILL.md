---
name: nueva-regla-de-limpieza
description: Agregar, cambiar o quitar una regla de limpieza en el proceso recurrente (2_transformacion/src/etl) sin romper la trazabilidad ni las validaciones.
---

# Nueva regla de limpieza

1. **Probar primero** con la skill `probar-hipotesis`: cuántas filas toca la regla, en qué indicadores y con qué ejemplos. Si la regla inventaría valores o asume una equivalencia que el dato no demuestra, no se implementa; se reporta.
2. **Declararla en `etl/reglas.py`:**
   - en `REGLAS`, `"<id>": ("<problema en lenguaje de analista>", "<tratamiento>")`;
   - las constantes que necesite (patrones, listas, homologaciones).
3. **Escribir la función en `etl/limpieza.py`:**
   ```python
   def excluir_meta_vacia(datos):
       return _excluir(datos, datos["meta"].isna(), "meta_vacia", "Meta: vacío")
   ```
   - Firma `(datos) -> (datos, traza)`. Usar `_excluir` o `_traza` con un `detalle` literal (`Columna: antes → después`).
   - Una sola responsabilidad. Sin docstring; con líneas en blanco entre preparar, trazar y devolver.
   - No agregar condiciones que oculten casos válidos (por ejemplo "solo si el valor cambia").
4. **Registrarla en el orden correcto de `limpiar()`.** Las exclusiones van antes de agrupar y los cálculos después.
5. **Ejecutar** `uv run python 2_transformacion/src/main.py` y revisar:
   - **Validaciones:** todas en `ok`.
   - **Registro de calidad:** las filas de la regla en `registro_calidad` coinciden con la prueba.
   - **Idempotencia:** dos ejecuciones dan el mismo resultado.
6. **Actualizar** la sección de transformación del `README.md` y el registro de 1.3 si cambia un tratamiento. Agregar una entrada a la bitácora (skill `bitacora-ia`).
