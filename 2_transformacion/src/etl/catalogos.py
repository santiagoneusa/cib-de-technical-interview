"""Cruce con los catálogos: entorno de cada equipo y catálogo de indicadores actualizado con lo que se mide."""

import pandas as pd

from etl import reglas


def asignar_entorno(datos, cat_entornos):
    """Agrega cod_entorno y entorno desde catalogo_entornos. Las vicepresidencias cuentan como entorno; los equipos
    que no están en el catálogo o cuyo padre no es entorno ni vicepresidencia quedan en reglas.SIN_ENTORNO."""
    catalogo = cat_entornos.set_index(cat_entornos["Codigo_EQU"].str.upper())
    cod_padre = datos["cod_equipo"].map(catalogo["Codigo_Padre"])
    es_entorno = cod_padre.str.startswith(reglas.PREFIJOS_ENTORNO, na=False)
    entorno = datos["cod_equipo"].map(catalogo["Nombre_Padre"]).where(es_entorno, reglas.SIN_ENTORNO)
    posicion = datos.columns.get_loc("equipo") + 1
    datos = datos.copy()
    datos.insert(posicion, "cod_entorno", cod_padre.where(es_entorno))
    datos.insert(posicion + 1, "entorno", entorno)
    return datos


def actualizar_catalogo_indicadores(datos, cat_indicadores):
    """Una fila por indicador medido o catalogado: frente, definición, unidad y sentido. Los indicadores que se
    miden pero no están en el catálogo se agregan como pendientes de documentar."""
    catalogo = _catalogo_por_clave(cat_indicadores)
    medidos = datos.sort_values("corte").groupby("indicador")["frente"].last().reset_index()
    medidos["clave"] = medidos["indicador"].map(simplificar)
    medidos = medidos.merge(catalogo[["clave", "definicion", "unidad"]], on="clave", how="left")
    medidos["en_catalogo"] = medidos["definicion"].notna().map({True: "sí", False: "no"})
    medidos[["definicion", "unidad"]] = medidos[["definicion", "unidad"]].fillna(reglas.PENDIENTE)
    medidos["con_mediciones"] = "sí"

    sin_medir = catalogo[~catalogo["clave"].isin(medidos["clave"])].assign(en_catalogo="sí", con_mediciones="no")
    actualizado = pd.concat([medidos, sin_medir], ignore_index=True)
    actualizado["sentido"] = actualizado["indicador"].map(reglas.SENTIDO).fillna(reglas.SENTIDO_POR_DEFECTO)
    columnas = ["frente", "indicador", "definicion", "unidad", "sentido", "en_catalogo", "con_mediciones"]
    return actualizado[columnas].sort_values(["frente", "indicador"], ignore_index=True)


def simplificar(texto):
    """Minúsculas y sin tildes, para cruzar nombres que solo difieren en la escritura."""
    return texto.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")


def _catalogo_por_clave(cat_indicadores):
    definicion = next(columna for columna in cat_indicadores.columns if columna.startswith("Defin"))
    catalogo = cat_indicadores.rename(columns={"Frente": "frente", "Indicador": "indicador", definicion: "definicion", "Unidad": "unidad"})
    catalogo["frente"] = catalogo["frente"].replace(reglas.FRENTES_MAL_ESCRITOS)
    return catalogo.assign(clave=catalogo["indicador"].map(simplificar))
