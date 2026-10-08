# Entrevista Técnica DE Game

Prueba técnica – Ingeniero de Datos N2, Estrategia Corporativa. Se presenta la construcción de una base confiable, junto con su análisis y propuesta de automatización.

**Contenido:** [1. Ejecución](#1-ejecución) · [2. Exploración](#2-exploración-y-calidad-actividad-1) · [3. Transformación](#3-transformación-actividad-2) · [4. Hallazgos](#4-hallazgos-actividad-3) · [5. Solución técnica](#5-solución-técnica-y-decisiones-tecnológicas-actividad-4) · [6. Uso de IA](#6-uso-de-inteligencia-artificial)

## 1. Ejecución

Requisitos: Python 3.12+ y [uv](https://docs.astral.sh/uv/). Desde la raíz, `uv sync` y luego:

```bash
uv run python 2_transformacion/src/main.py    # 0_datos/1_crudos → 2_procesados (dataset y calidad) → 3_score
uv run python 3_reporte/generar_reporte.py    # 3_reporte/reporte.html y presentacion.html
uv run jupyter lab                            # notebooks 1.1, 1.2 y 1.3 de 1_experimentacion
```

## 2. Exploración y calidad (actividad 1)

**1.1** Cada fila es **el resultado de un indicador, para un equipo, en un mes** (`Corte` + `Codigo_EQU` + `Indicador`). Como los nombres y frentes se repiten y hacen de llave, se separa en mediciones y catálogos con códigos estables:

```text
MEDICIONES (corte, cod_equipo, cod_indicador, resultado, meta, cumplimiento_original, cumplimiento_procesado)
EQUIPOS (cod_equipo, nombre, cod_entorno) → ENTORNOS (cod_entorno, nombre)
INDICADORES (cod_indicador, nombre, cod_frente, unidad, sentido) → FRENTES (cod_frente, nombre)
```

**1.2** La base y los catálogos no coinciden:
- 15 de los 25 indicadores (57% de las filas) no están en el catálogo.
- 26 de los 89 equipos no están en `catalogo_entornos`.
- "Talento + Agilidad" no existe como frente.

**1.3** El [registro de calidad](1_experimentacion/notebooks/1_3_evaluacion_calidad.ipynb) tiene 16 problemas con evidencia, impacto y tratamiento:
- **Faltantes:** nombre de equipo vacío en el 41% de las filas → completar.
- **Duplicados:** 14% de filas repetidas → excluir.
- **Formato:** 146 escrituras para 89 códigos de equipo → corregir.
- **Catálogo:** 54% de las filas con indicadores sin definición → reportar.
- **Valores:** encuestas en escala de puntaje → corregir.

## 3. Transformación (actividad 2)

- **2.1** Una función por regla: normaliza códigos, excluye filas sin Resultado, Meta o Cumplimiento (sin imputar), quita repetidas y promedia conflictos. Quedan **11.466 mediciones** (mes × equipo × indicador) en `_procesado.xlsx`.
- **2.2** La métrica es la **meta cumplida**: 1 si el resultado alcanza la meta según el sentido del indicador y 0 si no. No depende de escalas y todos los indicadores pesan igual.
- **2.3** Por entorno, la **mediana de sus equipos**. Las vicepresidencias se agrupan como un entorno más, y los "Sin entorno" se cuentan sin calificarse.
- **2.5 y 2.6** `_calidad.xlsx` traza cada fila tocada. Si una validación falla, no se publica nada, y cada ejecución da el mismo resultado.
- **Supuestos:**
  - El entorno de hoy (`catalogo_entornos`) vale para todo el histórico.
  - Un mismo nombre de indicador en dos frentes son dos indicadores.
  - En 3 indicadores no se pudo verificar si más es mejor, y se usa su Cumplimiento ≥ 1.

## 4. Hallazgos (actividad 3)

Detalle en [`reporte.html`](3_reporte/reporte.html). *Comparación justa: cada resultado frente al de los equipos que miden el mismo indicador ese mes.*
1. **Que una meta se cumpla depende más del indicador que del equipo.**
   - **Evidencia:** de todo lo que varía entre metas cumplidas y no cumplidas, el 48% se explica por qué indicador es y en qué mes; solo el 5% por qué equipo lo reporta.
   - **Interpretación:** calibrar metas antes de comparar.
   - **Certeza:** alta.
2. **La comparación justa cambia a quién acompañar.**
   - **Evidencia:** Entorno 8 cumple el 33% de sus metas (puesto 20), pero al compararlo con equipos que miden lo mismo pasa al puesto 5.
   - **Interpretación:** acompañar según la comparación justa.
   - **Certeza:** media, porque hay entornos de 1 a 4 equipos.
3. **En 2026 no bajó el desempeño: subió la vara.**
   - **Evidencia:** en Disponibilidad el resultado sigue cerca de 99,7%, pero la meta subió de 99,2% a 99,6%; con el mismo resultado, los equipos que cumplen pasan de 98% a 57%.
   - **Interpretación:** registrar los cambios de meta.
   - **Certeza:** alta.

**No se puede concluir** si las metas están bien calibradas ni si acompañar mejora el cumplimiento. **Faltan** el histórico de metas, el entorno de cada equipo por mes y los acompañamientos realizados.

## 5. Solución técnica y decisiones tecnológicas (actividad 4)

Es un proceso **semiautomatizado** en el stack del banco (Cloudera):
1. **Recolección:** durante el mes el negocio registra los datos en una plantilla de Excel con listas tomadas de los catálogos.
2. **Carga incremental:** al cierre, solo el corte del mes se sube a Cloudera Data Hub.
3. **ETL y score:** un job de Cloudera AI ejecuta las reglas de `etl/` y `score/` sobre ese corte.
4. **Tablero:** Streamlit o Power BI, alimentado directamente por las tablas en la nube.
- **Errores, calidad y monitoreo:** si una validación falla, no se publica, se conserva la última versión buena, las filas rechazadas van a cuarentena y se avisa. Hay umbrales por corte y una tabla de ejecuciones.

**Con 20 veces más volumen** (unas 300.000 filas), Excel sigue sirviendo para recolectar cada mes, pero almacenar y consultar periodos largos pasa a SQL, y la transformación a jobs de SQL.

| Decisión | Herramienta | Para qué | Razón | Alternativa | Con mucho más volumen |
|---|---|---|---|---|---|
| Extracción/consulta | Excel + Python | Explorar los datos y hacer el diagnóstico | Flexible y ampliamente conocido | SQL | Excel para recolectar; SQL para almacenar y consultar |
| Transformación | Scripts de Python (hoy locales) | Ejecutar el ETL de limpieza y el score | Stack conocido: al pasarlo a negocio no genera tanta deuda técnica | SQL | Jobs de SQL |
| Análisis | Python con pandas | Encontrar hallazgos y calcular cifras | Mismo stack, reproducible | Excel o SQL | SQL en Hue |
| Visualización | HTML | Mostrar los análisis y conclusiones | Se necesita un reporte estático, no interactivo | Streamlit o Power BI | HTML para lo estático; Power BI para lo dinámico |

## 6. Uso de inteligencia artificial

Usé **Claude Code** (Claude Opus) como ayudante en las tareas de **diseño e implementación**. El desarrollo con agentes es más rápido y completo cuando una persona lo orquesta: le doy contexto desde que se toman las decisiones, la IA implementa rápido y yo itero sobre el resultado. De ese trabajo salieron las **skills y reglas de implementación** de `.github/`, para que las próximas iteraciones (con Claude o con GitHub Copilot) sigan el mismo estándar.
- **Prompt clave:** tenía ideas para presentar los hallazgos, pero la forma resultaba compleja. Pedí a la IA plantear una estructura para presentarlos y cuestionar si lo que quería mostrar aportaba valor; tras varias iteraciones quedó el formato de hallazgo, evidencia, interpretación y certeza del reporte.
- **Otros prompts:** "Construyamos la prueba como equipo, sin leer el Excel completo" y "Prueba el cumplimiento recalculado antes de aplicarlo".
- **Corregido:** la IA homologó "Talento + Agilidad" a otro frente. Se corrigió porque sus indicadores no coinciden con el catálogo.
- **Validado:** recalcular todo el Cumplimiento como Resultado / Meta inventaba valores (Regulatorio topa en 1), así que se limitó a encuestas y valores copiados.
