import pandas as pd

from etl import reglas

TABLAS = ["frentes", "indicadores", "entornos", "equipos", "mediciones"]


def normalizar(datos, cat_indicadores, cat_entornos):
    frentes = construir_frentes(datos, cat_indicadores)
    indicadores = construir_indicadores(datos, cat_indicadores)

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


def construir_indicadores(datos, cat_indicadores):
    definicion = next(columna for columna in cat_indicadores.columns if columna.startswith("Defin"))
    del_catalogo = cat_indicadores.rename(columns={"Indicador": "nombre", definicion: "definicion", "Unidad": "unidad"})

    medidos = datos["indicador"].drop_duplicates()
    nuevos = medidos[~medidos.map(simplificar).isin(del_catalogo["nombre"].map(simplificar))]
    pendientes = pd.DataFrame({"nombre": nuevos, "definicion": reglas.PENDIENTE, "unidad": reglas.PENDIENTE})

    indicadores = pd.concat([del_catalogo[["nombre", "definicion", "unidad"]], pendientes], ignore_index=True)
    sentido = {simplificar(nombre): valor for nombre, valor in reglas.SENTIDO.items()}
    indicadores["sentido"] = indicadores["nombre"].map(simplificar).map(sentido).fillna(reglas.SENTIDO_POR_DEFECTO)

    codigos = _con_codigo(indicadores["nombre"], "cod_indicador", "IND", digitos=3)

    return codigos.merge(indicadores, on="nombre")


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
    cod_frente = frentes.set_index("nombre")["cod_frente"]
    cod_indicador = indicadores.set_index(indicadores["nombre"].map(simplificar))["cod_indicador"]

    mediciones = datos.assign(
        cod_frente=datos["frente"].map(cod_frente),
        cod_indicador=datos["indicador"].map(simplificar).map(cod_indicador),
    )
    columnas = [
        "corte", "cod_equipo", "cod_indicador", "cod_frente",
        "resultado", "meta", "cumplimiento_original", "cumplimiento_procesado",
    ]

    return mediciones[columnas]


def simplificar(texto):
    return texto.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")


def _con_codigo(nombres, columna, prefijo, digitos):
    codigos = [f"{prefijo}{numero:0{digitos}d}" for numero in range(1, len(nombres) + 1)]

    return pd.DataFrame({columna: codigos, "nombre": list(nombres)})
