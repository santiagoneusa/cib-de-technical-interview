# Instrucciones del repositorio

Prueba técnica de Ingeniero de Datos N2 (Bancolombia, Estrategia Corporativa) sobre `KPIS_historico.xlsx`: exploración y calidad, transformación a un modelo normalizado, score comparable entre equipos, frentes y entornos, y un proceso recurrente.

## Contexto
- La audiencia son **analistas de negocio** del equipo de estrategia, que administrarán la solución. Lo simple gana: "no se premia usar más herramientas, sino elegir bien".
- Todo (código, nombres, comentarios, documentos) va en **español**.
- Las decisiones de criterio son humanas. La IA propone, implementa y valida contra los datos, y cada decisión queda en `4_aplicacion/bitacora_ia.md` (skill `bitacora-ia`).

## Estructura
| Carpeta | Contenido |
|---|---|
| `0_datos/1_crudos/` | Archivo original. **Nunca se modifica** |
| `0_datos/2_procesados/` | `_procesado.xlsx` (modelo normalizado) y `_calidad.xlsx` (registro, trazabilidad, validaciones) |
| `0_datos/3_score/` | `_score.xlsx` |
| `1_experimentacion/notebooks/` | Un notebook por numeral de la actividad 1 |
| `2_transformacion/src/` | `main.py`, `etl/` (reglas, limpieza, modelo, calidad) y `score/` (features, agregación) |
| `3_reporte/` | `generar_reporte.py` + `plantilla.html` → `reporte.html` (hallazgos interactivos) |
| `4_aplicacion/` | Bitácora de IA |

Hay un solo `README.md`, en la raíz. No se crean READMEs por carpeta.

## Comandos
- Dependencias: `uv sync`
- Proceso completo: `uv run python 2_transformacion/src/main.py`
- Notebooks: `uv run jupyter nbconvert --to notebook --execute --inplace <notebook>`

## Reglas de oro
1. **El dato manda.** Nunca se asume una equivalencia que el dato no demuestra. Por ejemplo, "Talento + Agilidad" no es un nombre anterior de "Modelos de trabajo y Agilidad".
2. **Probar antes de aplicar.** Toda regla nueva se prueba primero contra los datos, indicador por indicador (skill `probar-hipotesis`).
3. **No inventar valores.** Si falta Resultado, Meta o Cumplimiento, la fila se excluye; no se imputa.
4. **Trazabilidad literal.** Cada fila tocada deja en la traza qué cambió (`antes → después`), y eso tiene que ser verdad en el archivo original.
5. **Cifras desde las salidas.** Los números de los documentos se leen de los notebooks ejecutados o de los Excel publicados, nunca se escriben de memoria.
6. **No leer el Excel completo** en la conversación; usar agregados y muestras pequeñas.
7. **Menos es más.** Cada columna, hoja o archivo debe justificar su existencia ante un analista.
