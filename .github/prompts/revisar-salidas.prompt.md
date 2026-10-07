---
description: Revisar que los Excel publicados sean coherentes y entendibles para un analista
agent: agent
---

Ejecuta `uv run python 2_transformacion/src/main.py` y revisa las tres salidas en `0_datos/2_procesados/` y `0_datos/3_score/`:

1. **Validaciones:** todas en `ok`, y filas originales = mediciones + excluidas + agrupadas.
2. **Utilidad:** cada hoja y columna se entiende sin explicación y sirve para el análisis. Señala lo que sobra o lo que no es dicente.
3. **Trazabilidad:** toma 5 filas al azar de `trazabilidad` y compruébalas contra el archivo crudo. El `detalle` debe ser literalmente cierto.
4. **README:** sus cifras coinciden con las salidas.

Responde con una lista corta: hoja, problema y propuesta. No edites archivos.
