# Base confiable de KPIs por equipo

Prueba técnica – Ingeniero de Datos N2, Estrategia Corporativa. El equipo de estrategia decide dónde enfocar acompañamiento con el histórico `KPIS_historico.xlsx`, pero duda de que los números reflejen la realidad. Aquí se construye una base confiable, se analiza y se propone cómo volverla un proceso recurrente.

## Estructura

```text
0_datos/              # archivo original (nunca se modifica)
1_experimentacion/    # notebooks 1 → 2: exploración y calidad (actividad 1)
2_transformacion/     # limpieza y dataset analítico (actividades 2 y 3)
3_aplicacion/         # proceso recurrente, decisiones tecnológicas y uso de IA (actividad 4)
```

Cada carpeta tiene su README con el detalle de ejecución.

## Ejecutar

Python 3.12+ y [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run jupyter lab
```

Ejecutar los notebooks de cada carpeta en orden, de arriba a abajo.

## 1. Exploración y calidad

### 1.1 ¿Qué es cada fila?

El resultado de **un indicador, para un equipo, en un mes**. La identifican `Corte` + `Codigo_EQU` + `Indicador`: el frente depende del indicador y el nombre depende del código del equipo. Según lo anterior, se infiere un posible esquema de datos:

```mermaid
erDiagram
    MEDICIONES }o--|| EQUIPOS : "Codigo_EQU"
    MEDICIONES }o--|| INDICADORES : "Indicador"
    EQUIPOS }o--|| ENTORNOS : "Codigo_Padre"
    MEDICIONES { string Corte string Codigo_EQU string Indicador float Resultado float Meta float Cumplimiento }
    EQUIPOS { string Codigo_EQU string EQU string Tipo string Codigo_Padre }
    ENTORNOS { string Codigo_Padre string Nombre_Padre string tipo }
    INDICADORES { string Indicador string Frente string Definicion string Unidad }
```

### 1.2 ¿La base y los catálogos coinciden?

| Pregunta | Respuesta |
|---|---|
| ¿Los indicadores medidos están en el catálogo? | **Solo 10 de 25 (40%)**. 1 está escrito distinto y 14 no aparecen: son el **54% de las filas** |
| ¿Todos los indicadores del catálogo se miden? | **No: 2 de 13 nunca se miden** y tienen la misma definición (un índice consolidado de agilidad) |
| ¿Los frentes tienen un solo nombre? | **No**: el frente de agilidad tiene 3 nombres en el tiempo, y el error "Modeos…" viene del propio catálogo |
| ¿Los códigos de equipo son confiables? | **146 formas de escribir 89 equipos** (minúsculas, dígitos de menos) |
| ¿Los equipos medidos existen en el catálogo? | **63 de 89 (71%)**. 26 son equipos fantasma: 18 históricos y **8 activos en 2026** que faltan en el catálogo |
| ¿Cada equipo tiene un entorno? | **Solo 56% (50 de 89)**. 11 cuelgan de una vicepresidencia y 2 están marcados "sin entorno" |

### 1.3 Problemas de calidad

| Tipo | Problema | Evidencia | Tratamiento |
|---|---|---|---|
| ![Faltantes](https://img.shields.io/badge/Faltantes-9063cd) | Filas sin código de equipo | 36 filas (0,2%) | excluir |
| ![Faltantes](https://img.shields.io/badge/Faltantes-9063cd) | Nombre de equipo vacío | 6.185 filas (40,7%) | corregir desde el catálogo |
| ![Faltantes](https://img.shields.io/badge/Faltantes-9063cd) | Cumplimiento vacío | 265 filas; 59 recalculables | corregir / excluir |
| ![Faltantes](https://img.shields.io/badge/Faltantes-9063cd) | Meses con pocos equipos | 202510: 20 equipos vs 64 normal | marcar |
| ![Duplicados](https://img.shields.io/badge/Duplicados-59cbe8) | Filas repetidas exactamente | 2.182 filas (14,4%) | excluir (se deja una) |
| ![Duplicados](https://img.shields.io/badge/Duplicados-59cbe8) | Mismo equipo, indicador y mes con valores distintos | 1.265 filas; 962 son respuestas de encuesta | corregir (promedio) |
| ![Formato](https://img.shields.io/badge/Formato-fdda24) | Código de equipo mal escrito | 325 filas (2,1%) | corregir |
| ![Formato](https://img.shields.io/badge/Formato-fdda24) | Un frente con tres nombres | 3.089 filas (20,3%) | corregir (homologar) |
| ![Catálogo](https://img.shields.io/badge/Cat%C3%A1logo-ff7f41) | Equipos fantasma | 1.473 filas (9,7%), 26 equipos | marcar "Sin entorno" |
| ![Catálogo](https://img.shields.io/badge/Cat%C3%A1logo-ff7f41) | Equipos con vicepresidencia o sin entorno | 2.218 filas (14,6%), 13 equipos | marcar "Sin entorno" (se conserva la VP) |
| ![Catálogo](https://img.shields.io/badge/Cat%C3%A1logo-ff7f41) | Indicadores sin definición | 14 de 25; 8.267 filas (54,4%) | marcar y documentar |
| ![Catálogo](https://img.shields.io/badge/Cat%C3%A1logo-ff7f41) | Indicadores del catálogo que nadie mide | 2 de 13 | aceptar y reportar |
| ![Valores](https://img.shields.io/badge/Valores-f5b6cd) | Cumplimiento en escalas distintas | 5.498 filas (36,2%): encuestas ≈ 4.4, resto ≈ 1.0 | corregir (Resultado / Meta) |
| ![Valores](https://img.shields.io/badge/Valores-f5b6cd) | Cumplimientos imposibles (155 y −1873) | 22 filas | marcar y excluir del análisis |
| ![Valores](https://img.shields.io/badge/Valores-f5b6cd) | Cumplimiento copiado (1.014683) | 530 filas (3,5%) | marcar y excluir del análisis |

Impacto y detalle: [`1_experimentacion/resultados/registro_calidad.csv`](1_experimentacion/resultados/registro_calidad.csv).
