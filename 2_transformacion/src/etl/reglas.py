"""Reglas de negocio de la limpieza. Se editan aquí, sin tocar la lógica de limpieza.py."""

# Columnas de la hoja query tal como llegan
COLUMNAS_ORIGEN = ["Frente", "Corte", "Codigo_EQU", "EQU", "Indicador", "Resultado", "Meta", "Cumplimiento"]

# Llave de la granularidad final: una fila por mes × equipo × indicador
LLAVE = ["corte", "cod_equipo", "indicador"]

# Códigos con un dígito de menos (EQU0024 → EQU00024); se aplica después de pasar a mayúsculas
PATRON_CODIGO = r"^([A-Z]{3})0(\d{3})$"
REEMPLAZO_CODIGO = r"\g<1>00\2"
FORMATO_CODIGO = r"^(EQU|CEX)\d{5}$"

# El frente de agilidad cambió de nombre cada año; se homologa al nombre correcto
FRENTES_HOMOLOGADOS = {
    "Talento + Agilidad": "Modelos de trabajo y Agilidad",
    "Modeos de trabajo y Agilidad": "Modelos de trabajo y Agilidad",
}

# Indicadores de encuesta: su Cumplimiento es el puntaje, no el % de la meta
INDICADORES_ENCUESTA = ["Percepción", "Adopción", "Talento + Agilidad"]

# Valores de Cumplimiento que no son mediciones
VALOR_COPIADO = 1.014683
TOLERANCIA_COPIADO = 1e-5
CUMPLIMIENTO_MAXIMO = 3  # fuera de encuestas, más de 3 veces la meta se considera imposible

# Un mes es "con pocos equipos" si reportan menos de esta fracción de la mediana de equipos por mes
FRACCION_POCOS_EQUIPOS = 0.5

# Nivel del padre en catalogo_entornos según el prefijo de Codigo_Padre; cualquier otro es "sin entorno"
NIVEL_POR_PREFIJO = {"ENX": "entorno", "VPX": "vicepresidencia"}
SIN_ENTORNO = "Sin entorno asignado"

# Cada problema del registro de calidad (1.3): categoría, descripción y tratamiento aplicado
PROBLEMAS = {
    "sin_codigo": ("Faltantes", "Filas sin código de equipo", "corregir desde el nombre del equipo; excluir si no se puede"),
    "nombre_vacio": ("Faltantes", "Nombre de equipo vacío", "corregir con otras filas del código o el catálogo"),
    "sin_resultado_meta": ("Faltantes", "Sin Resultado o Meta: no se puede saber si cumplió", "marcar (no cuenta en el score)"),
    "pocos_equipos": ("Faltantes", "Mes con pocos equipos reportando", "marcar"),
    "copia_exacta": ("Duplicados", "Filas repetidas exactamente", "excluir (se deja una)"),
    "igual_salvo_nombre": ("Duplicados", "Filas iguales salvo el nombre del equipo", "excluir (se deja la que tiene nombre)"),
    "valores_en_conflicto": ("Duplicados", "Mismo equipo, indicador y mes con valores distintos", "corregir (promedio)"),
    "codigo_mal_escrito": ("Formato", "Código de equipo mal escrito", "corregir (mayúsculas y 5 dígitos)"),
    "frente_homologado": ("Formato", "Frente con nombre anterior o mal escrito", "corregir (homologar)"),
    "equipo_fantasma": ("Catálogo", "Equipo que no está en el catálogo", "marcar como sin entorno asignado"),
    "vp_o_sin_entorno": ("Catálogo", "Equipo con vicepresidencia o sin entorno en el catálogo", "marcar (se agrupa por su VP si la tiene)"),
    "indicador_sin_definicion": ("Catálogo", "Indicador sin definición en el catálogo", "marcar"),
    "escala_encuesta": ("Valores", "Encuesta: Cumplimiento es el puntaje, no el % de la meta", "corregir (la métrica compara Resultado con Meta)"),
    "cumplimiento_imposible": ("Valores", f"Cumplimiento mayor a {CUMPLIMIENTO_MAXIMO} fuera de encuestas", "marcar (no cuenta en el score)"),
    "cumplimiento_copiado": ("Valores", f"Cumplimiento copiado ({VALOR_COPIADO})", "marcar (no cuenta en el score)"),
}

# Marcas que sacan una fila del score (las demás solo informan)
MARCAS_EXCLUYENTES = ["sin_resultado_meta", "cumplimiento_imposible", "cumplimiento_copiado"]
