# Entrevista Técnica DE Game

Prueba técnica – Ingeniero de Datos N2, Estrategia Corporativa. Se presenta la construcción de una base confiable, junto con su análisis y propuesta de automatización.

## Estructura

```text
0_datos/              # 1_crudos (nunca se modifica), 2_procesados y 3_score
1_experimentacion/    # exploración y calidad de datos (actividad 1)
2_transformacion/     # limpieza y dataset analítico (actividades 2 y 3)
3_aplicacion/         # proceso recurrente, decisiones tecnológicas y uso de IA (actividad 4)
```

Cada módulo tiene su README con cómo ejecutarlo y el detalle de sus resultados.

## Conclusiones por módulo

### 1. Experimentación

En esta sección se entienden los datos, desde su forma hasta el contenido que yace en el archivo. Empíricamente se evidencia una arquitectura de cuatro tablas (mediciones, equipos, entornos e indicadores), pero con problemas estructurales grandes como:
- Más de la mitad de las filas usan indicadores que el catálogo no conoce
- Un mismo equipo aparece escrito de varias formas
- Más de un tercio de las filas reporta el cumplimiento en otra escala

Como conclusión, se registran 16 problemas de calidad con su tratamiento, sin embargo, para evitar que se repitan se propone un modelo donde cada dato vive una sola vez, identificado por un código estable, y las mediciones solo apuntan a esos códigos:

```mermaid
erDiagram
    ENTORNOS ||--o{ EQUIPOS : "contiene"
    EQUIPOS ||--o{ MEDICIONES : "reporta"
    INDICADORES ||--o{ MEDICIONES : "se mide en"
    FRENTES ||--o{ MEDICIONES : "agrupa"
    MEDICIONES {
        corte fecha PK "primer día del mes"
        cod_equipo texto PK, FK "EQU00000"
        cod_indicador texto PK, FK "IND000"
        cod_frente texto FK "FRE00"
        resultado decimal
        meta decimal
        cumplimiento decimal
    }
    EQUIPOS {
        cod_equipo texto PK "EQU00000 o CEX00000"
        nombre texto
        cod_entorno texto FK
    }
    ENTORNOS {
        cod_entorno texto PK "ENX0000, VPX0000 o SIN0000"
        nombre texto
    }
    INDICADORES {
        cod_indicador texto PK "IND000"
        nombre texto
        definicion texto
        unidad enum "[porcentaje, escala, cantidad]"
        sentido enum "[mayor, menor, no verificado]"
    }
    FRENTES {
        cod_frente texto PK "FRE00"
        nombre texto
    }
```

### 2. Transformación

Un solo comando (`uv run python 2_transformacion/src/main.py`) limpia el archivo original y publica dos Excel: los **datos procesados**, separados en el modelo propuesto (mediciones, equipos, entornos, indicadores y frentes, con los catálogos completados y la trazabilidad de cada fila tocada), y el **score** por equipo, frente y entorno. La métrica es la **meta cumplida** según el sentido de cada indicador; los entornos se comparan con la **mediana de sus equipos**, y los equipos sin entorno no se mezclan en un grupo artificial.

### 3. Aplicación

Pendiente.
