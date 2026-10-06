# 1. Experimentación

Exploración y calidad del archivo original (actividad 1). Los hallazgos y gráficas están dentro de cada notebook.

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
1_experimentacion/
├── notebooks/
└── resultados/                   # salidas de los notebooks
```

## Orden de ejecución

| # | Notebook | Qué hace | Escribe |
|---|---|---|---|
| 1 | `1_eda.ipynb` | Responde 1.1 y 1.2: qué es cada fila, cómo separar en tablas y cómo se relacionan la base y los catálogos | — |
| 2 | `2_calidad_datos.ipynb` | Responde 1.3: revisa faltantes, duplicados, formato, catálogo y valores, y arma el registro de calidad | `resultados/registro_calidad.csv` |
