# Bitácora de colaboración humano–IA

Herramienta: Claude Code (Claude Opus 5.5) como asistente de implementación. Las decisiones de criterio (tratamientos, métrica, agregación, hallazgos) son humanas y se toman en checkpoints por actividad.

### 2026-10-04 · Planeación · Stack y arquitectura
- **Prompt / pedido:** "Construyamos la prueba como equipo, con buenas prácticas, sin leer completo el Excel (~15k filas)."
- **Propuesta de la IA:** Python + DuckDB (SQL por capas), módulos en `src/`, presentación en PowerPoint.
- **Decisión humana:** corregida. Solo notebooks pandas numerados (`1_etl`, `2_modelo`), carpetas por etapa (`source/raw/processed/features/outputs`) + `models/`, presentación en HTML con mockup de aplicación. El estado futuro se plantea en Cloudera Data Hub por gobierno, no por volumen (20x ≈ 300k filas sigue siendo manejable en pandas).
- **Validación contra datos:** n/a (decisión de diseño).

### 2026-10-04 · Actividad 1 · Exploración sin saturar contexto
- **Prompt / pedido:** no cargar el Excel completo en la conversación.
- **Propuesta de la IA:** perfilar solo con agregados (conteos, nulos, rangos, cruces) y leer únicamente encabezados + 5 filas por hoja.
- **Decisión humana:** aceptada.
- **Validación contra datos:** `1_1_perfilamiento_source.ipynb` imprime solo resúmenes.

### 2026-10-04 · Actividad 1 · Supuesto de la IA corregido por los datos: fórmula de Cumplimiento
- **Propuesta de la IA:** asumir `Cumplimiento ≈ Resultado / Meta` para todos los indicadores.
- **Decisión humana:** corregida tras validar. En Percepción, Adopción y Talento + Agilidad `Cumplimiento = Resultado` en el 100% de las filas (puntaje ≈ 4.4 sobre 5), mientras en los indicadores tipo ratio coincide con `Resultado/Meta` topado a [0, 1.2]. Se crea la regla `DQ-CON-03`.
- **Validación contra datos:** `1_1` sección 4 (`pct_resultado = 1.0` en indicadores de escala).

### 2026-10-04 · Actividad 1 · Conteo de equipos corregido
- **Propuesta de la IA:** "el catálogo cubre 63 de 90 equipos".
- **Decisión humana:** corregida. Al normalizar códigos (`Equ00074` → `EQU00074`, `EQU0024` → `EQU00024`) quedan 89 equipos; 26 sin entorno (1.473 filas).
- **Validación contra datos:** `1_1` sección 6 y regla `DQ-VAL-01`.

### 2026-10-04 · Checkpoint 1 · Tope de Cumplimiento: propuesta de la IA corregida por el humano
- **Propuesta de la IA:** topar todo Cumplimiento fuera de [0, 1.2] (61 filas), asumiendo que 1.2 es una regla general del negocio.
- **Decisión humana:** descartada. "Cumplimiento normaliza resultado vs meta y los indicadores miden dinero, tiempo, porcentajes y errores; antes de topar, revisar cada caso (p. ej. Gestión del Gasto con −1873)". Se pidió una fase exploratoria más profunda (`1_exploratorio/`).
- **Validación contra datos:** `1_2_perfilamiento_indicadores` infiere fórmula/tope por indicador. El tope 1.2 aplica solo a algunos (Apps modernizadas, Cumplimiento presupuestal, Obsolescencia); Regulatorio topa en 1; Neon y Ejecución Presupuestal no topan. Gestión del Gasto usa `1 − (Resultado − Meta)` y su extremo viene de un Resultado en otra unidad.

### 2026-10-04 · Checkpoint 1 · Decisiones tomadas
- Llaves repetidas (encuestas 202502 y repeticiones): **consolidar con promedio por llave** (humano, opción recomendada por la IA).
- Equipos con padre Vicepresidencia: **"Sin entorno" en la vista de entornos, conservando la VP** para darles lectura propia (humano; la IA había propuesto un grupo VP dentro del ranking).

### 2026-10-04 · Actividad 1 · Hallazgos nuevos del perfilamiento por indicador
- **Propuesta de la IA:** inferir automáticamente la fórmula de cada indicador probando 6 fórmulas × 3 topes contra el Cumplimiento reportado.
- **Validación contra datos:** el primer intento con tolerancia 1e-3 confundía `Resultado/Meta` con `1 + (Resultado − Meta)` cuando ambos ≈ 1 (Disponibilidad); se corrigió a tolerancia 1e-6 y prioridad explícita ante empates. Aparecieron dos problemas no vistos antes: el valor 1.014683 copiado en 416 filas de Disponibilidad/Incidentes y 19 equipos con Cumplimiento idéntico 155.42 en Incidentes 202408.

### 2026-10-05 · Reorganización · Nomenclatura y EDA por hipótesis
- **Pedido humano:** numerar carpetas de datos (`0_source`, `1_raw`…), renombrar notebooks con términos estándar (`eda`, `profiling`, `quality_check`), plantear hipótesis explícitas en el EDA, organizar las reglas de calidad como el Excel (hoja → columna) y eliminar archivos que nadie usa (`manifiesto_ingesta.json`).
- **Propuesta de la IA (previa):** reglas agrupadas por dimensión de calidad (`DQ-UNI-01`, `DQ-COM-02`…) y un manifiesto de ingesta.
- **Decisión humana:** corregida. Ahora `regla_id = <hoja>.<columna>.<nn>` con referencia a la hipótesis del EDA (H01–H23) que la originó; el manifiesto se eliminó.
- **Validación contra datos:** 23 hipótesis evaluadas (4 se cumplen, 18 no, 1 parcial); 29 reglas en `registro_calidad.csv`; pipeline re-ejecutado de principio a fin.

### 2026-10-05 · Reinicio · Simplificar para el usuario de negocio
- **Pedido humano:** "fuimos muy rápido más allá de lo esperado". Volver al enunciado: rol, contexto, actividad y la precaución "no se premia usar más herramientas, sino elegir bien". Somos un equipo que facilita la vida a la operación; algo complejo genera deuda técnica.
- **Propuesta de la IA (previa):** 5 capas de datos, 5 notebooks de ETL, 29 reglas con ids por hoja/columna, inferencia automática de fórmulas.
- **Decisión humana:** corregida. Nueva rama `simplificacion` con README base y 4 carpetas (`0_datos`, `1_experimentacion`, `2_transformacion`, `3_aplicacion`). Actividad 1 resuelta con 2 notebooks legibles para analistas y 15 problemas de calidad. El trabajo anterior queda en `main`.
- **Validación contra datos:** se profundizó en cómo se comunican las hojas: 10 de 25 indicadores coinciden con el catálogo, 2 indicadores del catálogo sin ningún equipo (misma definición), 146 escrituras de código para 89 equipos, 26 equipos fantasma (8 activos).

### 2026-10-05 · Actividad 1 · Conclusión de la IA corregida por los datos
- **Propuesta de la IA:** "con los códigos tal como vienen solo cruzan 46 equipos con el catálogo".
- **Decisión humana:** corregida tras ejecutar: cruzan 63 tal cual y 63 corregidos; el problema real es que 89 equipos aparecen escritos de 146 formas (minúsculas y dígitos de menos), lo que hace que un equipo parezca varios.
- **Validación contra datos:** `1_eda.ipynb`, sección 4.
