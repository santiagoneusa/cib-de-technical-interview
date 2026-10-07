import pandas as pd

from etl import reglas

HOJAS = {
    "query": list(reglas.COLUMNAS),
    "catalogo_indicadores": ["Frente", "Indicador", "Unidad"],
    "catalogo_entornos": ["Codigo_EQU", "EQU", "Codigo_Padre", "Nombre_Padre"],
}


def validar_esquema(hojas):
    errores = []

    for hoja, columnas in HOJAS.items():
        if hoja not in hojas:
            errores.append(f"falta la hoja '{hoja}'")
            continue

        faltantes = sorted(set(columnas) - set(hojas[hoja].columns))
        if faltantes:
            errores.append(f"a la hoja '{hoja}' le faltan las columnas {faltantes}")

    return errores


def validar(kpis, tablas, traza):
    mediciones, equipos = tablas["mediciones"], tablas["equipos"]

    llaves_repetidas = mediciones.duplicated(["corte", "cod_equipo", "cod_indicador"]).sum()
    codigos_invalidos = (~equipos["cod_equipo"].str.match(reglas.FORMATO_CODIGO)).sum()
    vacios = mediciones.isna().sum().sum()
    sin_referencia = (
        (~mediciones["cod_equipo"].isin(equipos["cod_equipo"])).sum()
        + (~mediciones["cod_indicador"].isin(tablas["indicadores"]["cod_indicador"])).sum()
        + (~mediciones["cod_frente"].isin(tablas["frentes"]["cod_frente"])).sum()
        + (~equipos["cod_entorno"].isin(tablas["entornos"]["cod_entorno"])).sum()
    )
    salientes = traza["accion"].isin(["excluida", "agrupada"]).sum()

    chequeos = [
        ("Una sola medición por mes, equipo e indicador", llaves_repetidas == 0, f"{llaves_repetidas} llaves repetidas"),
        ("Códigos de equipo con formato EQU/CEX + 5 dígitos", codigos_invalidos == 0, f"{codigos_invalidos} códigos fuera de formato"),
        ("Mediciones sin valores vacíos", vacios == 0, f"{vacios} valores vacíos"),
        ("Cada código apunta a una fila de su tabla", sin_referencia == 0, f"{sin_referencia} códigos sin referencia"),
        ("Filas originales = mediciones + excluidas + agrupadas", len(kpis) == len(mediciones) + salientes,
         f"{len(kpis):,} = {len(mediciones):,} + {salientes:,}"),
    ]

    return pd.DataFrame(chequeos, columns=["validacion", "ok", "detalle"])


def registro(kpis, tablas, traza, cat_indicadores, cat_entornos):
    filas = traza.groupby("regla")["fila_origen"].nunique().to_dict()
    filas.update(_filas_fuera_de_catalogo(tablas, cat_indicadores, cat_entornos))

    tabla = pd.DataFrame(
        [(regla, problema, tratamiento) for regla, (problema, tratamiento) in reglas.REGLAS.items()],
        columns=["regla", "problema", "tratamiento"],
    )
    tabla["filas"] = tabla["regla"].map(filas).fillna(0).astype(int)
    tabla["pct_filas"] = (tabla["filas"] / len(kpis)).round(4)

    return tabla


def _filas_fuera_de_catalogo(tablas, cat_indicadores, cat_entornos):
    mediciones, indicadores, frentes = tablas["mediciones"], tablas["indicadores"], tablas["frentes"]

    indicadores_nuevos = indicadores.loc[indicadores["definicion"] == reglas.PENDIENTE, "cod_indicador"]
    frentes_catalogados = cat_indicadores["Frente"].replace(reglas.FRENTES_MAL_ESCRITOS)
    frentes_nuevos = frentes.loc[~frentes["nombre"].isin(frentes_catalogados), "cod_frente"]

    return {
        "equipo_fuera_de_catalogo": (~mediciones["cod_equipo"].isin(cat_entornos["Codigo_EQU"].str.upper())).sum(),
        "indicador_fuera_de_catalogo": mediciones["cod_indicador"].isin(indicadores_nuevos).sum(),
        "frente_fuera_de_catalogo": mediciones["cod_frente"].isin(frentes_nuevos).sum(),
    }
