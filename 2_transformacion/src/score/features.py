"""Métrica comparable entre indicadores (meta cumplida) y su resumen por indicador y por equipo-mes."""

import numpy as np
import pandas as pd

from score import reglas


def calcular_meta_cumplida(datos, catalogo_indicadores):
    """Una fila por medición con meta_cumplida: 1 si el resultado alcanza la meta según el sentido del indicador
    (≥ si más es mejor, ≤ si menos es mejor), 0 si no. En sentido no verificado se usa Cumplimiento ≥ 1."""
    sentido = datos["indicador"].map(catalogo_indicadores.set_index("indicador")["sentido"])
    cumple = np.select(
        [sentido == "mayor", sentido == "menor"],
        [datos["resultado"] >= datos["meta"], datos["resultado"] <= datos["meta"]],
        default=datos["cumplimiento"] >= 1,
    ).astype(float)
    sin_dato = (sentido == "no verificado") & datos["cumplimiento"].isna()
    mediciones = datos[["corte", "cod_equipo", "equipo", "entorno", "frente", "indicador", "resultado", "meta"]].copy()
    mediciones.insert(6, "sentido", sentido)
    mediciones["meta_cumplida"] = pd.Series(cumple, index=datos.index).mask(sin_dato)
    return mediciones


def por_indicador(mediciones):
    """Cobertura, tasa de cumplimiento y dispersión entre equipos de cada indicador. La cobertura es contexto, no un peso."""
    tasa_por_equipo = mediciones.groupby(["indicador", "cod_equipo"])["meta_cumplida"].mean()
    tabla = mediciones.sort_values("corte").groupby("indicador").agg(
        frente=("frente", "last"), sentido=("sentido", "first"),
        n_equipos=("cod_equipo", "nunique"), n_meses=("corte", "nunique"),
        primer_corte=("corte", "min"), ultimo_corte=("corte", "max"),
        tasa_cumplimiento=("meta_cumplida", "mean"),
    )
    tabla["dispersion_entre_equipos"] = tasa_por_equipo.groupby("indicador").std()
    return tabla.round({"tasa_cumplimiento": 3, "dispersion_entre_equipos": 3}).reset_index().sort_values(["frente", "indicador"], ignore_index=True)


def por_equipo_mes(mediciones):
    """Score de cada equipo en cada mes: proporción de sus indicadores que cumplieron la meta, todos con el mismo peso."""
    equipos = mediciones.dropna(subset=["meta_cumplida"]).groupby(["corte", "cod_equipo"], as_index=False).agg(
        equipo=("equipo", "first"), entorno=("entorno", "first"),
        n_indicadores=("indicador", "nunique"), metas_cumplidas=("meta_cumplida", "sum"), score=("meta_cumplida", "mean"),
    )
    equipos["metas_cumplidas"] = equipos["metas_cumplidas"].astype(int)
    tendencia = equipos.groupby("cod_equipo")["score"].transform(
        lambda score: score.shift(1).rolling(reglas.MESES_TENDENCIA, min_periods=1).mean())
    equipos["variacion_3m"] = equipos["score"] - tendencia
    return equipos.round({"score": 3, "variacion_3m": 3})
