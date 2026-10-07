"""Aplica los tratamientos del registro de calidad (actividad 1.3) y deja la traza de cada fila tocada."""

import pandas as pd

from etl import reglas


def simplificar(texto):
    """Minúsculas y sin tildes, para cruzar nombres que solo difieren en la escritura."""
    return texto.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")


def limpiar(kpis, cat_indicadores, cat_entornos):
    """Devuelve (datos, traza): una fila por mes × equipo × indicador, y una fila por cada fila de origen
    excluida, corregida o agrupada. Las marcas no cambian datos: se listan en la columna `marcas`."""
    datos = kpis.copy()
    datos.insert(0, "fila_origen", datos.index + 2)  # número de fila en la hoja query de Excel
    traza = []

    def registrar(filas, accion, regla, detalle=""):
        if isinstance(detalle, pd.Series):
            detalle = detalle.loc[filas.index].values
        traza.append(pd.DataFrame({"fila_origen": filas["fila_origen"].values, "accion": accion,
                                   "regla": regla, "detalle": detalle}))

    # Excluir: copias exactas (se deja la primera) y filas sin código de equipo
    primera = datos.groupby(reglas.COLUMNAS_ORIGEN, dropna=False)["fila_origen"].transform("first")
    copia = datos["fila_origen"] != primera
    registrar(datos[copia], "excluida", "copia_exacta", "copia de la fila " + primera.astype(str))
    datos = datos[~copia]

    # Corregir: código vacío desde el nombre del equipo (cada nombre corresponde a un solo código); excluir si no se puede
    catalogo = cat_entornos.assign(cod_equipo=cat_entornos["Codigo_EQU"].str.upper()).set_index("cod_equipo")
    conocidos = pd.concat([datos[["EQU", "Codigo_EQU"]].dropna(), cat_entornos[["EQU", "Codigo_EQU"]]])
    unicos = conocidos.assign(Codigo_EQU=conocidos["Codigo_EQU"].str.upper()).drop_duplicates()
    codigo_por_nombre = unicos[~unicos["EQU"].duplicated(keep=False)].set_index("EQU")["Codigo_EQU"]
    sin_codigo = datos["Codigo_EQU"].isna()
    recuperado = datos["EQU"].map(codigo_por_nombre)
    registrar(datos[sin_codigo & recuperado.notna()], "corregida", "sin_codigo", "código tomado del nombre: " + recuperado)
    registrar(datos[sin_codigo & recuperado.isna()], "excluida", "sin_codigo", "sin nombre que identifique al equipo")
    datos["Codigo_EQU"] = datos["Codigo_EQU"].fillna(recuperado)
    datos = datos[datos["Codigo_EQU"].notna()]

    datos = datos.rename(columns={"Frente": "frente", "Codigo_EQU": "codigo_origen", "EQU": "nombre_equipo",
                                  "Indicador": "indicador", "Resultado": "resultado", "Meta": "meta",
                                  "Cumplimiento": "cumplimiento_origen"})
    datos["corte"] = pd.to_datetime(datos["Corte"], format="%Y%m", errors="coerce")

    # Corregir: código de equipo en mayúsculas y con 5 dígitos
    datos["cod_equipo"] = datos["codigo_origen"].str.strip().str.upper().str.replace(
        reglas.PATRON_CODIGO, reglas.REEMPLAZO_CODIGO, regex=True)
    mal_escrito = datos["cod_equipo"] != datos["codigo_origen"]
    registrar(datos[mal_escrito], "corregida", "codigo_mal_escrito", datos["codigo_origen"] + " → " + datos["cod_equipo"])

    # Excluir: la misma medición repetida, una con nombre de equipo y otra sin él (se deja la que tiene nombre)
    medicion = ["frente", "corte", "cod_equipo", "indicador", "resultado", "meta", "cumplimiento_origen"]
    datos = datos.sort_values(["nombre_equipo", "fila_origen"], na_position="last")
    repetida = datos.duplicated(medicion)
    registrar(datos[repetida], "excluida", "igual_salvo_nombre")
    datos = datos[~repetida].sort_values("fila_origen")

    # Corregir: frente homologado
    homologar = datos["frente"].isin(reglas.FRENTES_HOMOLOGADOS)
    registrar(datos[homologar], "corregida", "frente_homologado", datos["frente"] + " → " + datos["frente"].map(reglas.FRENTES_HOMOLOGADOS))
    datos["frente"] = datos["frente"].replace(reglas.FRENTES_HOMOLOGADOS)

    # Corregir: varias filas para el mismo mes, equipo e indicador se promedian en la primera
    grupo = datos.groupby(reglas.LLAVE)["fila_origen"]
    n_filas, representante = grupo.transform("size"), grupo.transform("min")
    conflicto = n_filas > 1
    absorbida = conflicto & (datos["fila_origen"] != representante)
    registrar(datos[absorbida], "agrupada", "valores_en_conflicto", "promediada en la fila " + representante.astype(str))
    registrar(datos[conflicto & ~absorbida], "corregida", "valores_en_conflicto", "promedio de " + n_filas.astype(str) + " filas")
    datos = datos.groupby(reglas.LLAVE, as_index=False).agg(
        fila_origen=("fila_origen", "min"), frente=("frente", "first"), nombre_equipo=("nombre_equipo", "first"),
        resultado=("resultado", "mean"), meta=("meta", "mean"), cumplimiento_origen=("cumplimiento_origen", "mean"))

    # Corregir: nombre de equipo vacío, desde otras filas del mismo código o desde el catálogo
    nombre_frecuente = datos.dropna(subset=["nombre_equipo"]).groupby("cod_equipo")["nombre_equipo"].agg(lambda s: s.mode()[0])
    vacio = datos["nombre_equipo"].isna()
    de_filas = datos["cod_equipo"].map(nombre_frecuente)
    de_catalogo = datos["cod_equipo"].map(catalogo["EQU"])
    origen_nombre = de_filas.notna().map({True: "tomado de otras filas del código", False: "tomado del catálogo"})
    corregible = vacio & (de_filas.notna() | de_catalogo.notna())
    registrar(datos[corregible], "corregida", "nombre_vacio", origen_nombre)
    datos["nombre_equipo"] = datos["nombre_equipo"].fillna(de_filas).fillna(de_catalogo)

    # Entorno: del catálogo; los equipos que no están quedan "sin entorno asignado"
    datos["tipo_equipo"] = datos["cod_equipo"].str[:3]
    datos["cod_padre"] = datos["cod_equipo"].map(catalogo["Codigo_Padre"])
    datos["nivel"] = datos["cod_padre"].str[:3].map(reglas.NIVEL_POR_PREFIJO).fillna("sin entorno")
    agrupable = datos["nivel"] != "sin entorno"
    datos["grupo_entorno"] = datos["cod_equipo"].map(catalogo["Nombre_Padre"]).where(agrupable, reglas.SIN_ENTORNO)
    ultimo_anio = datos["corte"].dt.year.max()
    anio_equipo = datos.groupby("cod_equipo")["corte"].transform("max").dt.year
    datos["estado"] = (anio_equipo == ultimo_anio).map({True: "vigente", False: "histórico"})

    # Marcar: problemas que no cambian el dato pero hay que tener presentes al analizar
    equipos_mes = datos.groupby("corte")["cod_equipo"].nunique()
    pocos = equipos_mes.index[equipos_mes < equipos_mes.median() * reglas.FRACCION_POCOS_EQUIPOS]
    encuesta = datos["indicador"].isin(reglas.INDICADORES_ENCUESTA)
    documentados = set(cat_indicadores["Indicador"].map(simplificar))
    marcas = {
        "sin_resultado_meta": datos["resultado"].isna() | datos["meta"].isna(),
        "pocos_equipos": datos["corte"].isin(pocos),
        "equipo_fantasma": datos["cod_padre"].isna(),
        "vp_o_sin_entorno": datos["cod_padre"].notna() & (datos["nivel"] != "entorno"),
        "indicador_sin_definicion": ~datos["indicador"].map(simplificar).isin(documentados),
        "escala_encuesta": encuesta,
        "cumplimiento_imposible": ~encuesta & (datos["cumplimiento_origen"].abs() > reglas.CUMPLIMIENTO_MAXIMO),
        "cumplimiento_copiado": (datos["cumplimiento_origen"] - reglas.VALOR_COPIADO).abs() < reglas.TOLERANCIA_COPIADO,
    }
    marcas = pd.DataFrame(marcas)
    datos["marcas"] = marcas.dot(marcas.columns + ", ").str.removesuffix(", ")
    datos["apta_para_score"] = ~marcas[reglas.MARCAS_EXCLUYENTES].any(axis=1)

    columnas = ["corte", "cod_equipo", "nombre_equipo", "tipo_equipo", "estado", "grupo_entorno", "nivel", "cod_padre",
                "frente", "indicador", "resultado", "meta", "cumplimiento_origen", "marcas", "apta_para_score", "fila_origen"]
    traza = pd.concat(traza, ignore_index=True).sort_values(["fila_origen", "accion"], ignore_index=True)
    return datos[columnas].sort_values(reglas.LLAVE, ignore_index=True), traza
