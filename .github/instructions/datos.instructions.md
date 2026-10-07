---
applyTo: "2_transformacion/**,1_experimentacion/**"
description: Reglas de datos, calidad y trazabilidad
---

# Datos y calidad

## Tratamientos
- **Código de equipo:** mayúsculas y 5 dígitos (`Equ00074 → EQU00074`, `EQU0024 → EQU00024`). Si está vacío, se toma del nombre, solo cuando ese nombre corresponde a un único código.
- **Frente:** se corrigen solo los errores de digitación demostrables ("Modeos…"). Un frente fuera del catálogo se conserva y se reporta.
- **Resultado, Meta o Cumplimiento vacíos:** se excluye la fila. Nunca se imputa ni se recalcula un valor faltante.
- **Filas repetidas:** se deja una. Varias filas del mismo mes, equipo e indicador con valores distintos se promedian en una.
- **Cumplimiento:** se conservan `cumplimiento_original` y `cumplimiento_procesado`. El procesado es Resultado / Meta, con meta positiva, solo con evidencia:
  - **Escala:** el original es igual al Resultado (encuestas).
  - **Valor copiado:** el mismo valor aparece en 5 o más equipos del mismo indicador y mes con resultados distintos, en indicadores donde más es mejor, salvo que sea un tope que el resultado supera.
  - **Sin condiciones extra:** no se agrega "solo si el valor cambia". Resultado 1 con meta 1 y Resultado 0 con meta 0 son válidos.
- **Indicadores** se cruzan con el catálogo en minúsculas y sin tildes.

## Modelo normalizado
- **Cinco tablas** con códigos estables:
  - `frentes` (`FRE00`)
  - `indicadores` (`IND000`, con `cod_frente`, `definicion`, `unidad` y `sentido`; un mismo nombre en dos frentes son dos indicadores)
  - `entornos` (`ENX`/`VPX` del catálogo y `SIN0000` "Sin entorno")
  - `equipos` (`cod_equipo`, `nombre`, `cod_entorno`)
  - `mediciones` (`corte`, `cod_equipo`, `cod_indicador`, `resultado`, `meta`, `cumplimiento_original`, `cumplimiento_procesado`), sin columnas que se puedan obtener de otra tabla
- **Catálogos completos:** no se borran los indicadores que nadie mide; los que se miden sin estar en el catálogo se agregan como "Pendiente".
- **Modelo simple:** sin columnas derivables ni poco dicientes (`estado`, `nivel`, `tipo`).

## Calidad y trazabilidad
- **Traza:** `fila_excel`, `regla`, `accion` (`excluida`, `corregida`, `completada` o `agrupada`) y un `detalle` literal (`Codigo_EQU: Equ00074 → EQU00074`).
- **`registro_calidad`:** una fila por regla, con su problema, tratamiento y filas afectadas. No se incluye nada que un analista no pueda entender ni verificar.
- **Validaciones antes de publicar:**
  - llave única (mes, equipo, indicador);
  - códigos con formato;
  - mediciones sin vacíos;
  - cada código existe en su tabla;
  - filas originales = mediciones + excluidas + agrupadas.

## Score
- **Meta cumplida:** 1 si el resultado alcanza la meta según el sentido (≥ mayor, ≤ menor) y 0 si no. En sentido "no verificado" se usa `cumplimiento_procesado ≥ 1`.
- **Peso:** todos los indicadores pesan igual; la cobertura es contexto, no un peso.
- **Entorno:** mediana de los equipos con `n_equipos` y rango. "Sin entorno" se cuenta pero no se califica.
