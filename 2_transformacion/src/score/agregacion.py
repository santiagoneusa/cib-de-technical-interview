"""Agregación del score por frente, entorno y mes: mediana de los equipos, cada equipo cuenta una vez."""

from etl.reglas import SIN_ENTORNO


def por_frente(mediciones):
    """Primero el score de cada equipo dentro del frente; luego la mediana entre equipos."""
    equipos = mediciones.dropna(subset=["meta_cumplida"]).groupby(["corte", "frente", "cod_equipo"], as_index=False)["meta_cumplida"].mean()
    return _resumir(equipos.rename(columns={"meta_cumplida": "score"}), ["corte", "frente"])


def por_entorno(equipos):
    """Mediana de los equipos de cada entorno o vicepresidencia. Los equipos sin entorno se cuentan pero no se
    califican como grupo: juntarlos mezclaría áreas sin relación entre sí."""
    tabla = _resumir(equipos, ["corte", "entorno"])
    tabla.loc[tabla["entorno"] == SIN_ENTORNO, ["score_mediana", "score_min", "score_max"]] = None
    return tabla


def por_mes(equipos):
    """Evolución general: cuántos equipos e indicadores hay detrás de cada mes y su score mediano."""
    return equipos.groupby("corte", as_index=False).agg(
        n_equipos=("cod_equipo", "nunique"), indicadores_por_equipo=("n_indicadores", "median"),
        score_mediana=("score", "median"),
    ).round({"score_mediana": 3})


def _resumir(equipos, grupo):
    return equipos.groupby(grupo, as_index=False).agg(
        n_equipos=("cod_equipo", "nunique"), score_mediana=("score", "median"),
        score_min=("score", "min"), score_max=("score", "max"),
    ).round({"score_mediana": 3, "score_min": 3, "score_max": 3})
