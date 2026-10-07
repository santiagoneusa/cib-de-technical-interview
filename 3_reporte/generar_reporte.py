import json
from pathlib import Path

import pandas as pd

CARPETA = Path(__file__).resolve().parent
SCORE = CARPETA.parent / "0_datos" / "3_score" / "KPIS_historico_score.xlsx"
PROCESADO = CARPETA.parent / "0_datos" / "2_procesados" / "KPIS_historico_procesado.xlsx"
PLANTILLA = CARPETA / "plantilla.html"
REPORTE = CARPETA / "reporte.html"

INDICADOR = ["frente", "indicador"]
SIN_ENTORNO = "Sin entorno"
MOVIMIENTO_RELEVANTE = 5
SEMESTRE_INICIAL_CONSTANCIA = "2024-S1"


def main():
    mediciones = cargar_mediciones()
    desde = mediciones["corte"].max() - pd.DateOffset(months=11)

    variacion = variacion_explicada(mediciones)
    indicadores = cumplimiento_por_indicador(mediciones)
    entornos = comparar_entornos(mediciones, desde)
    tendencia = tendencia_por_semestre(mediciones)
    disponibilidad = seguimiento_mensual(mediciones, "Disponibilidad")
    mezcla = cambio_por_mezcla(mediciones, "Excelencia operativa", 2025, 2026)

    datos = {
        "variacion": variacion,
        "indicadores": indicadores,
        "entornos": entornos,
        "tendencia": tendencia,
        "disponibilidad": disponibilidad,
        "mezcla": mezcla,
    }
    textos = redactar(mediciones, desde, variacion, indicadores, entornos, tendencia, disponibilidad, mezcla)

    escribir(datos, textos)


def cargar_mediciones():
    mediciones = pd.read_excel(SCORE, sheet_name="mediciones")
    pares = mediciones.groupby(INDICADOR + ["corte"])["meta_cumplida"]

    mediciones["esperado"] = pares.transform("mean")
    mediciones["relativo"] = mediciones["meta_cumplida"] - mediciones["esperado"]
    mediciones["anio"] = mediciones["corte"].dt.year

    return mediciones


def variacion_explicada(mediciones):
    grupos = {
        "Indicador y mes": INDICADOR + ["corte"],
        "Indicador": INDICADOR,
        "Frente": ["frente"],
        "Equipo": ["cod_equipo"],
        "Entorno": ["entorno"],
    }
    cumple = mediciones["meta_cumplida"]
    total = ((cumple - cumple.mean()) ** 2).sum()

    explicada = {}
    for nombre, grupo in grupos.items():
        promedio = mediciones.groupby(grupo)["meta_cumplida"].transform("mean")
        explicada[nombre] = 1 - ((cumple - promedio) ** 2).sum() / total

    return [{"grupo": nombre, "pct": round(valor * 100, 1)} for nombre, valor in explicada.items()]


def cumplimiento_por_indicador(mediciones):
    tabla = mediciones.groupby(INDICADOR).agg(
        tasa=("meta_cumplida", "mean"), equipos=("cod_equipo", "nunique"),
        desde=("corte", "min"), hasta=("corte", "max"),
    ).reset_index()

    tabla["tasa"] = (tabla["tasa"] * 100).round(1)
    tabla["periodo"] = tabla["desde"].dt.strftime("%Y-%m") + " a " + tabla["hasta"].dt.strftime("%Y-%m")
    repetido = tabla["indicador"].duplicated(keep=False)
    tabla["etiqueta"] = tabla["indicador"].where(~repetido, tabla["indicador"] + " (" + tabla["frente"] + ")")

    return tabla.sort_values("tasa")[["indicador", "etiqueta", "frente", "tasa", "equipos", "periodo"]].to_dict("records")


def comparar_entornos(mediciones, desde):
    recientes = mediciones[(mediciones["corte"] >= desde) & (mediciones["entorno"] != SIN_ENTORNO)]

    por_equipo = recientes.groupby(["entorno", "cod_equipo"]).agg(
        bruto=("meta_cumplida", "mean"), relativo=("relativo", "mean"), mediciones=("meta_cumplida", "size"))
    tabla = por_equipo.groupby("entorno").agg(
        equipos=("bruto", "size"), mediciones=("mediciones", "sum"),
        bruto=("bruto", "median"), relativo=("relativo", "median"),
    ).reset_index()

    tabla["puesto_bruto"] = tabla["bruto"].rank(ascending=False, method="first").astype(int)
    tabla["puesto_pares"] = tabla["relativo"].rank(ascending=False, method="first").astype(int)
    tabla["bruto"] = (tabla["bruto"] * 100).round(1)
    tabla["relativo"] = (tabla["relativo"] * 100).round(1)

    return tabla.sort_values("puesto_pares").to_dict("records")


def tendencia_por_semestre(mediciones):
    con_entorno = mediciones[mediciones["entorno"] != SIN_ENTORNO].copy()
    con_entorno["semestre"] = con_entorno["anio"].astype(str) + "-S" + (con_entorno["corte"].dt.month > 6).map({False: "1", True: "2"})

    por_equipo = con_entorno.groupby(["entorno", "semestre", "cod_equipo"])["relativo"].mean()
    por_entorno = (por_equipo.groupby(["entorno", "semestre"]).median() * 100).round(1).reset_index()

    return {
        "semestres": sorted(por_entorno["semestre"].unique()),
        "series": {entorno: dict(zip(filas["semestre"], filas["relativo"])) for entorno, filas in por_entorno.groupby("entorno")},
    }


def seguimiento_mensual(mediciones, indicador):
    del_indicador = mediciones[mediciones["indicador"] == indicador]

    tabla = del_indicador.groupby("corte").agg(
        resultado=("resultado", "median"), meta=("meta", "median"),
        tasa=("meta_cumplida", "mean"), equipos=("cod_equipo", "nunique"),
    ).reset_index()

    tabla["mes"] = tabla["corte"].dt.strftime("%Y-%m")
    tabla[["resultado", "meta", "tasa"]] = (tabla[["resultado", "meta", "tasa"]] * 100).round(2)

    return tabla[["mes", "resultado", "meta", "tasa", "equipos"]].to_dict("records")


def cambio_por_mezcla(mediciones, frente, anio_antes, anio_despues):
    del_frente = mediciones[(mediciones["frente"] == frente) & mediciones["anio"].isin([anio_antes, anio_despues])]
    anios_por_indicador = del_frente.groupby("indicador")["anio"].nunique()
    se_mantienen = anios_por_indicador.index[anios_por_indicador == 2]

    def tasa(filas, anio):
        return round(filas.loc[filas["anio"] == anio, "meta_cumplida"].mean() * 100, 1)

    mantenidos = del_frente[del_frente["indicador"].isin(se_mantienen)]
    por_indicador = del_frente.groupby(["indicador", "anio"])["meta_cumplida"].mean().mul(100).round(1).unstack()

    return {
        "frente": frente,
        "anios": [anio_antes, anio_despues],
        "todos": [tasa(del_frente, anio_antes), tasa(del_frente, anio_despues)],
        "mantenidos": [tasa(mantenidos, anio_antes), tasa(mantenidos, anio_despues)],
        "indicadores": [
            {"indicador": nombre, "antes": _numero(fila.get(anio_antes)), "despues": _numero(fila.get(anio_despues))}
            for nombre, fila in por_indicador.iterrows()
        ],
    }


def redactar(mediciones, desde, variacion, indicadores, entornos, tendencia, disponibilidad, mezcla):
    explicada = {fila["grupo"]: fila["pct"] for fila in variacion}
    movidos = [e for e in entornos if abs(e["puesto_bruto"] - e["puesto_pares"]) >= MOVIMIENTO_RELEVANTE]
    mayor_salto = max(entornos, key=lambda e: e["puesto_bruto"] - e["puesto_pares"])
    mayor_caida = max(entornos, key=lambda e: e["puesto_pares"] - e["puesto_bruto"])

    constantes = entornos_siempre_sobre_sus_pares(tendencia)
    nuevos_bajos = [fila for fila in mezcla["indicadores"] if fila["antes"] is None and fila["despues"] < mezcla["todos"][0]]
    pendientes = pd.read_excel(PROCESADO, sheet_name="indicadores")["definicion"].eq("Pendiente").sum()
    recientes = mediciones[mediciones["corte"] >= desde]

    por_anio = pd.DataFrame(disponibilidad).assign(anio=lambda d: d["mes"].str[:4])
    antes, despues = (por_anio[por_anio["anio"] == anio] for anio in ("2025", "2026"))

    return {
        "mediciones": f"{len(mediciones):,}".replace(",", "."),
        "periodo": f"{mediciones['corte'].min():%Y-%m} a {mediciones['corte'].max():%Y-%m}",
        "ventana": f"{desde:%Y-%m} a {mediciones['corte'].max():%Y-%m}",
        "pct_indicador_mes": _coma(explicada["Indicador y mes"]),
        "pct_equipo": _coma(explicada["Equipo"]),
        "pct_entorno": _coma(explicada["Entorno"]),
        "tasa_min": _coma(indicadores[0]["tasa"]),
        "indicador_min": indicadores[0]["indicador"],
        "tasa_max": _coma(indicadores[-1]["tasa"]),
        "indicador_max": indicadores[-1]["indicador"],
        "n_entornos": str(len(entornos)),
        "n_movidos": str(len(movidos)),
        "salto_entorno": mayor_salto["entorno"],
        "salto_de": str(mayor_salto["puesto_bruto"]),
        "salto_a": str(mayor_salto["puesto_pares"]),
        "caida_entorno": mayor_caida["entorno"],
        "caida_de": str(mayor_caida["puesto_bruto"]),
        "caida_a": str(mayor_caida["puesto_pares"]),
        "disp_tasa_antes": _coma(round(antes["tasa"].mean(), 1)),
        "disp_tasa_despues": _coma(round(despues["tasa"].mean(), 1)),
        "disp_res_antes": _coma(round(antes["resultado"].median(), 2)),
        "disp_res_despues": _coma(round(despues["resultado"].median(), 2)),
        "disp_meta_antes": _coma(round(antes["meta"].median(), 2)),
        "disp_meta_despues": _coma(round(despues["meta"].median(), 2)),
        "mezcla_todos_antes": _coma(mezcla["todos"][0]),
        "mezcla_todos_despues": _coma(mezcla["todos"][1]),
        "mezcla_mant_antes": _coma(mezcla["mantenidos"][0]),
        "mezcla_mant_despues": _coma(mezcla["mantenidos"][1]),
        "min_equipos_por_indicador_mes": str(mediciones.groupby(INDICADOR + ["corte"])["cod_equipo"].nunique().min()),
        "constantes": _lista(constantes) or "ningún entorno",
        "semestre_inicial": SEMESTRE_INICIAL_CONSTANCIA,
        "indicadores_nuevos": _lista([f"{fila['indicador']} ({_coma(fila['despues'])}%)" for fila in nuevos_bajos]),
        "disp_equipos": str(mediciones.loc[(mediciones["indicador"] == "Disponibilidad") & (mediciones["anio"] == 2026), "cod_equipo"].nunique()),
        "equipos_sin_entorno": str(recientes.loc[recientes["entorno"] == SIN_ENTORNO, "cod_equipo"].nunique()),
        "indicadores_pendientes": str(pendientes),
        "sentido_no_verificado": str(mediciones.loc[mediciones["sentido"] == "no verificado", "indicador"].nunique()),
    }


def entornos_siempre_sobre_sus_pares(tendencia):
    semestres = [s for s in tendencia["semestres"] if s >= SEMESTRE_INICIAL_CONSTANCIA]
    return [
        entorno for entorno, serie in tendencia["series"].items()
        if all(serie.get(semestre) is not None and serie[semestre] > 0 for semestre in semestres)
    ]


def escribir(datos, textos):
    html = PLANTILLA.read_text(encoding="utf-8")

    for clave, valor in textos.items():
        html = html.replace("{{" + clave + "}}", valor)
    html = html.replace("__DATOS__", json.dumps(datos, ensure_ascii=False, default=str))

    REPORTE.write_text(html, encoding="utf-8")
    print(f"Reporte publicado en {REPORTE.relative_to(CARPETA.parent)}")


def _coma(valor):
    return f"{valor:.1f}".replace(".", ",") if abs(valor) < 99 else f"{valor:.2f}".replace(".", ",")


def _lista(nombres):
    return ", ".join(nombres[:-1]) + " y " + nombres[-1] if len(nombres) > 1 else "".join(nombres)


def _numero(valor):
    return None if pd.isna(valor) else float(valor)


if __name__ == "__main__":
    main()
