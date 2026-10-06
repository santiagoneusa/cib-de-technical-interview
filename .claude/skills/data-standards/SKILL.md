---
name: data-standards
description: Data quality and traceability rules for the KPIs project (quality log format, treatments, team-code normalization, catalog matching). Load before writing any quality check or transformation.
---

# Data standards

## Quality log (shown inside `1_experimentacion/notebooks/1_3_evaluacion_calidad.ipynb`; no CSV)
Columns: `categoria, problema, evidencia, impacto, tratamiento` (what activity 1.3 asks + a category).
- `categoria` ∈ Faltantes (morado), Duplicados (azul), Formato (amarillo), Catálogo (naranja), Valores (rosado); shown as a colored label.
- `evidencia` is always quantified (rows, % of the base, teams or indicators affected).
- `tratamiento` starts with one of `corregir`, `excluir`, `marcar`, `aceptar`, optionally followed by a short "how".

## Shared rules (use the same logic everywhere)
- Team code: uppercase + 5 digits (`Equ00074 → EQU00074`, `EQU0024 → EQU00024`).
- Indicator matching against the catalog: lowercase and without accents.
- Exact duplicate rows: keep one. Same month × team × indicator with different values: average.
- Teams not in `catalogo_entornos`, with a VP parent or a "sin entorno" parent → group "Sin entorno" (keep the original parent value).
- Never drop rows silently: anything excluded must be countable from the quality log.
- The source Excel in `0_datos/` is never modified.
