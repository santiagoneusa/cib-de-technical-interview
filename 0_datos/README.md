# 0. Datos

| Carpeta | Contenido |
|---|---|
| `entrada/` | Archivos a procesar. `KPIS_historico.xlsx` es el original entregado y **nunca se modifica** |
| `salida/` | Lo que publica el proceso de [transformación](../2_transformacion/README.md): `<archivo>_analitico.xlsx` y `ejecucion.log` |

Hojas del archivo de entrada:

| Hoja | Filas | Qué contiene |
|---|---|---|
| `query` | 15.188 | Resultado mensual de cada indicador por equipo: `Frente`, `Corte` (AAAAMM), `Codigo_EQU`, `EQU`, `Indicador`, `Resultado`, `Meta`, `Cumplimiento` |
| `catalogo_indicadores` | 13 | Qué mide cada indicador, para qué y en qué unidad |
| `catalogo_entornos` | 64 | Entorno o vicepresidencia al que pertenece cada equipo vigente hoy |

Periodo: enero 2023 a agosto 2026 (44 meses).
