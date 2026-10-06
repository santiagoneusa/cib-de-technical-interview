---
name: data-standards
description: Data engineering standards for the KPIs pipeline (stage folders, naming, contracts, quality rules, traceability, scoring model registry). Load before creating or editing any notebook that reads or writes under data/ or models/.
---

# Data standards – KPIs pipeline

All deliverables (code identifiers, comments, markdown, file names) are written in **Spanish**. Stage folder names stay in English because they are industry vocabulary.

## Stage folders (numbered; one direction only: 0_source → 1_raw → 2_processed → 3_features → 4_outputs)
| Folder | Content | Rule |
|---|---|---|
| `data/0_source/` | `KPIS_historico.xlsx` as delivered | Immutable. Never write here. |
| `data/1_raw/` | One Parquet per sheet (no manifests or side files), explicit dtypes, values untouched + ingest metadata (`_archivo_origen`, `_hoja`, `_fila_origen`, `_hash_archivo`; no run timestamps, for idempotency) | Only type casting and metadata. No cleaning. |
| `data/2_processed/` | Clean, homologated fact + dims, `registro_calidad.csv`, `trazabilidad_filas.csv` | Every change is traceable to a `regla_id`. |
| `data/3_features/` | Scoring inputs per team × indicator × corte | Derived only from processed. |
| `data/4_outputs/` | Analytical dataset, entorno scores, `app_data.json` | Consumption layer. |
| `models/` | `especificacion_puntaje.json`, `validacion_puntaje.json`, `metadata_puntaje.json` | Single scoring model. Version is a JSON property (`"version"`), never a folder. |

Future-state mapping (Cloudera Data Hub): 1_raw → bronze, 2_processed → silver, 3_features/4_outputs → gold, models → versioned registry.

## Naming
- Spanish `snake_case` for columns, variables, files: `codigo_equipo`, `corte`, `cumplimiento_ajustado`.
- Constants in `UPPER_CASE` in the config cell.
- Keys: `codigo_equipo` (team), `codigo_entorno`, `indicador_id`, `frente_id`, `corte` (period `YYYYMM`, stored as `int` plus `fecha_corte` as first day of month).

## Contracts
- Every notebook asserts its input schema (expected columns + dtypes) before working, and its output grain (unique key) before saving.
- Reconciliation is mandatory: `filas_raw == filas_processed + filas_excluidas`.
- Outputs are idempotent: same source file ⇒ byte-equivalent outputs (sort before saving, no timestamps inside data files except `metadata_puntaje.json`).

## Quality rules
- Rules are organized like the Excel: **sheet → column**, in the Excel column order. Row-level rules use the pseudo-column `fila`.
- `regla_id` = `<hoja>.<columna>.<nn>`, e.g. `query.Codigo_EQU.02`, `catalogo_entornos.Codigo_Padre.01`.
- Each rule is phrased as the expectation it validates (`validacion`, e.g. "Codigo_EQU no es nulo") and links the EDA hypothesis that originated it (`hipotesis_eda`, e.g. `H04`).
- `registro_calidad.csv` columns: `regla_id, hoja, columna, validacion, evidencia, filas_afectadas, pct_afectado, impacto, tratamiento, justificacion, hipotesis_eda, estado`.
- `tratamiento` ∈ {`corregir`, `excluir`, `marcar`, `aceptar`}; `estado` ∈ {`aprobado` (decided at a checkpoint), `propuesto`}.
- `trazabilidad_filas.csv` columns: `fila_origen, regla_id, tratamiento, columna, valor_antes, valor_despues`.
- Never drop rows silently: excluded rows are listed in the trace with their `regla_id`.
- Keep outputs minimal: do not persist files that no downstream step reads.

## Scoring model
- The performance score is a rules-based model. Treat it with MLOps discipline: explicit spec → tuning decisions documented → validation (sensitivity, sanity, reconciliation) → registry in `models/` → serving via `data/4_outputs/`.
- `especificacion_puntaje.json` must contain: `version`, `fecha`, `metrica`, `tope`, `sentido_por_indicador`, `agregacion`, `tratamiento_sin_entorno`, `supuestos`.
