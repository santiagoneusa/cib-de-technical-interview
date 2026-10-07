---
applyTo: "**/*.ipynb"
description: Estándar de los notebooks de exploración
---

# Notebooks

- **Uno por numeral** de la prueba: `<actividad>_<numeral>_<nombre>.ipynb` (por ejemplo `1_2_validacion_catalogos`), ejecutados en orden.
- **Encabezado:** `# <numeral> Título`, el texto de la actividad en viñetas, una lista **Contenido** con las secciones `x.y.a`, `x.y.b`… y una tabla `| Artefacto | Ruta |`.
- **Código contraído** (`metadata.jupyter.source_hidden = true` y etiqueta `hide-input`): el lector ve resultados y lecturas.
- **Por sección:** una celda de código corta, como máximo una gráfica con la paleta (skill `estilo-visual-bancolombia`) y una **Lectura** en lenguaje simple con las cifras.
- **Títulos afirmativos**, no preguntas.
- **El mismo estilo que el código Python:** sin comentarios ni docstrings y con una línea en blanco al abrir una figura, al salir de un bucle y antes de `plt.tight_layout()`.
- **Solo leen** `0_datos/1_crudos/`; no escriben archivos. Muestran tablas de 25 filas como máximo, nunca hojas completas.
- **Se editan en su lugar.** El humano también los edita: se revisa el diff antes de tocarlos y nunca se regeneran desde un script.
- **Deben correr** de principio a fin en un kernel limpio.
