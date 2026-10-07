# 1. Experimentación

Exploración y calidad del archivo original (actividad 1). Cada notebook responde un numeral; las gráficas y el paso a paso están dentro de él, con el código contraído para leer solo resultados.

## Ejecución

Desde la raíz del repositorio (Python 3.12+ y [uv](https://docs.astral.sh/uv/)):

```bash
uv sync
uv run jupyter lab
```

Abrir `1_experimentacion/notebooks/` y ejecutar cada notebook de arriba a abajo, en orden. Los notebooks solo leen `0_datos/KPIS_historico.xlsx`; no escriben archivos.

| # | Notebook | Contenido |
|---|---|---|
| 1.1 | [`1_1_exploracion_datos.ipynb`](notebooks/1_1_exploracion_datos.ipynb) | Qué representa cada fila, cómo separar en tablas y si el dataset y los catálogos coinciden |
| 1.2 | [`1_2_validacion_catalogos.ipynb`](notebooks/1_2_validacion_catalogos.ipynb) | Contraste con el catálogo de indicadores y el de entornos; diferencias documentadas |
| 1.3 | [`1_3_evaluacion_calidad.ipynb`](notebooks/1_3_evaluacion_calidad.ipynb) | Registro de problemas de calidad: problema, evidencia, impacto y tratamiento |

## Conclusiones

### 1.1 Arquitectura empírica de datos

El resultado de **un indicador, para un equipo, en un mes**. La identifican `Corte` + `Codigo_EQU` + `Indicador`: el frente depende del indicador y el nombre depende del código del equipo. Tal como viene en el Excel, la información se puede leer como cuatro tablas: es la **arquitectura empírica**, lo que los datos dejan ver sin intervenirlos. La notación se explica en la arquitectura propuesta.

```mermaid
erDiagram
    INDICADORES ||--o{ MEDICIONES : "Indicador"
    EQUIPOS ||--o{ MEDICIONES : "Codigo_EQU"
    ENTORNOS ||--o{ EQUIPOS : "Codigo_Padre"
    MEDICIONES {
        texto Corte PK "AAAAMM"
        texto Codigo_EQU PK, FK
        texto Indicador PK, FK "el nombre hace de llave"
        decimal Resultado
        decimal Meta
        decimal Cumplimiento
    }
    EQUIPOS {
        texto Codigo_EQU PK
        texto EQU
        enum Tipo "[EQU, CEX]"
        texto Codigo_Padre FK
    }
    ENTORNOS {
        texto Codigo_Padre PK
        texto Nombre_Padre
    }
    INDICADORES {
        texto Indicador PK
        texto Frente
        texto Definicion
        enum Unidad "[Porcentaje, Escala, Cantidad]"
    }
```

### 1.2 Coincidencia del dataset con los catálogos

| Validación | Resultado |
|---|---|
| Indicadores del dataset registrados en el catálogo | **Solo 10 de 25 (40%)**. Los otros 15 (14 que no aparecen y 1 escrito distinto) representan el **57% de las filas** |
| Indicadores del catálogo con mediciones | **11 de 13**: 2 nunca se miden y tienen la misma definición (un índice consolidado de agilidad) |
| Nombres de frente | El frente de agilidad tiene **3 nombres** en el tiempo; el error "Modeos…" viene del propio catálogo |
| Escritura de los códigos de equipo | **146 formas de escribir 89 equipos** (minúsculas, dígitos de menos) |
| Equipos del dataset registrados en el catálogo | **63 de 89 (71%)**. 26 son equipos fantasma: 18 históricos y **8 activos en 2026** que faltan en el catálogo |
| Equipos con entorno asignado | **Solo 56% (50 de 89)**. 11 cuelgan de una vicepresidencia y 2 están marcados "sin entorno" |

### 1.3 Registro de problemas de calidad

| Tipo | Problema | Evidencia | Tratamiento |
|---|---|---|---|
| ![Faltantes](https://img.shields.io/badge/Faltantes-9063cd) | Filas sin código de equipo | 36 filas (0,2%) | excluir |
| ![Faltantes](https://img.shields.io/badge/Faltantes-9063cd) | Nombre de equipo vacío | 6.185 filas (40,7%) | corregir desde el catálogo |
| ![Faltantes](https://img.shields.io/badge/Faltantes-9063cd) | Cumplimiento vacío | 265 filas; 59 recalculables | corregir / excluir |
| ![Faltantes](https://img.shields.io/badge/Faltantes-9063cd) | Meses con pocos equipos | 202510: 20 equipos vs 64 normal | marcar |
| ![Duplicados](https://img.shields.io/badge/Duplicados-59cbe8) | Filas repetidas exactamente | 2.182 filas (14,4%) | excluir (se deja una) |
| ![Duplicados](https://img.shields.io/badge/Duplicados-59cbe8) | Filas iguales salvo el nombre del equipo | 13 filas: la misma medición, una con EQU vacío | excluir (se deja la que tiene nombre) |
| ![Duplicados](https://img.shields.io/badge/Duplicados-59cbe8) | Mismo equipo, indicador y mes con valores distintos | 1.265 filas; 962 son respuestas de encuesta | corregir (promedio) |
| ![Formato](https://img.shields.io/badge/Formato-fdda24) | Código de equipo mal escrito | 325 filas (2,1%) | corregir |
| ![Formato](https://img.shields.io/badge/Formato-fdda24) | Un frente con tres nombres | 3.089 filas (20,3%) | corregir (homologar) |
| ![Catálogo](https://img.shields.io/badge/Cat%C3%A1logo-ff7f41) | Equipos fantasma | 1.473 filas (9,7%), 26 equipos | marcar "Sin entorno" |
| ![Catálogo](https://img.shields.io/badge/Cat%C3%A1logo-ff7f41) | Equipos con vicepresidencia o sin entorno | 2.218 filas (14,6%), 13 equipos | marcar "Sin entorno" (se conserva la VP) |
| ![Catálogo](https://img.shields.io/badge/Cat%C3%A1logo-ff7f41) | Indicadores sin definición | 14 de 25; 8.267 filas (54,4%) | marcar y documentar |
| ![Catálogo](https://img.shields.io/badge/Cat%C3%A1logo-ff7f41) | Indicadores del catálogo que nadie mide | 2 de 13 | aceptar y reportar |
| ![Valores](https://img.shields.io/badge/Valores-f5b6cd) | Cumplimiento en escalas distintas | 5.498 filas (36,2%): mediana 4,6 en encuestas vs 1,0 en el resto | corregir (Resultado / Meta) |
| ![Valores](https://img.shields.io/badge/Valores-f5b6cd) | Cumplimientos imposibles (155 y −1873) | 22 filas | marcar y excluir del análisis |
| ![Valores](https://img.shields.io/badge/Valores-f5b6cd) | Cumplimiento copiado (1.014683) | 530 filas (3,5%), casi todas en Disponibilidad e Incidentes | marcar y excluir del análisis |

Impacto y detalle: [`notebooks/1_3_evaluacion_calidad.ipynb`](notebooks/1_3_evaluacion_calidad.ipynb).

### Arquitectura de datos propuesta

La arquitectura empírica funciona como punto de partida, pero 1.2 y 1.3 muestran que no protege la información: los nombres cambian, un mismo código se escribe de varias formas y los catálogos no reconocen buena parte de lo que se mide. Por eso se propone un modelo donde **cada dato vive una sola vez, en su tabla, identificado por un código que no cambia**, y las mediciones solo apuntan a esos códigos:

```mermaid
erDiagram
    FRENTES ||--o{ INDICADORES : "agrupa"
    INDICADORES ||--o{ MEDICIONES : "se mide en"
    EQUIPOS ||--o{ MEDICIONES : "reporta"
    ENTORNOS ||--o{ EQUIPOS : "contiene"
    MEDICIONES {
        fecha corte PK "primer día del mes"
        texto codigo_equipo PK, FK "EQU00000"
        texto codigo_indicador PK, FK "IND000"
        decimal resultado
        decimal meta
        decimal cumplimiento "resultado frente a la meta: 1 = meta cumplida"
    }
    EQUIPOS {
        texto codigo_equipo PK "EQU00000 o CEX00000"
        texto nombre
        enum tipo "[EQU, CEX]"
        texto codigo_entorno FK
        enum estado "[vigente, histórico]"
    }
    ENTORNOS {
        texto codigo_entorno PK "ENX0000 o VPX0000"
        texto nombre
        enum nivel "[entorno, vicepresidencia, sin entorno]"
    }
    INDICADORES {
        texto codigo_indicador PK "IND000"
        texto nombre
        texto codigo_frente FK
        texto definicion
        enum unidad "[porcentaje, escala, cantidad]"
        enum sentido "[mayor es mejor, menor es mejor]"
    }
    FRENTES {
        texto codigo_frente PK "FRE00"
        texto nombre
    }
```

| Notación | Significado |
|---|---|
| `PK` | Llave primaria: identifica cada fila y no se repite. En Mediciones son tres columnas juntas: un mes, un equipo y un indicador |
| `FK` | Llave foránea: apunta a la llave primaria de otra tabla y solo acepta valores que existan allí |
| `enum "[a, b]"` | Lista cerrada: la columna solo admite los valores entre corchetes |
| `texto` · `fecha` · `decimal` | Tipo de dato de la columna; el texto entre comillas es el formato o una aclaración |
| Línea `\|\|──o{` | Relación uno a muchos: el extremo con doble raya es el "uno" y el de tres patas el "muchos". Un frente agrupa muchos indicadores; cada indicador pertenece a un solo frente |

| Hallazgo | Decisión de diseño | Evidencia |
|---|---|---|
| 146 escrituras para 89 equipos y nombre vacío en 41% de las filas | Mediciones guarda solo el `codigo_equipo` normalizado; el nombre vive una vez en Equipos | 1.2.d · 1.3.a |
| El mismo indicador se escribe distinto entre hojas | Cada indicador tiene un `codigo_indicador` propio (hoy no existe: se crea al homologar); el nombre es solo una etiqueta | 1.2.a |
| El frente de agilidad tuvo tres nombres | Mediciones no repite el frente: lo hereda de su indicador, y cada frente existe una vez en Frentes | 1.2.c |
| Encuestas en otra escala; no se sabe si más alto es mejor | Indicadores declara unidad y sentido, para calcular el cumplimiento igual en todos | 1.3.e |
| La columna "padre" mezcla entornos, vicepresidencias y "sin entorno" | Entornos tiene un `nivel` explícito | 1.2.f |
| 26 equipos fantasma, 18 de ellos históricos | Equipos tiene un `estado`: la historia se conserva sin confundirse con lo vigente | 1.2.e |
| Mediciones repetidas o en conflicto | Corte + equipo + indicador es la llave: una sola medición por mes | 1.3.b |

Con este modelo, una medición solo entra si su equipo y su indicador existen en los catálogos: los problemas de catálogo se detienen en la carga en vez de descubrirse en el análisis. Es el punto de partida de la transformación (actividad 2).
