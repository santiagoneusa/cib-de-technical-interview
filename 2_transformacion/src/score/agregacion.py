"""Agregación del score por frente, entorno y mes: mediana de equipos, cada equipo cuenta una vez."""

from etl.reglas import SIN_ENTORNO


def _resumir(tabla, grupo):
    resumen = tabla.groupby(grupo, as_index=False).agg(
        n_equipos=("cod_equipo", "nunique"), score_mediana=("score", "median"),
        score_min=("score", "min"), score_max=("score", "max"))
    return resumen.round({"score_mediana": 3, "score_min": 3, "score_max": 3})


def por_frente(datos):
    """Primero el score de cada equipo dentro del frente; luego la mediana entre equipos."""
    contadas = datos.dropna(subset=["meta_cumplida"])
    equipos = contadas.groupby(["corte", "frente", "cod_equipo"], as_index=False)["meta_cumplida"].mean()
    return _resumir(equipos.rename(columns={"meta_cumplida": "score"}), ["corte", "frente"])


def por_entorno(equipos):
    """Mediana de los equipos de cada entorno o VP. Los equipos sin entorno asignado se cuentan pero no se
    califican como grupo: juntarlos mezclaría áreas sin relación entre sí."""
    tabla = _resumir(equipos, ["corte", "grupo_entorno", "nivel"])
    sin_entorno = tabla["grupo_entorno"] == SIN_ENTORNO
    tabla.loc[sin_entorno, ["score_mediana", "score_min", "score_max"]] = None
    return tabla.sort_values(["corte", "nivel", "grupo_entorno"], ignore_index=True)


def por_mes(datos, equipos):
    """Evolución general: cuántos equipos e indicadores hay detrás de cada mes y su score mediano."""
    resumen = datos.groupby("corte", as_index=False).agg(
        filas=("cod_equipo", "size"), n_equipos=("cod_equipo", "nunique"), n_indicadores=("indicador", "nunique"),
        pocos_equipos=("marcas", lambda m: m.str.contains("pocos_equipos").any()))
    mediana = equipos.groupby("corte")["score"].median().round(3).rename("score_mediana")
    return resumen.merge(mediana, on="corte", how="left")
