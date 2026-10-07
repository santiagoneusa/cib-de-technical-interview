import pandas as pd

from etl import reglas

TABLAS = ["frentes", "indicadores", "entornos", "equipos", "mediciones"]


def normalizar(datos, cat_indicadores, cat_entornos):
    frentes = construir_frentes(datos, cat_indicadores)
    indicadores = construir_indicadores(datos, cat_indicadores, frentes)

    return {
        "mediciones": construir_mediciones(datos, frentes, indicadores),
        "equipos": construir_equipos(datos, cat_entornos),
        "entornos": construir_entornos(cat_entornos),
        "indicadores": indicadores,
        "frentes": frentes,
    }


def construir_frentes(datos, cat_indicadores):
    del_catalogo = cat_indicadores["Frente"].replace(reglas.FRENTES_MAL_ESCRITOS)
    nombres = pd.concat([del_catalogo, datos["frente"]]).drop_duplicates()

    return _con_codigo(nombres, "cod_frente", "FRE", digitos=2)


def construir_indicadores(datos, cat_indicadores, frentes):
    definicion = next(columna for columna in cat_indicadores.columns if columna.startswith("Defin"))
    del_catalogo = cat_indicadores.rename(columns={"Frente": "frente", "Indicador": "nombre", definicion: "definicion", "Unidad": "unidad"})
    del_catalogo["frente"] = del_catalogo["frente"].replace(reglas.FRENTES_MAL_ESCRITOS)

    medidos = datos[["frente", "indicador"]].drop_duplicates().rename(columns={"indicador": "nombre"})
    nuevos = medidos[~_clave(medidos).isin(_clave(del_catalogo))]
    pendientes = nuevos.assign(definicion=reglas.PENDIENTE, unidad=reglas.PENDIENTE)

    indicadores = pd.concat([del_catalogo[["frente", "nombre", "definicion", "unidad"]], pendientes], ignore_index=True)
    sentido = {simplificar(nombre): valor for nombre, valor in reglas.SENTIDO.items()}
    indicadores["sentido"] = indicadores["nombre"].map(simplificar).map(sentido).fillna(reglas.SENTIDO_POR_DEFECTO)
    indicadores["cod_indicador"] = _codigos("IND", len(indicadores), digitos=3)
    indicadores["cod_frente"] = indicadores["frente"].map(frentes.set_index("nombre")["cod_frente"])

    return indicadores[["cod_indicador", "nombre", "cod_frente", "definicion", "unidad", "sentido"]]


def construir_entornos(cat_entornos):
    padres = cat_entornos[cat_entornos["Codigo_Padre"].str.startswith(reglas.PREFIJOS_ENTORNO, na=False)]
    entornos = (padres[["Codigo_Padre", "Nombre_Padre"]].drop_duplicates()
                .rename(columns={"Codigo_Padre": "cod_entorno", "Nombre_Padre": "nombre"})
                .sort_values("cod_entorno"))
    sin_entorno = pd.DataFrame({"cod_entorno": [reglas.COD_SIN_ENTORNO], "nombre": [reglas.SIN_ENTORNO]})

    return pd.concat([entornos, sin_entorno], ignore_index=True)


def construir_equipos(datos, cat_entornos):
    catalogo = cat_entornos.set_index(cat_entornos["Codigo_EQU"].str.upper())
    nombre_en_datos = datos.dropna(subset=["equipo"]).groupby("cod_equipo")["equipo"].agg(lambda nombres: nombres.mode()[0])

    equipos = pd.DataFrame({"cod_equipo": catalogo.index.union(datos["cod_equipo"].unique())})
    equipos["nombre"] = equipos["cod_equipo"].map(catalogo["EQU"]).fillna(equipos["cod_equipo"].map(nombre_en_datos))

    padre = equipos["cod_equipo"].map(catalogo["Codigo_Padre"])
    equipos["cod_entorno"] = padre.where(padre.str.startswith(reglas.PREFIJOS_ENTORNO, na=False), reglas.COD_SIN_ENTORNO)

    return equipos


def construir_mediciones(datos, frentes, indicadores):
    con_frente = indicadores.merge(frentes.rename(columns={"nombre": "frente"}), on="cod_frente")
    cod_indicador = con_frente.set_index(_clave(con_frente))["cod_indicador"]

    mediciones = datos.assign(cod_indicador=_clave(datos.rename(columns={"indicador": "nombre"})).map(cod_indicador))
    columnas = ["corte", "cod_equipo", "cod_indicador", "resultado", "meta", "cumplimiento_original", "cumplimiento_procesado"]

    return mediciones[columnas]


def simplificar(texto):
    return texto.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")


def _clave(tabla):
    return tabla["frente"] + " | " + tabla["nombre"].map(simplificar)


def _codigos(prefijo, cantidad, digitos):
    return [f"{prefijo}{numero:0{digitos}d}" for numero in range(1, cantidad + 1)]


def _con_codigo(nombres, columna, prefijo, digitos):
    return pd.DataFrame({columna: _codigos(prefijo, len(nombres), digitos), "nombre": list(nombres)})
