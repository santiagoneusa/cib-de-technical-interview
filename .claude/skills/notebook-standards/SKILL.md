---
name: notebook-standards
description: Conventions for the project notebooks and folders (structure, naming, cell layout, audience). Load before creating or editing any notebook or README in this repo.
---

# Notebook and folder standards

## Audience first
The readers are **business analysts of the strategy team**, not engineers. Prefer the simplest code that answers the question; avoid abstractions, helper layers and extra files that create technical debt. "No se premia usar más herramientas, sino elegir bien."

## Structure (one folder per stage, each with its own README)
| Folder | Content | Test activity |
|---|---|---|
| `0_datos/` | `KPIS_historico.xlsx` as delivered (never modified) | – |
| `1_experimentacion/` | `notebooks/1_1_exploracion_datos.ipynb`, `1_2_validacion_catalogos.ipynb`, `1_3_evaluacion_calidad.ipynb` (no output files) | 1 |
| `2_transformacion/` | cleaning + analytical dataset | 2 and 3 |
| `3_aplicacion/` | recurrent process, tech decisions, `bitacora_ia.md` | 4 |

One notebook per test numeral: `<actividad>_<numeral>_<spanish_name>.ipynb` (e.g. `1_2_validacion_catalogos`), run in numeric order. Sections inside use the numeral plus a letter: `## 1.2.a …`. Everything (code, comments, markdown) in Spanish.

## Cell layout
1. Markdown header: `# <numeral> Título`, the test activity text as bullets (**Actividad x.y**), a **Contenido** list of the lettered sections (table of contents), and an `| Artefacto | Ruta |` table.
2. Config cell: imports, paths as constants, load the sheets.
- **All code cells are collapsed** (`metadata.jupyter.source_hidden = true`, tag `hide-input`): readers see outputs and conclusions; code is one click away.
3. Sections `## <n>. <pregunta de negocio>`: one short code cell, then a markdown "Respuesta/Lectura" in plain language with the numbers.
4. End with a summary that matches the folder README.

## Rules
- Read the Excel directly; do not write intermediate files unless a later step reads them.
- Print short summaries or small tables (≤ 25 rows); never full sheets.
- At most one chart per section, using the palette in `bancolombia-visual-style`.
- The notebook must run top to bottom on a fresh kernel (`uv run jupyter nbconvert --execute`).
