# 2. Transformación

Proceso que convierte el archivo original en datos limpios y en un score comparable entre equipos, frentes y entornos (actividad 2). Son scripts de Python con un solo punto de entrada, para que el equipo de estrategia los ejecute cada mes sin abrir un notebook.

## Ejecución

Desde la raíz del repositorio:

```bash
uv run python 2_transformacion/src/main.py
```

Por cada `.xlsx` de `0_datos/1_originales/` publica dos archivos y deja una línea en `0_datos/ejecucion.log`:

| Archivo | Hojas |
|---|---|
| `0_datos/2_procesados/<archivo>_procesado.xlsx` | `datos` (la sábana limpia), `indicadores` (catálogo actualizado), `registro_calidad`, `trazabilidad`, `validaciones` |
| `0_datos/3_score/<archivo>_score.xlsx` | `mediciones` (meta cumplida por fila), `indicadores`, `equipos_mes`, `frentes_mes`, `entornos_mes`, `evolucion_mes` |

Si al archivo le falta una hoja o columna, o una validación falla, **no publica nada** y termina con código 1, que cualquier orquestador (cron, Power Automate, Cloudera) detecta como error.

```text
src/
  main.py            # originales → etl → procesados → score
  etl/
    reglas.py        # reglas de negocio editables: formatos, frentes mal escritos, sentido de cada indicador
    limpieza.py      # una función por regla; cada una devuelve los datos tratados y su traza
    catalogos.py     # entorno de cada equipo y catálogo de indicadores actualizado
    calidad.py       # validaciones y registro de calidad
  score/
    features.py      # meta cumplida, resumen por indicador y score por equipo-mes
    agregacion.py    # score por frente, entorno y mes
```

El score no se entrena ni se guarda como `.pkl`: son reglas deterministas, versionadas en git y legibles por un analista.

## Datos procesados (2.1)

**Granularidad:** una fila por **mes × equipo × indicador**, con las columnas `corte`, `cod_equipo`, `equipo`, `cod_entorno`, `entorno`, `frente`, `indicador`, `resultado`, `meta`, `cumplimiento` y `fila_origen`, que es la fila del Excel original.

De 15.188 filas quedan 11.521. Las reglas se aplican en este orden:

| Regla | Qué hace |
|---|---|
| Código de equipo | Lo pasa a mayúsculas y 5 dígitos. Si está vacío, lo toma del nombre del equipo, porque cada nombre corresponde a un solo código |
| Frente | Corrige "Modeos…" a "Modelos de trabajo y Agilidad". **"Talento + Agilidad" se conserva:** no está en el catálogo y sus indicadores no coinciden con los de ningún frente, así que se reporta para actualizar el catálogo |
| Resultado o Meta vacíos | Se excluye la fila: no hay medición o no hay contra qué compararla |
| Filas repetidas | Se excluyen; se deja una |
| Valores en conflicto | Varias filas del mismo mes, equipo e indicador con valores distintos (sobre todo respuestas de encuesta) se promedian en una |
| Nombre de equipo vacío | Se toma de otras filas del mismo código o del catálogo |
| Cumplimiento | Donde más es mejor y la meta es positiva, se recalcula como Resultado / Meta. Eso corrige las encuestas (traían el puntaje), los valores copiados y los vacíos. En los demás se conserva el de origen, y si es imposible (más de 3) se deja vacío |
| Entorno | Se toma de `catalogo_entornos`; las vicepresidencias cuentan como entorno. Los equipos que no están en el catálogo o están marcados sin entorno quedan en "Sin entorno" |

**Catálogo de indicadores actualizado:** los 25 indicadores medidos y los 2 del catálogo que nadie mide, con su `sentido` (mayor o menor es mejor). Los que no estaban en el catálogo aparecen con su definición y unidad como pendientes de documentar.

**Trazabilidad (2.5):** cada fila tocada queda en la hoja `trazabilidad`, con su número de fila en Excel, la regla, la acción (`excluida`, `corregida`, `completada` o `agrupada`) y qué cambió. Por ejemplo, `Cumplimiento: 9.434 → 0.943` o `Codigo_EQU: Equ00074 → EQU00074`. La hoja `registro_calidad` resume cuántas filas tocó cada regla.

**Reejecución (2.6):** cada ejecución parte del archivo original, que nunca se modifica, y da el mismo resultado. Las validaciones comprueban que filas originales = procesadas + excluidas + agrupadas.

## Score

**2.2 Métrica: meta cumplida.** Por cada medición vale 1 si el resultado alcanza la meta según el sentido del indicador (≥ si más es mejor, ≤ si menos es mejor), y 0 si no. El score de un equipo en un mes es la proporción de sus indicadores que cumplieron, todos con el mismo peso.
- **Por qué es comparable:** no depende de la unidad ni de la escala, y ningún valor extremo domina.
- **Sentido no verificado:** en tres indicadores (Brecha Ingresos Gastos, Impactos a clientes, Índice AQR's) ningún sentido explica el dato de origen. Para ellos se usa `Cumplimiento ≥ 1` tal como llega, y se debe confirmar con su dueño.
- **Cobertura:** cuántos equipos miden un indicador es contexto, no un peso. Un indicador medido en pocos equipos puede ser un riesgo clave.

**2.3 Agregación por entorno: mediana de los equipos.** Cada equipo cuenta una vez, sin importar cuántos indicadores reporte, y un equipo extremo no mueve el resultado; muchos entornos tienen 1 a 4 equipos. Junto a la mediana siempre van `n_equipos` y el rango.
- **Vicepresidencias:** los equipos que cuelgan de una vicepresidencia se agrupan con ella.
- **Equipos sin entorno:** aparecen a nivel de equipo y frente. A nivel de entorno solo se cuentan, sin calificarlos como grupo, porque juntarlos mezclaría áreas sin relación entre sí.

*(La prueba no tiene numeral 2.4.)*

## Limitaciones

- **Se pierde magnitud:** quedar al 99% o al 50% de la meta cuenta igual.
- **Encuestas:** su meta es el puntaje máximo, así que casi nunca se cumple (Talento + Agilidad: 0%). Bajan por igual a todos los equipos medidos en esos meses.
- **Indicadores que cambian por año:** la mezcla de indicadores cambia cada año, así que el score compara bien entre equipos de un mismo mes. A lo largo del tiempo compara "qué tanto se cumplió lo que se medía", no los mismos indicadores.
