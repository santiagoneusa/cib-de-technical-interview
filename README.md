# Base confiable de KPIs por equipo

Prueba técnica – Ingeniero de Datos N2, área de Estrategia Corporativa.

El equipo de estrategia usa el histórico de KPIs (`KPIS_historico.xlsx`) para decidir dónde enfocar acompañamiento, pero hay dudas sobre si los números reflejan la realidad. Este repositorio construye una base confiable, la analiza y propone cómo volverla un proceso recurrente, con la solución más simple que resuelve el problema.

## Estructura

| Carpeta | Para qué | Actividad |
|---|---|---|
| [`0_datos/`](0_datos/) | Archivo original, sin modificar | – |
| [`1_experimentacion/`](1_experimentacion/) | Exploración y calidad de datos: qué hay en el archivo y qué tan confiable es | 1 |
| [`2_transformacion/`](2_transformacion/) | Limpieza y dataset analítico comparable | 2 y 3 |
| [`3_aplicacion/`](3_aplicacion/) | Proceso recurrente, decisiones tecnológicas y uso de IA | 4 |

Cada carpeta tiene su propio README con los resultados.

## Cómo ejecutar

Requiere Python 3.12+ y [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run jupyter lab
```

Abrir los notebooks de cada carpeta y ejecutarlos de arriba a abajo, en el orden de su número.

## Avance

- [x] Actividad 1 – Exploración y calidad → [`1_experimentacion/README.md`](1_experimentacion/README.md)
- [ ] Actividad 2 – Transformación
- [ ] Actividad 3 – Primeros hallazgos
- [ ] Actividad 4 – Solución técnica y decisiones tecnológicas
