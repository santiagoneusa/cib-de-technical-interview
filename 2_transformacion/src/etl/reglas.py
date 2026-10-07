"""Reglas de negocio de la limpieza. Se editan aquí, sin tocar la lógica de limpieza.py ni catalogos.py."""

# Columnas de la hoja query y su nombre en el dataset procesado
COLUMNAS = {
    "Corte": "corte", "Codigo_EQU": "cod_equipo", "EQU": "equipo", "Frente": "frente",
    "Indicador": "indicador", "Resultado": "resultado", "Meta": "meta", "Cumplimiento": "cumplimiento",
}

# Granularidad final: una fila por mes × equipo × indicador
LLAVE = ["corte", "cod_equipo", "indicador"]

# Código de equipo: mayúsculas y 5 dígitos (EQU0024 → EQU00024)
PATRON_CODIGO = r"^([A-Z]{3})0(\d{3})$"
REEMPLAZO_CODIGO = r"\g<1>00\2"
FORMATO_CODIGO = r"^(EQU|CEX)\d{5}$"

# Errores de digitación en el nombre del frente. "Talento + Agilidad" NO está aquí: es un frente
# que no aparece en el catálogo y no se puede asumir que sea el mismo que "Modelos de trabajo y Agilidad".
FRENTES_MAL_ESCRITOS = {"Modeos de trabajo y Agilidad": "Modelos de trabajo y Agilidad"}

# Sentido de cada indicador: si cumplir es quedar por encima ("mayor") o por debajo ("menor") de la meta.
# Se dedujo comparando el Cumplimiento de origen con Resultado vs Meta. En "no verificado" ningún sentido
# explica el dato de origen: se confía en su Cumplimiento y se debe confirmar con el dueño del indicador.
SENTIDO = {
    "Obsolescencia": "menor",
    "Pérdida esperada por fraude": "menor",
    "Gestión del Gasto": "menor",
    "Brecha Ingresos Gastos": "no verificado",
    "Impactos a clientes activos por fricciones, quejas y requerimientos": "no verificado",
    "Índice AQR's": "no verificado",
}
SENTIDO_POR_DEFECTO = "mayor"

# Cumplimiento: diferencia a partir de la cual el dato de origen no coincide con Resultado / Meta,
# y valor a partir del cual es imposible (más de 3 veces la meta)
TOLERANCIA_CUMPLIMIENTO = 0.001
CUMPLIMIENTO_MAXIMO = 3

# Entorno: en catalogo_entornos, Codigo_Padre empieza por ENX (entorno) o VPX (vicepresidencia);
# cualquier otro valor ("CdE sin Entorno") o un equipo que no está en el catálogo queda sin entorno
PREFIJOS_ENTORNO = ("ENX", "VPX")
SIN_ENTORNO = "Sin entorno"
PENDIENTE = "Pendiente: no está en catalogo_indicadores"

# Registro de calidad: cada regla con el problema que resuelve y su tratamiento, en orden de ejecución
REGLAS = {
    "codigo_mal_escrito": ("Código de equipo en minúsculas o con un dígito de menos", "corregir: mayúsculas y 5 dígitos"),
    "codigo_vacio": ("Código de equipo vacío", "completar con el código que corresponde al nombre del equipo; excluir si no hay nombre"),
    "frente_mal_escrito": ("Frente con error de digitación (Modeos de trabajo y Agilidad)", "corregir"),
    "frente_vacio": ("Frente vacío", "completar con el frente más reciente del indicador"),
    "resultado_vacio": ("Resultado vacío: no hay medición", "excluir"),
    "meta_vacia": ("Meta vacía: no hay contra qué comparar el resultado", "excluir"),
    "fila_repetida": ("La misma medición repetida en varias filas", "excluir (se deja una)"),
    "valores_en_conflicto": ("Mismo mes, equipo e indicador con valores distintos", "agrupar en una fila con el promedio"),
    "nombre_vacio": ("Nombre de equipo vacío", "completar con el nombre de su código (otras filas o catálogo)"),
    "cumplimiento_recalculado": ("Cumplimiento distinto de Resultado / Meta en indicadores donde más es mejor", "corregir: Resultado / Meta"),
    "cumplimiento_imposible": (f"Cumplimiento mayor a {CUMPLIMIENTO_MAXIMO} que no se puede recalcular", "dejar vacío"),
    "equipo_fuera_de_catalogo": ("Equipo que no está en catalogo_entornos", f"entorno = '{SIN_ENTORNO}'"),
    "indicador_fuera_de_catalogo": ("Indicador que no está en catalogo_indicadores", "agregarlo al catálogo como pendiente de documentar"),
    "frente_fuera_de_catalogo": ("Frente que no está en catalogo_indicadores", "conservarlo y reportarlo para actualizar el catálogo"),
}
