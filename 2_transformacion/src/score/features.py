import numpy as np

from score import reglas


def unir_tablas(tablas):
    equipos = tablas["equipos"].rename(columns={"nombre": "equipo"})
    entornos = tablas["entornos"].rename(columns={"nombre": "entorno"})
    frentes = tablas["frentes"].rename(columns={"nombre": "frente"})
    indicadores = tablas["indicadores"][["cod_indicador", "nombre", "sentido"]].rename(columns={"nombre": "indicador"})

    mediciones = (tablas["mediciones"]
                  .merge(equipos, on="cod_equipo")
                  .merge(entornos, on="cod_entorno")
                  .merge(frentes, on="cod_frente")
                  .merge(indicadores, on="cod_indicador"))
    columnas = ["corte", "cod_equipo", "equipo", "entorno", "frente", "indicador", "sentido", "resultado", "meta", "cumplimiento"]

    return mediciones[columnas]


def calcular_meta_cumplida(mediciones):
    cumple = np.select(
        [mediciones["sentido"] == "mayor", mediciones["sentido"] == "menor"],
        [mediciones["resultado"] >= mediciones["meta"], mediciones["resultado"] <= mediciones["meta"]],
        default=mediciones["cumplimiento"] >= 1,
    )

    return mediciones.assign(meta_cumplida=cumple.astype(int))


def por_indicador(mediciones):
    tasa_por_equipo = mediciones.groupby(["indicador", "cod_equipo"])["meta_cumplida"].mean()

    tabla = mediciones.sort_values("corte").groupby("indicador").agg(
        frente=("frente", "last"), sentido=("sentido", "first"),
        n_equipos=("cod_equipo", "nunique"), n_meses=("corte", "nunique"),
        primer_corte=("corte", "min"), ultimo_corte=("corte", "max"),
        tasa_cumplimiento=("meta_cumplida", "mean"),
    )
    tabla["dispersion_entre_equipos"] = tasa_por_equipo.groupby("indicador").std()

    return tabla.round({"tasa_cumplimiento": 3, "dispersion_entre_equipos": 3}).reset_index()


def por_equipo_mes(mediciones):
    equipos = mediciones.groupby(["corte", "cod_equipo"], as_index=False).agg(
        equipo=("equipo", "first"), entorno=("entorno", "first"),
        n_indicadores=("indicador", "nunique"), metas_cumplidas=("meta_cumplida", "sum"), score=("meta_cumplida", "mean"),
    )

    tendencia = equipos.groupby("cod_equipo")["score"].transform(
        lambda score: score.shift(1).rolling(reglas.MESES_TENDENCIA, min_periods=1).mean())
    equipos["variacion_3m"] = equipos["score"] - tendencia

    return equipos.round({"score": 3, "variacion_3m": 3})
