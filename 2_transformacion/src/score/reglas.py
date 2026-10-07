"""Reglas del score. Se editan aquí, sin tocar la lógica de features.py ni agregacion.py."""

# Sentido de cada indicador: si cumplir la meta es quedar por encima ("mayor") o por debajo ("menor").
# Se dedujo comparando Cumplimiento ≥ 1 con Resultado vs Meta en el archivo original:
#   - "menor": el Cumplimiento de origen coincide con Resultado ≤ Meta en todas las filas.
#   - "no verificado": ningún sentido explica el Cumplimiento de origen; se usa Cumplimiento ≥ 1
#     tal como llega, y debe confirmarse con el dueño del indicador.
# Cualquier indicador que no esté aquí es "mayor".
SENTIDO = {
    "Obsolescencia": "menor",
    "Pérdida esperada por fraude": "menor",
    "Gestión del Gasto": "menor",
    "Brecha Ingresos Gastos": "no verificado",
    "Impactos a clientes activos por fricciones, quejas y requerimientos": "no verificado",
    "Índice AQR's": "no verificado",
}
SENTIDO_POR_DEFECTO = "mayor"

# Meses hacia atrás para comparar el score de un equipo con su propia tendencia
MESES_TENDENCIA = 3
