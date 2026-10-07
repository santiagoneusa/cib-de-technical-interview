# 0. Datos

| Carpeta | Contenido |
|---|---|
| `1_crudos/` | Archivos a procesar tal como se entregan, sin ningún tratamiento. `KPIS_historico.xlsx` **nunca se modifica** |
| `2_procesados/` | `<archivo>_procesado.xlsx`: el modelo normalizado (mediciones, equipos, entornos, indicadores, frentes), registro de calidad y trazabilidad |
| `3_score/` | `<archivo>_score.xlsx`: meta cumplida y score por equipo, frente, entorno y mes |

Las carpetas 2 y 3 las genera el proceso de [transformación](../2_transformacion/README.md), que además escribe `ejecucion.log`.

Hojas del archivo original:

| Hoja | Filas | Qué contiene |
|---|---|---|
| `query` | 15.188 | Resultado mensual de cada indicador por equipo: `Frente`, `Corte` (AAAAMM), `Codigo_EQU`, `EQU`, `Indicador`, `Resultado`, `Meta`, `Cumplimiento` |
| `catalogo_indicadores` | 13 | Qué mide cada indicador, para qué y en qué unidad |
| `catalogo_entornos` | 64 | Entorno o vicepresidencia al que pertenece cada equipo vigente hoy |

Periodo: enero 2023 a agosto 2026 (44 meses).
