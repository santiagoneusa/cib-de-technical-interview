"""Validaciones de calidad: el esquema de entrada antes de limpiar, y el dataset final antes de publicarlo."""

import pandas as pd

from etl import reglas

HOJAS = {
    "query": reglas.COLUMNAS_ORIGEN,
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
        faltantes = set(columnas) - set(hojas[hoja].columns)
        if faltantes:
            errores.append(f"a la hoja '{hoja}' le faltan las columnas {sorted(faltantes)}")
    return errores


def validar(kpis, datos, traza):
    """Una fila por validación con su resultado; si alguna falla, el proceso no publica la salida."""
    salientes = traza["accion"].isin(["excluida", "agrupada"]).sum()
    contadas = datos["meta_cumplida"].notna()
    chequeos = [
        ("Llave única: un valor por mes, equipo e indicador", datos.duplicated(reglas.LLAVE).sum() == 0,
         f"{datos.duplicated(reglas.LLAVE).sum()} llaves repetidas"),
        ("Códigos de equipo con formato EQU/CEX + 5 dígitos", datos["cod_equipo"].str.match(reglas.FORMATO_CODIGO).all(),
         f"{(~datos['cod_equipo'].str.match(reglas.FORMATO_CODIGO)).sum()} códigos fuera de formato"),
        ("Corte con formato AAAAMM", datos["corte"].notna().all(), f"{datos['corte'].isna().sum()} cortes inválidos"),
        ("Todo equipo tiene entorno, VP o la marca sin entorno", datos["grupo_entorno"].notna().all(),
         f"{datos['grupo_entorno'].isna().sum()} filas sin grupo"),
        ("Las filas cuadran: entrada = dataset + excluidas + agrupadas", len(kpis) == len(datos) + salientes,
         f"{len(kpis):,} = {len(datos):,} + {salientes:,}"),
        ("Toda fila apta con sentido conocido tiene meta cumplida", (contadas | ~datos["apta_para_score"] | (datos["sentido"] == "no verificado")).all(),
         f"{(datos['apta_para_score'] & ~contadas).sum()} filas aptas sin meta cumplida (solo se aceptan si son de sentido no verificado y sin Cumplimiento)"),
        ("Hay filas que cuentan en el score", contadas.any(), f"{contadas.sum():,} filas cuentan"),
    ]
    return pd.DataFrame(chequeos, columns=["validacion", "ok", "detalle"])


def registro(kpis, datos, traza):
    """El registro de calidad de 1.3 con las filas que tocó esta ejecución."""
    por_traza = traza.groupby("regla")["fila_origen"].nunique()
    por_marca = pd.Series({p: datos["marcas"].str.contains(p).sum() for p in reglas.PROBLEMAS})
    filas = por_traza.reindex(list(reglas.PROBLEMAS), fill_value=0) + por_marca.where(~por_marca.index.isin(por_traza.index), 0)
    tabla = pd.DataFrame(reglas.PROBLEMAS, index=["categoria", "problema", "tratamiento"]).T
    tabla["filas_afectadas"] = filas.astype(int)
    tabla["pct_del_archivo"] = (tabla["filas_afectadas"] / len(kpis)).round(4)
    return tabla.rename_axis("regla").reset_index()
