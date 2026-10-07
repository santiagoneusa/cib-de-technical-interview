"""Métrica comparable entre indicadores (meta cumplida) y features por indicador y por equipo-mes."""

import numpy as np
import pandas as pd

from etl.limpieza import simplificar
from score import reglas


def calcular_meta_cumplida(datos):
    """1 si el resultado alcanza la meta según el sentido del indicador, 0 si no; vacío si la fila no cuenta."""
    datos = datos.copy()
    datos["sentido"] = datos["indicador"].map(reglas.SENTIDO).fillna(reglas.SENTIDO_POR_DEFECTO)
    cumple = np.select(
        [datos["sentido"] == "mayor", datos["sentido"] == "menor"],
        [datos["resultado"] >= datos["meta"], datos["resultado"] <= datos["meta"]],
        default=datos["cumplimiento_origen"] >= 1,
    ).astype(float)
    calculable = datos["apta_para_score"] & ((datos["sentido"] != "no verificado") | datos["cumplimiento_origen"].notna())
    datos["meta_cumplida"] = pd.Series(cumple, index=datos.index).where(calculable)
    return datos


def por_indicador(datos, cat_indicadores):
    """Cobertura, cumplimiento y dispersión de cada indicador. La cobertura es contexto, no un peso."""
    unidad = cat_indicadores.assign(clave=cat_indicadores["Indicador"].map(simplificar)).set_index("clave")["Unidad"]
    contadas = datos.dropna(subset=["meta_cumplida"])
    tasa_equipo = contadas.groupby(["indicador", "cod_equipo"])["meta_cumplida"].mean()
    tabla = datos.sort_values("corte").groupby("indicador").agg(
        frente=("frente", "last"), sentido=("sentido", "first"),
        n_equipos=("cod_equipo", "nunique"), n_meses=("corte", "nunique"),
        primer_corte=("corte", "min"), ultimo_corte=("corte", "max"), filas=("corte", "size"),
        resultado_mediana=("resultado", "median"), resultado_min=("resultado", "min"), resultado_max=("resultado", "max"),
        meta_mediana=("meta", "median"),
    )
    tabla.insert(2, "unidad", tabla.index.map(simplificar).map(unidad).fillna("sin definición"))
    tabla["filas_en_score"] = contadas.groupby("indicador").size().reindex(tabla.index, fill_value=0)
    tabla["tasa_cumplimiento"] = contadas.groupby("indicador")["meta_cumplida"].mean().round(3)
    tabla["dispersion_entre_equipos"] = tasa_equipo.groupby("indicador").std().round(3)
    return tabla.reset_index().sort_values(["frente", "indicador"], ignore_index=True)


def por_equipo_mes(datos):
    """Score de cada equipo en cada mes: % de sus indicadores que cumplieron la meta, todos con el mismo peso."""
    contadas = datos.dropna(subset=["meta_cumplida"])
    equipos = contadas.groupby(["corte", "cod_equipo"], as_index=False).agg(
        nombre_equipo=("nombre_equipo", "first"), estado=("estado", "first"),
        grupo_entorno=("grupo_entorno", "first"), nivel=("nivel", "first"),
        n_indicadores=("indicador", "nunique"), metas_cumplidas=("meta_cumplida", "sum"),
        score=("meta_cumplida", "mean"),
    )
    equipos["metas_cumplidas"] = equipos["metas_cumplidas"].astype(int)
    tendencia = equipos.groupby("cod_equipo")["score"].transform(
        lambda s: s.shift(1).rolling(reglas.MESES_TENDENCIA, min_periods=1).mean())
    equipos["variacion_3m"] = (equipos["score"] - tendencia).round(3)
    equipos["score"] = equipos["score"].round(3)
    return equipos
