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

### 2026-10-06 · Actividad 1 · Visualización y rol de README vs notebooks
- **Pedido humano:** respuestas tipo pregunta → respuesta, etiquetas de color por tipo de problema (buscando una agrupación óptima, no la sugerida), más gráficas que digan mucho, y READMEs enfocados en cómo ejecutar.
- **Propuesta de la IA:** 5 categorías de calidad que responden una pregunta cada una (Faltantes, Duplicados, Formato, Catálogo, Valores). Se reemplazó la propuesta inicial (faltantes / duplicados / …) moviendo "meses con pocos equipos" a Faltantes y separando Formato (escritura) de Catálogo (referencias entre hojas). Las respuestas de la actividad 1 quedan en el README raíz porque la prueba exige que el README las contenga; los READMEs de carpeta solo explican cómo ejecutar.
- **Validación contra datos:** la lectura de la gráfica de indicadores decía "Vulnerabilidades e Incidentes llevan más de dos años"; los datos muestran 15 meses. Se corrigió a "Percepción y Adopción: 25 meses y más de 70 equipos".

### 2026-10-06 · Actividad 1 · Un notebook por numeral y código contraído
- **Pedido humano:** un notebook por numeral (1.1, 1.2, 1.3) con el enunciado y una tabla de contenido arriba, secciones numeradas (1.1.a…), código oculto para que se lean los resultados, y sin `registro_calidad.csv` (el notebook es el registro).
- **Propuesta de la IA:** celdas de código con `source_hidden` (JupyterLab las muestra contraídas) y etiqueta `hide-input` para exportar sin código; el registro final se muestra como tabla con la categoría como etiqueta de color.
- **Validación:** se abrió JupyterLab en el navegador y se comprobó que el código aparece contraído con el resultado visible y que el diagrama mermaid renderiza. En 1.1.c el texto decía "85% de los indicadores del catálogo aparecen en la base"; con coincidencia exacta la gráfica muestra 77% (10 de 13) y se corrigió.

### 2026-10-07 · Actividad 1 · Revisión de los notebooks editados y modelo de datos propuesto
- **Pedido humano:** revisar las mejoras hechas a mano en los tres notebooks (funciones reutilizables, una gráfica por sección en 1.3, nueva clasificación de duplicados) y proponer en el README el modelo de datos al que se debería apuntar.
- **Propuesta de la IA:** cinco tablas (Mediciones, Equipos, Entornos, Indicadores, Frentes) donde cada dato vive una vez con un código estable; Mediciones solo guarda códigos. Cada decisión se justifica con un hallazgo y enlaza a su sección del notebook. Desde ahora los notebooks se editan directamente (ya no se regeneran desde scripts) para no borrar los cambios humanos.
- **Validación contra datos:** al ejecutar la versión humana aparecieron dos cifras que la IA había escrito a mano en el README y estaban mal: la mediana de las encuestas es 4,6 (no 4,4, que era la de Percepción sola) y el valor copiado 1.014683 también aparece en 1 fila de Vulnerabilidades. La clasificación humana además separó 13 filas "iguales salvo el nombre del equipo" que antes no estaban en el registro. Los diagramas mermaid del README se validaron con el parser de mermaid 11.

### 2026-10-07 · Actividad 1 · Diagramas legibles y títulos afirmativos
- **Pedido humano:** explicar PK, FK y tipos de dato en el diagrama; mostrar las listas cerradas como `enum [EQU, CEX]`; títulos de README afirmativos en vez de preguntas (el humano ya había renombrado 1.1.b a "Arquitectura de Datos según Evidencia Empírica").
- **Propuesta de la IA:** tipos en español (`texto`, `fecha`, `decimal`, `enum`), formato de cada código como aclaración (EQU00000, IND000…), una tabla de notación bajo el diagrama, la arquitectura empírica con la misma notación, y la tabla 1.2 como "Validación | Resultado".
- **Validación:** los tres diagramas mermaid se renderizaron con mermaid 11 sin errores.

### 2026-10-07 · Actividad 1 · La estructura propuesta responde 1.1
- **Pedido humano:** releyendo la prueba ("indica cómo separarías la información en tablas o catálogos"), la respuesta es la estructura propuesta y no el modelo empírico: quitar el diagrama del notebook 1.1.b y explicar en el README de experimentación qué es cada entidad y por qué es una buena estructura; el README principal solo muestra el diagrama.
- **Propuesta de la IA:** 1.1.b del notebook enlaza al README; el README del módulo une en 1.1 el diagrama, la notación, el significado de cada entidad y la tabla hallazgo → decisión. Además, Mermaid no permite poner `PK`/`FK` antes del tipo (son palabras reservadas): el orden más cercano a lo pedido es nombre | tipo | llave.
- **Validación:** el notebook 1.1 se ejecutó completo tras quitar el diagrama y las funciones que solo él usaba.

### 2026-10-07 · Actividad 2 · Scripts en vez de notebooks y métrica de meta cumplida
- **Pedido humano:** un proceso recurrente que el equipo de estrategia pueda administrar: un solo archivo de Python que lea la carpeta de entrada y publique un Excel con el registro de calidad, lo limpiado y las vistas por equipo, entorno y fecha. Carpetas separadas para la ETL y el "modelo" de score. Hipótesis humana: hay que recalcular Cumplimiento como Resultado/Meta porque no coincide. Idea de dar más peso a los indicadores que miden más equipos.
- **Propuesta de la IA:** `2_transformacion/src/main.py` con `etl/` y `score/`, y las reglas de negocio en archivos `reglas.py` editables. Se descartó guardar la preparación como `.pkl`: son reglas deterministas, no un modelo entrenado; un pickle las esconde del analista, depende de versiones y es inseguro al cargarse. La métrica es la meta cumplida según el sentido del indicador; la mediana de equipos por entorno; los equipos sin entorno no se agrupan entre sí.
- **Validación contra datos:**
  - **Fórmula de Cumplimiento:** la hipótesis humana era correcta solo en parte. Cumplimiento = Resultado/Meta en ~15 de 25 indicadores. En las encuestas copia el puntaje, y en Obsolescencia, Pérdida por fraude y Gestión del Gasto coincide con "menos es mejor". Recalcular todo como Resultado/Meta habría castigado a esos indicadores, y eso llevó a la métrica de meta cumplida.
  - **Ponderar por cobertura:** se descartó con el propio argumento humano (un indicador en pocos equipos puede ser un riesgo clave). La cobertura queda como contexto.
  - **Corrección a la actividad 1:**
    - Las 36 filas "sin código" sí tienen nombre, y cada nombre corresponde a un solo código. Se recuperan en vez de excluirse.
    - Las 13 filas que 1.3 clasificó como "iguales salvo el nombre" eran equipos distintos sin código, no duplicados. Se corrigió 1.3: el problema desaparece y el registro queda en 15 problemas; las filas sin código pasan de "excluir" a "corregir". En el pipeline la regla se mantiene como control (1 fila tras recuperar códigos).
  - **Verificación del proceso:** la salida es idéntica entre dos ejecuciones. Con un archivo sin la columna Meta, el proceso no publica nada y termina con código 1.
- **Decisión humana:** las encuestas (meta 5 de 5, casi nunca se cumple) se mantienen en el score y se declara la limitación.
