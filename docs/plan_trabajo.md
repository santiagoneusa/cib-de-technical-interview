# Plan: Bancolombia DE02 technical test (KPIs históricos)

## Context
This is the technical test for the Data Engineer role (VP Estrategia e Innovación Corporativa). The test is `Prueba_ingeniero_datos_N2.docx` and the data is `KPIS_historico.xlsx`. The test has 4 activities: 1) exploration + quality log, 2) a rerunnable transformation into a fair analytical dataset, 3) exactly 3 findings, 4) a recurrent-process design, a tech-decisions table and an AI-usage disclosure. Deliverables: code, the analytical dataset + quality log, a README (≤2 pages) and ≤3 slides (≤2 charts). Then a 5-minute presentation and 10 minutes of Q&A.
We build it as a team. Claude implements; the user owns the judgment calls at each checkpoint. Every decision and AI correction is logged, so the AI-usage section stays honest and concrete.

**Workbook structure (header + first rows only; the data itself was not read):**
- `query`: 15,188 rows. Frente, Corte (text `202301`), Codigo_EQU, EQU, Indicador, Resultado, Meta, Cumplimiento
- `catalogo_indicadores`: 13 rows. Frente, Indicador, Definición, Unidad (Porcentaje/Escala/Cantidad)
- `catalogo_entornos`: 64 rows. Codigo_EQU, Tipo, EQU, Codigo_Padre, Nombre_Padre
- Issues already visible: frente "Talento + Agilidad" (data) vs "Modelos de trabajo y Agilidad" (catalog); the typo "Modeos…" in the catalog; "Percepción"/"Adopción" in the data are not in the catalog; Cumplimiento on a 0–10 scale(?); mixed units / "lower is better" indicators (fraud loss, AQRs); the catalog probably misses teams.

## Decisions taken (user)
- **Processing:** Python + pandas, **notebooks only**, in two folders (`1_etl`, `2_modelo`) with `X_Y_` prefixes. Spanish names and code; stage folder names in English (source/raw/processed/features/outputs) + `models/`.
- **Environment:** `pyproject.toml` managed with `uv` (uv 0.11 and Python 3.14 are installed).
- **Future state (Act 4):** Python + Excel would still be manageable (20x ≈ 300k rows). But every piece of information deserves governance even at 15k rows, so: Python orchestration → storage in **Cloudera Data Hub** (Impala/Hive tables, Parquet/Iceberg, partitioned by Corte) → reuse for ML and apps.
- **README:** Spanish, only the sections the test requires, following the user's reference structure (setup → data layout → parameters → run-order table), plus the required content sections. ≤2 pages.
- **Presentation:** HTML holding (a) ≤3 low-text slides: data/DataOps→MLOps flow, findings, human↔AI flow, and (b) an **analytics-app mockup** (management, metrics, comparisons, forecasting, alerts), not a Power BI dashboard.
- **Visual style:** Bancolombia design-system principles (foundations/tokens first, consistent token naming, atomic components with states, light/dark, AAA contrast, sober/clean, human language). Tokens: amarillo `#fdda24`, verde `#00c389`, morado `#9063cd`, naranja `#ff7f41`, rosado `#f5b6cd`, azul `#59cbe8`, negro `#2a2625`, blanco `#ffffff`. Yellow is never used as text on white. Kept as a **local file** (not published as a public Artifact, since it carries the company's branding).
- **Workflow:** a checkpoint after each activity.

## DataOps → MLOps cycle (frames the notebooks and the presentation)
`fuentes → ingesta y validación → transformación → feature pipelines → desarrollo del modelo → entrenamiento/ajuste → validación → registro y despliegue → serving y decisiones`
The **hard-rules performance scoring is treated as the "model"**: an explicit spec (develop), calibrated caps/direction/weights (tune), sensitivity + sanity checks (validate), a versioned spec JSON + metadata (register/deploy), and the app + findings (serving/decisions).

## Project layout (`Entrevista DE02/`)
```
pyproject.toml                         # uv: pandas, numpy, openpyxl, pyarrow, matplotlib, jupyter, nbconvert
README.md
data/                                  # organized by pipeline stage (maps to bronze/silver/gold in Act 4)
  source/KPIS_historico.xlsx           # original moved here; immutable input (the root copy is removed)
  raw/                                 # kpis_raw.parquet, catalogo_indicadores_raw.parquet, catalogo_entornos_raw.parquet (typed as ingested + ingest metadata)
  processed/                           # kpis_procesado.parquet, registro_calidad.csv, trazabilidad_filas.csv
  features/                            # variables_desempeno.parquet (per team × indicator × corte, scoring inputs)
  outputs/                             # dataset_analitico.csv/.parquet, puntaje_entorno.csv, app_data.json
models/
  especificacion_puntaje.json          # single scoring model: "version" prop + rules, caps, direction, aggregation
  validacion_puntaje.json              # sensitivity + sanity results
  metadata_puntaje.json                # run date, input file hash, row counts, version
notebooks/
  1_etl/
    1_1_perfilamiento_source.ipynb     # Act 1.1–1.2: row grain, keys, model proposal, catalog contrast (writes nothing)
    1_2_ingesta_raw.ipynb              # Excel → raw: explicit dtypes, schema contract, ingest metadata
    1_3_calidad_raw.ipynb              # Act 1.3: declarative rules (rule_id) → registro_calidad
    1_4_procesamiento.ipynb            # Act 2.1/2.5: treatments, homologation, final grain, row traceability
    1_5_perfilamiento_processed.ipynb  # validate processed: reconciliation, unique keys, catalog coverage
  2_modelo/
    2_1_features_desempeno.ipynb       # feature pipeline: per-indicator inputs (direction, unit, caps)
    2_2_puntaje_desempeno.ipynb        # Act 2.2/2.3: scoring spec (develop/tune) + entorno aggregation → outputs
    2_3_validacion_registro_puntaje.ipynb # sensitivity (mean vs median, caps), sanity checks → models/
    2_4_hallazgos_serving.ipynb        # Act 3: findings, ≤2 charts, app_data.json
.claude/                               # instructions written in English (better adherence); they mandate Spanish deliverables
  skills/data-standards/SKILL.md       # naming, stage contracts, rule_id + quality-log schema, idempotency, model version as a JSON prop
  skills/notebook-standards/SKILL.md   # the notebook template below
  skills/bancolombia-visual-style/SKILL.md # tokens, palette usage, accessibility, components
  skills/ai-log/SKILL.md               # how to log prompts / corrections / validations in docs/bitacora_ia.md
  agents/data-quality-reviewer.md      # reviews notebooks against data-standards
  agents/presentation-reviewer.md      # text load, 3-slide limit, contrast, timing
docs/bitacora_ia.md                    # prompt → AI proposal → validated/corrected/discarded
presentacion/index.html                # slides + app mockup (self-contained; charts as inline SVG/JS)
```

### Notebook template (from the user's reference)
1. Markdown header `# 1.2 Ingesta raw`, then numbered steps in one line, then "Artefactos persistidos", then an `| Artefacto | Ruta |` table of inputs/outputs.
2. Imports + a config cell: UPPER_CASE constants, `Path("../../data/...")` roots, explicit input/output paths, `mkdir(exist_ok=True)`.
3. `## 1. …`, `## 2. …` sections: small functions defined inline, then a short driver loop. Output is one-line `print` summaries (`tabla | filas: … | guardado: …`) or a small `display()`. Never full dumps.
4. `assert`s for contracts (row counts, unique keys, allowed values). Saves are Parquet/CSV at the end of each section.
(No `%pip` cell: dependencies come from `pyproject.toml` via `uv sync`.)

## Structure update (checkpoint 1, user decision)
Notebooks are split into `1_exploratorio/` (1_1 source, 1_2 indicadores, 1_3 equipos y entornos), `2_etl/` (2_1 ingesta raw, 2_2 calidad raw, 2_3 procesamiento, ...) and `3_modelo/`. Treatments are decided only after the exploratory review.

## Structure update 2 (2026-10-05, user decision)
- Data folders numbered: `data/0_source`, `1_raw`, `2_processed`, `3_features`, `4_outputs`; `models/` at the root. No manifest/side files.
- Notebooks: `1_eda/` (1_1_data_source_profiling, 1_2_kpi_profiling, 1_3_catalog_profiling: hypothesis-driven H01–H23),
  `2_etl/` (2_1_data_raw_ingestion, 2_2_data_raw_quality_check, 2_3_data_processing, 2_4_data_processed_profiling), `3_model/`.
- Quality rules organized as the Excel (sheet → column), `regla_id = <hoja>.<columna>.<nn>`, linked to EDA hypotheses.

## Phases & checkpoints
**Phase 0 – Setup.** `uv init`/`pyproject.toml`, `uv sync`, folders, move the Excel → `data/source/`, first draft of the skills/agents, start `bitacora_ia.md`.

**Phase 1 – Act 1 (1_1–1_3).** Profile via aggregates: grain hypothesis (Corte × Codigo_EQU × Indicador [× Frente]), duplicate keys, nulls, ranges, Meta=0, Cumplimiento vs Resultado/Meta, Corte gaps, EQU name drift, Frente/Indicador variants. Catalog contrast both ways. Star-model proposal (`hecho_kpi`, `dim_equipo`, `dim_entorno`, `dim_indicador`, `dim_frente`, `dim_tiempo`). Draft quality log.
→ **Checkpoint 1:** the user decides the treatment per issue and the assumptions.

**Phase 2 – Act 2 (1_4–2_3).** Apply treatments → processed + traceability. Metric options decided together: capped Cumplimiento with direction handling vs within-indicator×corte percentile/z-score. Entorno aggregation: team-level first, then median vs mean across teams, with n_equipos; "Sin entorno" flagged, excluded from entorno rankings and kept at team level. Sensitivity check, then register the spec in `models/` (version as a JSON prop).
→ **Checkpoint 2:** the user picks the metric/aggregation and validates the edge cases.

**Phase 3 – Act 3 (2_4).** Candidate findings → the user picks exactly 3 (≥1 entorno-level): Hallazgo → Evidencia → Interpretación → Certeza + limits + needed data. ≤2 charts. `app_data.json`.
→ **Checkpoint 3:** the user rewrites the findings in their own voice.

**Phase 4 – Act 4 + README.** Recurrent process: Excel → Python orchestration → Cloudera Data Hub zones (raw→bronze, processed→silver, features/outputs→gold, models→versioned registry); incremental load by Corte (idempotent partition overwrite); quarantine table; quality gates (same rule_ids); monitoring (rule counts per run, freshness, volume deltas, score drift); the 20x answer. Tech-decisions table. AI usage with ≥1 concrete correction.
→ **Checkpoint 4:** the user reviews the README.

**Phase 5 – HTML presentation + app mockup.** Token sheet first. Slides: (1) problem + data trust in numbers, (2) 3 findings with 1–2 charts, (3) DataOps→MLOps diagram (current → Cloudera) + the human↔AI loop. App views fed by real `outputs/` data: overview, entorno/frente comparisons, team detail with history, forecast (labeled illustrative), alerts, data-quality panel. Review with `presentation-reviewer`; 5-minute rehearsal + likely Q&A.

## Verification
- From empty `data/raw…outputs` and `models/`: `uv run jupyter nbconvert --to notebook --execute --inplace notebooks/1_etl/*.ipynb notebooks/2_modelo/*.ipynb` regenerates everything; a second run gives identical outputs.
- In-notebook asserts: layer schemas, `raw rows = processed rows + excluded rows`, unique keys at the final grain.
- Spot-check 3–5 random source rows → outputs via `trazabilidad_filas.csv`.
- HTML opened in the built-in browser: light/dark, contrast, ≤3 slides; README ≤2 pages.
