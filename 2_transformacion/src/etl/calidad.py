"""Calidad: valida el esquema de entrada antes de limpiar, valida el dataset antes de publicarlo y resume
qué hizo cada regla en el registro de calidad."""

import pandas as pd

from etl import reglas

HOJAS = {
    "query": list(reglas.COLUMNAS),
    "catalogo_indicadores": ["Frente", "Indicador", "Unidad"],
    "catalogo_entornos": ["Codigo_EQU", "EQU", "Codigo_Padre", "Nombre_Padre"],
}


def validar_esquema(hojas):
    """Lista de errores si al archivo le falta una hoja o una columna; vacía si el esquema está completo."""
    errores = []
    for hoja, columnas in HOJAS.items():
        if hoja not in hojas:
            errores.append(f"falta la hoja '{hoja}'")
            continue
        faltantes = sorted(set(columnas) - set(hojas[hoja].columns))
        if faltantes:
            errores.append(f"a la hoja '{hoja}' le faltan las columnas {faltantes}")
    return errores


def validar(kpis, datos, traza):
    """Una fila por validación con su resultado. Si alguna falla, el proceso no publica la salida."""
    llaves_repetidas = datos.duplicated(reglas.LLAVE).sum()
    codigos_invalidos = (~datos["cod_equipo"].str.match(reglas.FORMATO_CODIGO)).sum()
    vacios = datos[["corte", "cod_equipo", "frente", "indicador", "resultado", "meta"]].isna().sum().sum()
    salientes = traza["accion"].isin(["excluida", "agrupada"]).sum()
    chequeos = [
        ("Una sola fila por mes, equipo e indicador", llaves_repetidas == 0, f"{llaves_repetidas} llaves repetidas"),
        ("Códigos de equipo con formato EQU/CEX + 5 dígitos", codigos_invalidos == 0, f"{codigos_invalidos} códigos fuera de formato"),
        ("Corte, equipo, frente, indicador, resultado y meta sin vacíos", vacios == 0, f"{vacios} valores vacíos"),
        ("Filas de entrada = filas del dataset + excluidas + agrupadas", len(kpis) == len(datos) + salientes,
         f"{len(kpis):,} = {len(datos):,} + {salientes:,}"),
    ]
    return pd.DataFrame(chequeos, columns=["validacion", "ok", "detalle"])


def registro(kpis, datos, traza, cat_entornos, catalogo_indicadores):
    """Cada regla con el problema que resuelve, su tratamiento y cuántas filas del archivo original tocó."""
    filas = traza.groupby("regla")["fila_origen"].nunique().to_dict()
    filas.update(_filas_fuera_de_catalogo(datos, cat_entornos, catalogo_indicadores))
    tabla = pd.DataFrame([(regla, problema, tratamiento) for regla, (problema, tratamiento) in reglas.REGLAS.items()],
                         columns=["regla", "problema", "tratamiento"])
    tabla["filas"] = tabla["regla"].map(filas).fillna(0).astype(int)
    tabla["pct_filas"] = (tabla["filas"] / len(kpis)).round(4)
    return tabla


def _filas_fuera_de_catalogo(datos, cat_entornos, catalogo_indicadores):
    """Filas del dataset cuyo equipo, indicador o frente no aparece en el catálogo oficial."""
    indicadores_nuevos = catalogo_indicadores.loc[catalogo_indicadores["en_catalogo"] == "no", "indicador"]
    frentes_catalogo = catalogo_indicadores.loc[catalogo_indicadores["en_catalogo"] == "sí", "frente"]
    return {
        "equipo_fuera_de_catalogo": (~datos["cod_equipo"].isin(cat_entornos["Codigo_EQU"].str.upper())).sum(),
        "indicador_fuera_de_catalogo": datos["indicador"].isin(indicadores_nuevos).sum(),
        "frente_fuera_de_catalogo": (~datos["frente"].isin(frentes_catalogo)).sum(),
    }
