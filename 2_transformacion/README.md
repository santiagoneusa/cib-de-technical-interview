# 2. Transformación

Proceso que lleva el archivo original al modelo de datos propuesto en la [actividad 1](../1_experimentacion/README.md#11-estructura-de-datos-propuesta) y calcula un score comparable entre equipos, frentes y entornos (actividad 2). Son scripts de Python con un solo punto de entrada, para que el equipo de estrategia los ejecute cada mes sin abrir un notebook.

## Ejecución

Desde la raíz del repositorio:

```bash
uv run python 2_transformacion/src/main.py
```

Por cada `.xlsx` de `0_datos/1_crudos/` publica dos archivos y deja una línea en `0_datos/ejecucion.log`:

| Archivo | Hojas |
|---|---|
| `0_datos/2_procesados/<archivo>_procesado.xlsx` | El modelo normalizado: `frentes`, `indicadores`, `entornos`, `equipos`, `mediciones` |
| `0_datos/2_procesados/<archivo>_calidad.xlsx` | `registro_calidad`, `trazabilidad`, `validaciones` |
| `0_datos/3_score/<archivo>_score.xlsx` | `mediciones` (con meta cumplida), `indicadores`, `equipos_mes`, `frentes_mes`, `entornos_mes`, `evolucion_mes` |

Si al archivo le falta una hoja o columna, o una validación falla, **no publica nada** y termina con código 1, que cualquier orquestador (cron, Power Automate, Cloudera) detecta como error.

```text
src/
  main.py            # crudos → etl → procesados → score
  etl/
    reglas.py        # reglas de negocio editables: formatos, frentes mal escritos, sentido de cada indicador
    limpieza.py      # una función por regla; cada una devuelve los datos tratados y su traza
    modelo.py        # separa los datos en mediciones, equipos, entornos, indicadores y frentes
    calidad.py       # validaciones y registro de calidad
  score/
    features.py      # meta cumplida, resumen por indicador y score por equipo-mes
    agregacion.py    # score por frente, entorno y mes
```

## Datos procesados (2.1)

**Granularidad:** una medición por **mes × equipo × indicador**. Cada medición guarda solo códigos (`cod_equipo`, `cod_indicador`, `cod_frente`) más `resultado`, `meta` y dos columnas de cumplimiento:
- `cumplimiento_original`: tal como llega en el archivo.
- `cumplimiento_procesado`: igual al original, salvo cuando el original es el mismo Resultado y la meta es positiva; ahí se calcula Resultado / Meta. Eso corrige la escala de las encuestas (Percepción 9,43 sobre una meta de 10 → 0,94). Con meta 0 o negativa no hay contra qué calcular y se conserva el original.

De 15.188 filas quedan 11.466 mediciones. Las reglas se aplican en este orden:

| Regla | Qué hace |
|---|---|
| Código de equipo | Lo pasa a mayúsculas y 5 dígitos. Si está vacío, lo toma del nombre del equipo, porque cada nombre corresponde a un solo código |
| Frente | Corrige "Modeos…" a "Modelos de trabajo y Agilidad". "Talento + Agilidad" se conserva como un frente propio |
| Resultado, Meta o Cumplimiento vacíos | Se excluye la fila; no se recalcula ningún valor faltante |
| Filas repetidas | Se excluyen; se deja una |
| Valores en conflicto | Varias filas del mismo mes, equipo e indicador con valores distintos (sobre todo respuestas de encuesta) se promedian en una |
| Cumplimiento procesado | Resultado / Meta cuando el Cumplimiento original es el mismo Resultado y la meta es positiva |

**Catálogos completos:** `indicadores` tiene los 13 del catálogo (aunque no se midan) más los que se miden sin estar catalogados, con definición y unidad `Pendiente`. `equipos` incluye los que no están en `catalogo_entornos`, con entorno `Sin entorno`. `frentes` incluye "Talento + Agilidad".

**Trazabilidad (2.5):** el archivo `_calidad.xlsx` deja cada fila tocada en `trazabilidad` con su número de fila en el Excel original (`fila_excel`), la regla, la acción (`excluida`, `corregida`, `completada` o `agrupada`) y qué cambió, por ejemplo `Codigo_EQU: Equ00074 → EQU00074`. `registro_calidad` resume cuántas filas tocó cada regla.

**Reejecución (2.6):** cada ejecución parte del archivo original, que nunca se modifica, y da el mismo resultado. Las validaciones comprueban que no haya llaves repetidas ni vacíos, que cada código exista en su tabla y que filas originales = mediciones + excluidas + agrupadas.

## Score

**2.2 Métrica: meta cumplida.** Por cada medición vale 1 si el resultado alcanza la meta según el sentido del indicador (≥ si más es mejor, ≤ si menos es mejor), y 0 si no. El score de un equipo en un mes es la proporción de sus indicadores que cumplieron, todos con el mismo peso.
- **Por qué es comparable:** no depende de la unidad, de la escala ni de cómo se calculó la columna Cumplimiento, y ningún valor extremo domina.
- **Sentido no verificado:** en tres indicadores (Brecha Ingresos Gastos, Impactos a clientes, Índice AQR's) ningún sentido explica el dato de origen. Para ellos se usa `cumplimiento_procesado ≥ 1`, y se debe confirmar con su dueño.
- **Cobertura:** cuántos equipos miden un indicador es contexto, no un peso. Un indicador medido en pocos equipos puede ser un riesgo clave.

**2.3 Agregación por entorno: mediana de los equipos.** Cada equipo cuenta una vez, sin importar cuántos indicadores reporte, y un equipo extremo no mueve el resultado; muchos entornos tienen 1 a 4 equipos. Junto a la mediana siempre van `n_equipos` y el rango.
- **Vicepresidencias:** los equipos que cuelgan de una vicepresidencia se agrupan con ella.
- **Equipos sin entorno:** aparecen a nivel de equipo y frente. A nivel de entorno solo se cuentan, sin calificarlos como grupo, porque juntarlos mezclaría áreas sin relación entre sí.

*(La prueba no tiene numeral 2.4.)*

## Limitaciones

- **Se pierde magnitud:** quedar al 99% o al 50% de la meta cuenta igual.
- **Encuestas:** su meta es el puntaje máximo, así que casi nunca se cumple (Talento + Agilidad: 0%). Bajan por igual a todos los equipos medidos en esos meses.
- **Indicadores que cambian por año:** la mezcla de indicadores cambia cada año, así que el score compara bien entre equipos de un mismo mes. A lo largo del tiempo compara "qué tanto se cumplió lo que se medía", no los mismos indicadores.
- **Códigos estables:** los códigos `IND` y `FRE` se asignan en el orden del catálogo y de aparición. Si el catálogo cambia, conviene fijarlos en el propio catálogo.
