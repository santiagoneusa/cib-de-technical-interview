import pandas as pd

from etl import reglas


def limpiar(kpis, cat_entornos):
    pasos = [
        normalizar_codigo_equipo,
        lambda datos: imputar_codigo_equipo(datos, cat_entornos),
        corregir_frente_mal_escrito,
        imputar_frente,
        excluir_resultado_vacio,
        excluir_meta_vacia,
        excluir_cumplimiento_vacio,
        excluir_filas_repetidas,
        agrupar_valores_en_conflicto,
    ]

    datos, trazas = preparar(kpis), []
    for paso in pasos:
        datos, traza = paso(datos)
        trazas.append(traza)

    traza = pd.concat(trazas, ignore_index=True).sort_values("fila_origen", kind="stable", ignore_index=True)

    return datos.sort_values(reglas.LLAVE, ignore_index=True), traza


def preparar(kpis):
    datos = kpis.rename(columns=reglas.COLUMNAS)[list(reglas.COLUMNAS.values())]
    datos["corte"] = pd.to_datetime(datos["corte"], format="%Y%m", errors="coerce")
    datos["fila_origen"] = kpis.index + 2  # fila de Excel: +1 por el encabezado y +1 porque cuenta desde 1

    return datos


def normalizar_codigo_equipo(datos):
    normalizado = (datos["cod_equipo"].str.strip().str.upper()
                   .str.replace(reglas.PATRON_CODIGO, reglas.REEMPLAZO_CODIGO, regex=True))
    cambia = datos["cod_equipo"].notna() & (normalizado != datos["cod_equipo"])

    traza = _traza(datos[cambia], "codigo_mal_escrito", "corregida", "Codigo_EQU: " + datos["cod_equipo"] + " → " + normalizado)

    return datos.assign(cod_equipo=normalizado), traza


def imputar_codigo_equipo(datos, cat_entornos):
    codigo = datos["equipo"].map(_codigo_por_nombre(datos, cat_entornos))
    vacio = datos["cod_equipo"].isna()
    imputable, sin_nombre = vacio & codigo.notna(), vacio & codigo.isna()

    traza = pd.concat([
        _traza(datos[imputable], "codigo_vacio", "completada", "Codigo_EQU: vacío → " + codigo + " (por el nombre " + datos["equipo"] + ")"),
        _traza(datos[sin_nombre], "codigo_vacio", "excluida", "sin nombre que identifique al equipo"),
    ])

    return datos.assign(cod_equipo=datos["cod_equipo"].fillna(codigo))[~sin_nombre], traza


def corregir_frente_mal_escrito(datos):
    mal_escrito = datos["frente"].isin(reglas.FRENTES_MAL_ESCRITOS)
    corregido = datos["frente"].replace(reglas.FRENTES_MAL_ESCRITOS)

    traza = _traza(datos[mal_escrito], "frente_mal_escrito", "corregida", "Frente: " + datos["frente"] + " → " + corregido)

    return datos.assign(frente=corregido), traza


def imputar_frente(datos):
    frente_reciente = datos.dropna(subset=["frente"]).sort_values("corte").groupby("indicador")["frente"].last()
    frente = datos["indicador"].map(frente_reciente)
    imputable = datos["frente"].isna() & frente.notna()

    traza = _traza(datos[imputable], "frente_vacio", "completada", "Frente: vacío → " + frente)

    return datos.assign(frente=datos["frente"].fillna(frente)), traza


def excluir_resultado_vacio(datos):
    return _excluir(datos, datos["resultado"].isna(), "resultado_vacio", "Resultado: vacío")


def excluir_meta_vacia(datos):
    return _excluir(datos, datos["meta"].isna(), "meta_vacia", "Meta: vacío")


def excluir_cumplimiento_vacio(datos):
    return _excluir(datos, datos["cumplimiento"].isna(), "cumplimiento_vacio", "Cumplimiento: vacío")


def excluir_filas_repetidas(datos):
    medicion = ["corte", "cod_equipo", "frente", "indicador", "resultado", "meta", "cumplimiento"]
    conservada = datos.groupby(medicion)["fila_origen"].transform("min")
    repetida = datos["fila_origen"] != conservada

    return _excluir(datos, repetida, "fila_repetida", "repite la fila " + conservada.astype(str))


def agrupar_valores_en_conflicto(datos):
    grupo = datos.groupby(reglas.LLAVE)["fila_origen"]
    n_filas, primera = grupo.transform("size"), grupo.transform("min")
    en_conflicto = n_filas > 1
    absorbida = en_conflicto & (datos["fila_origen"] != primera)

    traza = pd.concat([
        _traza(datos[en_conflicto & ~absorbida], "valores_en_conflicto", "corregida",
               "Resultado, Meta y Cumplimiento: promedio de " + n_filas.astype(str) + " filas"),
        _traza(datos[absorbida], "valores_en_conflicto", "agrupada", "promediada en la fila " + primera.astype(str)),
    ])

    agrupados = datos.groupby(reglas.LLAVE, as_index=False).agg(
        equipo=("equipo", "first"), frente=("frente", "first"), resultado=("resultado", "mean"),
        meta=("meta", "mean"), cumplimiento=("cumplimiento", "mean"), fila_origen=("fila_origen", "min"),
    )

    return agrupados[datos.columns], traza


def _codigo_por_nombre(datos, cat_entornos):
    catalogo = cat_entornos.rename(columns={"EQU": "equipo", "Codigo_EQU": "cod_equipo"})
    pares = pd.concat([datos[["equipo", "cod_equipo"]].dropna(), catalogo[["equipo", "cod_equipo"]]]).drop_duplicates()
    nombres_unicos = pares[~pares["equipo"].duplicated(keep=False)]

    return nombres_unicos.set_index("equipo")["cod_equipo"]


def _excluir(datos, excluir, regla, detalle):
    return datos[~excluir], _traza(datos[excluir], regla, "excluida", detalle)


def _traza(filas, regla, accion, detalle):
    if isinstance(detalle, pd.Series):
        detalle = detalle.loc[filas.index].values

    return pd.DataFrame({"fila_origen": filas["fila_origen"].values, "regla": regla, "accion": accion, "detalle": detalle})
