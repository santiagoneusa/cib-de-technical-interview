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
| `1_experimentacion/` | `notebooks/1_eda.ipynb`, `notebooks/2_calidad_datos.ipynb`, `resultados/` | 1 |
| `2_transformacion/` | cleaning + analytical dataset | 2 and 3 |
| `3_aplicacion/` | recurrent process, tech decisions, `bitacora_ia.md` | 4 |

Notebook names: `<n>_<spanish_name>.ipynb`, run in numeric order. Everything (code, comments, markdown) in Spanish.

## Cell layout
1. Markdown header: `# <n>. Título`, one line saying which test questions it answers, and an `| Artefacto | Ruta |` table.
2. Config cell: imports, paths as constants, load the sheets.
3. Sections `## <n>. <pregunta de negocio>`: one short code cell, then a markdown "Respuesta/Lectura" in plain language with the numbers.
4. End with a summary that matches the folder README.

## Rules
- Read the Excel directly; do not write intermediate files unless a later step reads them.
- Print short summaries or small tables (≤ 25 rows); never full sheets.
- At most one chart per section, using the palette in `bancolombia-visual-style`.
- The notebook must run top to bottom on a fresh kernel (`uv run jupyter nbconvert --execute`).
