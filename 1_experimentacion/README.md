# 1. Experimentación

Exploración y calidad del archivo original (actividad 1). Cada notebook responde un numeral; los hallazgos y gráficas están dentro de él, con el código contraído para leer solo resultados.

## Ejecutar

Desde la raíz del repositorio:

```bash
uv sync
uv run jupyter lab
```

Abrir `1_experimentacion/notebooks/` y ejecutar cada notebook de arriba a abajo, en orden.

## Datos

```text
0_datos/KPIS_historico.xlsx       # entrada: hojas query, catalogo_indicadores, catalogo_entornos
1_experimentacion/notebooks/      # no escriben archivos: solo leen el Excel
```

## Orden de ejecución

| # | Notebook | Responde |
|---|---|---|
| 1.1 | `1_1_exploracion_datos.ipynb` | Qué representa cada fila, cómo separar en tablas y si la base y los catálogos coinciden (vista general) |
| 1.2 | `1_2_validacion_catalogos.ipynb` | Contraste detallado con el catálogo de indicadores y el de entornos; diferencias documentadas |
| 1.3 | `1_3_evaluacion_calidad.ipynb` | Registro de problemas de calidad: problema, evidencia, impacto y tratamiento |
