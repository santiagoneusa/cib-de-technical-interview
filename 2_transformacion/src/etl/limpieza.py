"""Limpieza de la hoja query. Cada función aplica una regla de reglas.py y devuelve (datos, traza):
los datos ya tratados y una fila por cada fila de origen que la regla excluyó, corrigió, completó o agrupó."""

import pandas as pd

from etl import reglas


def limpiar(kpis, cat_entornos):
    """Aplica las reglas en orden. Devuelve el dataset limpio y la traza completa."""
    pasos = [
        normalizar_codigo_equipo,
        lambda datos: completar_codigo_equipo(datos, cat_entornos),
        corregir_frente_mal_escrito,
        completar_frente_vacio,
        excluir_resultado_vacio,
        excluir_meta_vacia,
        excluir_filas_repetidas,
        agrupar_valores_en_conflicto,
        lambda datos: completar_nombre_equipo(datos, cat_entornos),
        recalcular_cumplimiento,
        vaciar_cumplimiento_imposible,
    ]
    datos, trazas = preparar(kpis), []
    for paso in pasos:
        datos, traza = paso(datos)
        trazas.append(traza)
    traza = pd.concat(trazas, ignore_index=True).sort_values("fila_origen", kind="stable", ignore_index=True)
    return datos.sort_values(reglas.LLAVE, ignore_index=True), traza


def preparar(kpis):
    """Renombra las columnas, convierte el corte a fecha y guarda el número de fila de Excel de cada medición."""
    datos = kpis.rename(columns=reglas.COLUMNAS)[list(reglas.COLUMNAS.values())]
    datos["corte"] = pd.to_datetime(datos["corte"], format="%Y%m", errors="coerce")
    datos["fila_origen"] = kpis.index + 2  # +1 por el encabezado y +1 porque Excel cuenta desde 1
    return datos


def normalizar_codigo_equipo(datos):
    """Código en mayúsculas y con 5 dígitos: Equ00074 → EQU00074, EQU0024 → EQU00024."""
    normalizado = datos["cod_equipo"].str.strip().str.upper().str.replace(reglas.PATRON_CODIGO, reglas.REEMPLAZO_CODIGO, regex=True)
    cambia = datos["cod_equipo"].notna() & (normalizado != datos["cod_equipo"])
    traza = _traza(datos[cambia], "codigo_mal_escrito", "corregida",
                   "Codigo_EQU: " + datos["cod_equipo"] + " → " + normalizado)
    return datos.assign(cod_equipo=normalizado), traza


def completar_codigo_equipo(datos, cat_entornos):
    """Código vacío: se toma del nombre del equipo, solo si ese nombre corresponde a un único código
    en la base y en el catálogo. Si no hay nombre que lo identifique, la fila se excluye."""
    codigo_por_nombre = _codigo_por_nombre(datos, cat_entornos)
    vacio = datos["cod_equipo"].isna()
    encontrado = datos["equipo"].map(codigo_por_nombre)
    completar, excluir = vacio & encontrado.notna(), vacio & encontrado.isna()
    traza = pd.concat([
        _traza(datos[completar], "codigo_vacio", "completada", "Codigo_EQU: vacío → " + encontrado + " (por el nombre " + datos["equipo"] + ")"),
        _traza(datos[excluir], "codigo_vacio", "excluida", "sin nombre que identifique al equipo"),
    ])
    return datos.assign(cod_equipo=datos["cod_equipo"].fillna(encontrado))[~excluir], traza


def corregir_frente_mal_escrito(datos):
    """Frentes con error de digitación, según reglas.FRENTES_MAL_ESCRITOS."""
    mal_escrito = datos["frente"].isin(reglas.FRENTES_MAL_ESCRITOS)
    corregido = datos["frente"].replace(reglas.FRENTES_MAL_ESCRITOS)
    traza = _traza(datos[mal_escrito], "frente_mal_escrito", "corregida", "Frente: " + datos["frente"] + " → " + corregido)
    return datos.assign(frente=corregido), traza


def completar_frente_vacio(datos):
    """Frente vacío: se toma el frente más reciente con el que se reportó el mismo indicador."""
    frente_reciente = datos.dropna(subset=["frente"]).sort_values("corte").groupby("indicador")["frente"].last()
    encontrado = datos["indicador"].map(frente_reciente)
    completar = datos["frente"].isna() & encontrado.notna()
    traza = _traza(datos[completar], "frente_vacio", "completada", "Frente: vacío → " + encontrado)
    return datos.assign(frente=datos["frente"].fillna(encontrado)), traza


def excluir_resultado_vacio(datos):
    """Sin Resultado no hay medición."""
    return _excluir(datos, datos["resultado"].isna(), "resultado_vacio", "Resultado: vacío")


def excluir_meta_vacia(datos):
    """Sin Meta no se puede saber si el resultado cumplió."""
    return _excluir(datos, datos["meta"].isna(), "meta_vacia", "Meta: vacío")


def excluir_filas_repetidas(datos):
    """La misma medición (mes, equipo, frente, indicador, resultado, meta y cumplimiento) en varias filas:
    se deja una, preferiblemente la que trae el nombre del equipo."""
    medicion = ["corte", "cod_equipo", "frente", "indicador", "resultado", "meta", "cumplimiento"]
    ordenados = datos.sort_values(["equipo", "fila_origen"], na_position="last")
    conservada = ordenados.groupby(medicion, dropna=False)["fila_origen"].transform("first")
    repetida = ordenados["fila_origen"] != conservada
    datos_sin_repetidas, traza = _excluir(ordenados, repetida, "fila_repetida", "repite la fila " + conservada.astype(str))
    return datos_sin_repetidas.sort_values("fila_origen"), traza


def agrupar_valores_en_conflicto(datos):
    """Varias filas para el mismo mes, equipo e indicador con valores distintos (sobre todo respuestas
    individuales de encuesta): se agrupan en la primera fila con el promedio de Resultado, Meta y Cumplimiento."""
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
        meta=("meta", "mean"), cumplimiento=("cumplimiento", "mean"), fila_origen=("fila_origen", "min"))
    return agrupados[datos.columns], traza


def completar_nombre_equipo(datos, cat_entornos):
    """Nombre vacío: se toma el nombre más frecuente del mismo código en otras filas; si no hay, el del catálogo."""
    nombre_en_filas = datos.dropna(subset=["equipo"]).groupby("cod_equipo")["equipo"].agg(lambda nombres: nombres.mode()[0])
    nombre_en_catalogo = cat_entornos.set_index(cat_entornos["Codigo_EQU"].str.upper())["EQU"]
    de_filas = datos["cod_equipo"].map(nombre_en_filas)
    encontrado = de_filas.fillna(datos["cod_equipo"].map(nombre_en_catalogo))
    fuente = de_filas.notna().map({True: " (otras filas del código)", False: " (catálogo)"})
    completar = datos["equipo"].isna() & encontrado.notna()
    traza = _traza(datos[completar], "nombre_vacio", "completada", "EQU: vacío → " + encontrado + fuente)
    return datos.assign(equipo=datos["equipo"].fillna(encontrado)), traza


def recalcular_cumplimiento(datos):
    """En indicadores donde más es mejor y la meta es positiva, Cumplimiento = Resultado / Meta. Corrige las
    encuestas (traían el puntaje), los valores copiados y los vacíos. En los demás se conserva el de origen."""
    calculable = (_sentido(datos) == "mayor") & (datos["meta"] > 0)
    nuevo = (datos["resultado"] / datos["meta"]).where(calculable, datos["cumplimiento"])
    distinto = datos["cumplimiento"].isna() | ((nuevo - datos["cumplimiento"]).abs() > reglas.TOLERANCIA_CUMPLIMIENTO)
    cambia = calculable & distinto
    traza = _traza(datos[cambia], "cumplimiento_recalculado", "corregida",
                   "Cumplimiento: " + _texto(datos["cumplimiento"]) + " → " + _texto(nuevo))
    return datos.assign(cumplimiento=nuevo), traza


def vaciar_cumplimiento_imposible(datos):
    """Cumplimiento mayor a reglas.CUMPLIMIENTO_MAXIMO que no se pudo recalcular: no es una medición creíble."""
    imposible = datos["cumplimiento"].abs() > reglas.CUMPLIMIENTO_MAXIMO
    traza = _traza(datos[imposible], "cumplimiento_imposible", "corregida", "Cumplimiento: " + _texto(datos["cumplimiento"]) + " → vacío")
    return datos.assign(cumplimiento=datos["cumplimiento"].mask(imposible)), traza


def _codigo_por_nombre(datos, cat_entornos):
    """Nombre → código, solo para los nombres que corresponden a un único código en la base y en el catálogo."""
    pares = pd.concat([
        datos[["equipo", "cod_equipo"]].dropna(),
        cat_entornos.rename(columns={"EQU": "equipo", "Codigo_EQU": "cod_equipo"})[["equipo", "cod_equipo"]],
    ]).drop_duplicates()
    unicos = pares[~pares["equipo"].duplicated(keep=False)]
    return unicos.set_index("equipo")["cod_equipo"]


def _sentido(datos):
    return datos["indicador"].map(reglas.SENTIDO).fillna(reglas.SENTIDO_POR_DEFECTO)


def _excluir(datos, excluir, regla, detalle):
    return datos[~excluir], _traza(datos[excluir], regla, "excluida", detalle)


def _traza(filas, regla, accion, detalle):
    """Una fila de traza por cada fila tocada: número de fila en Excel, regla, acción y qué cambió."""
    if isinstance(detalle, pd.Series):
        detalle = detalle.loc[filas.index].values
    return pd.DataFrame({"fila_origen": filas["fila_origen"].values, "regla": regla, "accion": accion, "detalle": detalle})


def _texto(valores):
    return valores.map(lambda valor: "vacío" if pd.isna(valor) else f"{valor:.3f}")
