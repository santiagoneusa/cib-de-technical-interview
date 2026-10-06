---
name: notebook-standards
description: Template and conventions for the pipeline Jupyter notebooks (naming, header, config cell, sections, outputs). Load before creating or editing any notebook under notebooks/.
---

# Notebook standards

## Location and naming
- `notebooks/1_eda/` (diagnosis: reads `data/0_source`, writes nothing to the pipeline; review artifacts go to `docs/`),
  `notebooks/2_etl/` (ingestion, quality check, processing) and `notebooks/3_model/` (features, scoring, validation, findings).
- File name: `<folder>_<step>_<english_snake_name>.ipynb` using standard data-engineering terms:
  `1_1_data_source_profiling`, `1_2_kpi_profiling`, `1_3_catalog_profiling`, `2_1_data_raw_ingestion`, `2_2_data_raw_quality_check`,
  `2_3_data_processing`, `2_4_data_processed_profiling`. Run order = lexical order. Content and code stay in Spanish.
- EDA notebooks are hypothesis-driven: each section is titled `## Hxx. <hipótesis>`, tests it with code and calls
  `registrar_hipotesis(codigo, enunciado, resultado, evidencia)` with resultado ∈ {se cumple, no se cumple, parcial}; the notebook ends with a hypothesis summary table. Hypothesis codes are global and consecutive across EDA notebooks.
- Notebooks are the code. There is no `src/` package; helper functions live inside the notebook that uses them.

## Cell structure
1. **Header (markdown)**
   ```
   # 2.1 Data raw ingestion

   (1) paso uno, (2) paso dos, (3) paso tres.

   Artefactos persistidos: ...

   | Artefacto | Ruta |
   |---|---|
   | Entrada ... | `data/0_source/...` |
   | Salida ... | `data/1_raw/...` |
   ```
2. **Config cell (code)**: imports, then UPPER_CASE constants, `Path("../../data/...")` roots, every input/output path declared explicitly, `mkdir(parents=True, exist_ok=True)` for outputs.
3. **Numbered sections**: markdown `## 1. <título>` followed by one code cell: small functions first, then a short driver block.
4. **Final section**: contract `assert`s and saves.

## Output hygiene
- Print one-line summaries: `print("kpis | filas:", n, "| guardado:", ruta)`.
- `display()` only small tables (≤ 20 rows) or aggregates. Never print full sheets.
- No hidden state: the notebook must run top to bottom on a fresh kernel.
- Comments in Spanish, sparse, explaining *why* not *what*.
- No `%pip` cells: dependencies live in `pyproject.toml` (`uv sync`).
