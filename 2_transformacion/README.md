# 2. Transformación

Proceso que convierte el archivo original en un dataset analítico para comparar equipos, frentes y entornos en el tiempo (actividad 2). Son scripts de Python con un solo punto de entrada, pensados para que el equipo de estrategia los ejecute cada mes sin abrir un notebook.

## Ejecución

Desde la raíz del repositorio:

```bash
uv run python 2_transformacion/src/main.py
```

Procesa cada `.xlsx` de `0_datos/entrada/` y publica `0_datos/salida/<archivo>_analitico.xlsx`. Cada ejecución deja una línea en `0_datos/salida/ejecucion.log`. Si el archivo no trae las hojas o columnas esperadas, o alguna validación falla, **no publica nada** y termina con código 1, que cualquier orquestador (cron, Power Automate, Cloudera) detecta como error.

```text
src/
  main.py            # entrada → etl → score → Excel de salida
  etl/               # DataOps: limpieza y calidad
    reglas.py        # reglas de negocio editables (homologaciones, umbrales, valor copiado)
    limpieza.py      # aplica los tratamientos del registro de calidad y deja la traza
    calidad.py       # valida el esquema de entrada y el dataset final
  score/             # métrica de desempeño
    reglas.py        # sentido de cada indicador (mayor o menor es mejor)
    features.py      # meta cumplida y features por indicador y por equipo-mes
    agregacion.py    # score por frente, entorno y mes
```

El "modelo" no se entrena ni se guarda como `.pkl`: son reglas deterministas. Su artefacto es `score/reglas.py`, versionado en git y legible por un analista.

## Decisiones

**2.1 Limpieza y granularidad.** Se aplican los tratamientos del [registro de calidad](../1_experimentacion/README.md#13-registro-de-problemas-de-calidad). La granularidad final es **una fila por mes × equipo × indicador**. De 15.188 filas quedan 11.977:
- 2.183 se excluyen (2.182 copias exactas);
- 1.028 se promedian con otra fila del mismo mes, equipo e indicador;
- 897 se conservan, pero quedan fuera del score: sin Resultado o Meta, cumplimiento copiado o imposible.

Las 36 filas sin código no se pierden: su nombre corresponde a un solo código, así que se recuperan.

**2.2 Métrica: meta cumplida.** Por cada medición vale 1 si el Resultado alcanza la Meta, según el sentido del indicador (≥ si más es mejor, ≤ si menos es mejor), y 0 si no. El score de un equipo en un mes es el % de sus indicadores que cumplieron, todos con el mismo peso.
- **Por qué no la columna Cumplimiento:** es Resultado/Meta solo en parte de los indicadores. En las encuestas copia el puntaje, y en los indicadores de "menos es mejor" usa otras fórmulas.
- **Por qué es comparable:** no depende de la unidad ni de la escala, y ningún valor extremo domina.
- **Sentido no verificado:** en tres indicadores (Brecha Ingresos Gastos, Impactos a clientes, Índice AQR's) ningún sentido explica el dato de origen. Para ellos se usa `Cumplimiento ≥ 1` tal como llega, y se debe confirmar con su dueño.
- **Cobertura:** cuántos equipos miden un indicador es contexto, no un peso. Un indicador nuevo o medido en pocos equipos puede ser un riesgo clave, y el score de un equipo no debe depender de lo que miden los demás.

**2.3 Agregación por entorno: mediana de los equipos.** Cada equipo cuenta una vez, sin importar cuántos indicadores reporte. Un equipo extremo no mueve el resultado, lo que importa porque muchos entornos tienen 1 a 4 equipos. Junto a la mediana siempre va `n_equipos` y el rango (mín–máx).
- **Equipos con vicepresidencia:** los 11 equipos que en el catálogo cuelgan de una vicepresidencia se agrupan con su VP, con `nivel = vicepresidencia`.
- **Equipos sin entorno:** los 28 equipos sin entorno (26 que no están en el catálogo y 2 marcados así) aparecen a nivel de equipo y frente. A nivel de entorno solo se cuentan, sin calificarlos, porque juntarlos compararía áreas sin relación entre sí.

**2.5 Trazabilidad.** La hoja `trazabilidad` tiene una fila por cada fila de origen excluida, corregida o agrupada, con su número de fila en Excel, la regla y el detalle (por ejemplo `EQU0024 → EQU00024`). Las marcas que no cambian el dato quedan en la columna `marcas` del dataset.

**2.6 Reejecución.** Cada ejecución parte del archivo original, que nunca se modifica, y da el mismo resultado. Las validaciones comprueban que entrada = dataset + excluidas + agrupadas.

*(La prueba no tiene numeral 2.4.)*

## Salida

| Hoja | Contenido |
|---|---|
| `registro_calidad` | Los problemas de 1.3 con las filas afectadas en esta ejecución y su tratamiento |
| `trazabilidad` | Qué se excluyó, corrigió o agrupó, fila por fila |
| `validaciones` | Cada validación y su resultado |
| `dataset_analitico` | El dataset final: una fila por mes × equipo × indicador, con `meta_cumplida` y `marcas` |
| `indicadores` | Por indicador: sentido, unidad, cobertura (equipos, meses), tasa de cumplimiento y dispersión entre equipos |
| `equipos_mes` | Score de cada equipo por mes, n.º de indicadores y variación frente a sus 3 meses anteriores |
| `frentes_mes` · `entornos_mes` | Mediana, mínimo, máximo y n.º de equipos por frente o entorno y mes |
| `evolucion_mes` | Filas, equipos e indicadores detrás de cada mes y su score mediano |

## Limitaciones

- **Se pierde magnitud:** quedar al 99% o al 50% de la meta cuenta igual.
- **Encuestas:** su meta es 5 sobre 5, así que casi nunca se cumple (Talento + Agilidad: 0%). Bajan por igual a todos los equipos medidos en esos meses.
- **Indicadores que cambian por año:** la mezcla de indicadores cambia cada año, así que el score compara bien entre equipos de un mismo mes. A lo largo del tiempo compara "qué tanto se cumplió lo que se medía", no los mismos indicadores.
