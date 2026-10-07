# Entrevista Técnica DE Game

Prueba técnica – Ingeniero de Datos N2, Estrategia Corporativa. Se presenta la construcción de una base confiable, junto con su análisis y propuesta de automatización.

## Estructura

```text
0_datos/              # archivo original (nunca se modifica)
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

### 2. Transformación

Pendiente.

### 3. Aplicación

Pendiente.
