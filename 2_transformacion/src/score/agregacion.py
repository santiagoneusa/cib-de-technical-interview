from etl.reglas import SIN_ENTORNO


def por_frente(mediciones):
    equipos = mediciones.groupby(["corte", "frente", "cod_equipo"], as_index=False)["meta_cumplida"].mean()

    return _resumir(equipos.rename(columns={"meta_cumplida": "score"}), ["corte", "frente"])


def por_entorno(equipos):
    tabla = _resumir(equipos, ["corte", "entorno"])
    tabla.loc[tabla["entorno"] == SIN_ENTORNO, ["score_mediana", "score_min", "score_max"]] = None  # no es un grupo comparable

    return tabla


def por_mes(equipos):
    return equipos.groupby("corte", as_index=False).agg(
        n_equipos=("cod_equipo", "nunique"),
        indicadores_por_equipo=("n_indicadores", "median"),
        score_mediana=("score", "median"),
    ).round({"score_mediana": 3})


def _resumir(equipos, grupo):
    return equipos.groupby(grupo, as_index=False).agg(
        n_equipos=("cod_equipo", "nunique"),
        score_mediana=("score", "median"),
        score_min=("score", "min"),
        score_max=("score", "max"),
    ).round({"score_mediana": 3, "score_min": 3, "score_max": 3})
