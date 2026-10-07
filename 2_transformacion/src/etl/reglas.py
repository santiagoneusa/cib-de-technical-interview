COLUMNAS = {
    "Corte": "corte", "Codigo_EQU": "cod_equipo", "EQU": "equipo", "Frente": "frente",
    "Indicador": "indicador", "Resultado": "resultado", "Meta": "meta", "Cumplimiento": "cumplimiento_original",
}

LLAVE = ["corte", "cod_equipo", "indicador"]

PATRON_CODIGO = r"^([A-Z]{3})0(\d{3})$"
REEMPLAZO_CODIGO = r"\g<1>00\2"
FORMATO_CODIGO = r"^(EQU|CEX)\d{5}$"

FRENTES_MAL_ESCRITOS = {"Modeos de trabajo y Agilidad": "Modelos de trabajo y Agilidad"}

SENTIDO = {
    "Obsolescencia": "menor",
    "Pérdida esperada por fraude": "menor",
    "Gestión del Gasto": "menor",
    "Brecha Ingresos Gastos": "no verificado",
    "Impactos a clientes activos por fricciones, quejas y requerimientos": "no verificado",
    "Índice AQR's": "no verificado",
}
SENTIDO_POR_DEFECTO = "mayor"

PREFIJOS_ENTORNO = ("ENX", "VPX")
COD_SIN_ENTORNO = "SIN0000"
SIN_ENTORNO = "Sin entorno"
PENDIENTE = "Pendiente"

REGLAS = {
    "codigo_mal_escrito": ("Código de equipo en minúsculas o con un dígito de menos", "corregir: mayúsculas y 5 dígitos"),
    "codigo_vacio": ("Código de equipo vacío", "completar con el código que corresponde al nombre del equipo; excluir si no hay nombre"),
    "frente_mal_escrito": ("Frente con error de digitación (Modeos de trabajo y Agilidad)", "corregir"),
    "frente_vacio": ("Frente vacío", "completar con el frente más reciente del indicador"),
    "resultado_vacio": ("Resultado vacío: no hay medición", "excluir"),
    "meta_vacia": ("Meta vacía: no hay contra qué comparar el resultado", "excluir"),
    "cumplimiento_vacio": ("Cumplimiento vacío", "excluir"),
    "fila_repetida": ("La misma medición repetida en varias filas", "excluir (se deja una)"),
    "valores_en_conflicto": ("Mismo mes, equipo e indicador con valores distintos", "agrupar en una fila con el promedio"),
    "cumplimiento_en_otra_escala": ("Cumplimiento igual al Resultado con meta positiva: en las encuestas viene en la escala del puntaje", "cumplimiento_procesado = Resultado / Meta"),
    "equipo_fuera_de_catalogo": ("Equipo que no está en catalogo_entornos", f"agregarlo a Equipos con entorno '{SIN_ENTORNO}'"),
    "indicador_fuera_de_catalogo": ("Indicador que no está en catalogo_indicadores", "agregarlo a Indicadores como pendiente de documentar"),
    "frente_fuera_de_catalogo": ("Frente que no está en catalogo_indicadores", "agregarlo a Frentes y reportarlo para actualizar el catálogo"),
}
