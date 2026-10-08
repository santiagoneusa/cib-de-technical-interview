import json
from pathlib import Path

import pandas as pd

CARPETA = Path(__file__).resolve().parent
DATOS = CARPETA.parent / "0_datos"
CRUDO = DATOS / "1_crudos" / "KPIS_historico.xlsx"
PROCESADO = DATOS / "2_procesados" / "KPIS_historico_procesado.xlsx"
CALIDAD = DATOS / "2_procesados" / "KPIS_historico_calidad.xlsx"
SCORE = DATOS / "3_score" / "KPIS_historico_score.xlsx"
GRAFICAS = CARPETA / "graficas.js"
PAGINAS = {
    CARPETA / "plantilla.html": CARPETA / "reporte.html",
    CARPETA / "plantilla_presentacion.html": CARPETA / "presentacion.html",
}

AUTOR = "Santiago Neusa"

INDICADOR = ["frente", "indicador"]
SIN_ENTORNO = "Sin entorno"
INDICADOR_SEGUIDO = "Disponibilidad"
FRENTE_SEGUIDO = "Excelencia operativa"
MARGEN_PARES = 5


def main():
    mediciones = cargar_mediciones()
    desde = mediciones["corte"].max() - pd.DateOffset(months=11)

    variacion = variacion_explicada(mediciones)
    entornos = clasificar_entornos(mediciones, desde)
    seguimiento = seguimiento_mensual(mediciones, INDICADOR_SEGUIDO)

    datos = {"variacion": variacion, "entornos": entornos, "seguimiento": seguimiento}
    textos = redactar(mediciones, desde, variacion, entornos, seguimiento) | resumir_base(mediciones)

    for plantilla, destino in PAGINAS.items():
        escribir(plantilla, destino, datos, textos)


def cargar_mediciones():
    mediciones = pd.read_excel(SCORE, sheet_name="mediciones")
    tasa_de_pares = mediciones.groupby(INDICADOR + ["corte"])["meta_cumplida"].transform("mean")

    mediciones["frente_a_pares"] = mediciones["meta_cumplida"] - tasa_de_pares
    mediciones["anio"] = mediciones["corte"].dt.year

    return mediciones


def variacion_explicada(mediciones):
    grupos = {
        "Qué indicador y en qué mes": INDICADOR + ["corte"],
        "Qué equipo": ["cod_equipo"],
        "Qué entorno": ["entorno"],
    }
    cumple = mediciones["meta_cumplida"]
    total = ((cumple - cumple.mean()) ** 2).sum()

    explicada = []
    for nombre, grupo in grupos.items():
        promedio = mediciones.groupby(grupo)["meta_cumplida"].transform("mean")
        explicada.append({"grupo": nombre, "pct": round((1 - ((cumple - promedio) ** 2).sum() / total) * 100, 1)})

    return explicada


def clasificar_entornos(mediciones, desde):
    recientes = mediciones[(mediciones["corte"] >= desde) & (mediciones["entorno"] != SIN_ENTORNO)]

    por_equipo = recientes.groupby(["entorno", "cod_equipo"]).agg(
        cumplimiento=("meta_cumplida", "mean"), frente_a_pares=("frente_a_pares", "mean"))
    tabla = por_equipo.groupby("entorno").agg(
        equipos=("cumplimiento", "size"), cumplimiento=("cumplimiento", "median"), frente_a_pares=("frente_a_pares", "median"),
    ).reset_index()

    tabla[["cumplimiento", "frente_a_pares"]] = (tabla[["cumplimiento", "frente_a_pares"]] * 100).round(1)
    corte_cumplimiento = tabla["cumplimiento"].median()
    alto = tabla["cumplimiento"] >= corte_cumplimiento
    sobre_pares = tabla["frente_a_pares"] >= MARGEN_PARES
    bajo_pares = tabla["frente_a_pares"] <= -MARGEN_PARES

    tabla["lectura"] = "coincide"
    tabla.loc[~alto & sobre_pares, "lectura"] = "parece bajo, supera a sus pares"
    tabla.loc[alto & bajo_pares, "lectura"] = "parece bien, está bajo sus pares"
    tabla["puesto_cumplimiento"] = tabla["cumplimiento"].rank(ascending=False, method="first").astype(int)
    tabla["puesto_justo"] = tabla["frente_a_pares"].rank(ascending=False, method="first").astype(int)

    return {"corte_cumplimiento": round(corte_cumplimiento, 1), "margen": MARGEN_PARES, "filas": tabla.to_dict("records")}


def seguimiento_mensual(mediciones, indicador):
    del_indicador = mediciones[mediciones["indicador"] == indicador]

    tabla = del_indicador.groupby("corte").agg(
        resultado=("resultado", "median"), meta=("meta", "median"), cumplieron=("meta_cumplida", "mean"),
    ).reset_index()

    tabla["mes"] = tabla["corte"].dt.strftime("%Y-%m")
    tabla[["resultado", "meta", "cumplieron"]] = (tabla[["resultado", "meta", "cumplieron"]] * 100).round(2)

    return tabla[["mes", "resultado", "meta", "cumplieron"]].to_dict("records")


def indicadores_nuevos_que_bajan(mediciones, frente, anio_antes, anio_despues):
    del_frente = mediciones[(mediciones["frente"] == frente) & mediciones["anio"].isin([anio_antes, anio_despues])]
    tasa_anterior = del_frente.loc[del_frente["anio"] == anio_antes, "meta_cumplida"].mean()

    por_indicador = del_frente.groupby(["indicador", "anio"])["meta_cumplida"].mean().unstack()
    nuevos = por_indicador[por_indicador[anio_antes].isna()]

    return nuevos.index[nuevos[anio_despues] < tasa_anterior].tolist()


def redactar(mediciones, desde, variacion, entornos, seguimiento):
    explicada = {fila["grupo"]: fila["pct"] for fila in variacion}
    filas = pd.DataFrame(entornos["filas"])
    ejemplo = filas.loc[(filas["puesto_cumplimiento"] - filas["puesto_justo"]).idxmax()]
    ocultos = filas[filas["lectura"] == "parece bien, está bajo sus pares"].sort_values("frente_a_pares")
    subestimados = filas[filas["lectura"] == "parece bajo, supera a sus pares"]

    tasa_indicador = mediciones.groupby(INDICADOR)["meta_cumplida"].mean() * 100
    seguido = pd.DataFrame(seguimiento).assign(anio=lambda tabla: tabla["mes"].str[:4])
    antes, despues = (seguido[seguido["anio"] == anio] for anio in ("2025", "2026"))
    nuevos = indicadores_nuevos_que_bajan(mediciones, FRENTE_SEGUIDO, 2025, 2026)

    return {
        "mediciones": _miles(len(mediciones)),
        "equipos": str(mediciones["cod_equipo"].nunique()),
        "periodo": f"{mediciones['corte'].min():%Y-%m} a {mediciones['corte'].max():%Y-%m}",
        "ventana": f"{desde:%Y-%m} a {mediciones['corte'].max():%Y-%m}",
        "veces": str(round(explicada["Qué indicador y en qué mes"] / explicada["Qué equipo"])),
        "pct_indicador_mes": _entero(explicada["Qué indicador y en qué mes"]),
        "pct_equipo": _entero(explicada["Qué equipo"]),
        "tasa_min": _entero(tasa_indicador.min()),
        "tasa_max": _entero(tasa_indicador.max()),
        "min_equipos": str(mediciones.groupby(INDICADOR + ["corte"])["cod_equipo"].nunique().min()),
        "n_cambian": str(len(ocultos) + len(subestimados)),
        "n_entornos": str(len(filas)),
        "margen": str(MARGEN_PARES),
        "ejemplo_entorno": ejemplo["entorno"],
        "ejemplo_puesto_antes": str(ejemplo["puesto_cumplimiento"]),
        "ejemplo_puesto_despues": str(ejemplo["puesto_justo"]),
        "ejemplo_cumplimiento": _entero(ejemplo["cumplimiento"]),
        "ejemplo_pares": _decimal(ejemplo["frente_a_pares"]),
        "ocultos": _lista(ocultos["entorno"].tolist()),
        "ocultos_verbo": "parecen" if len(ocultos) > 1 else "parece",
        "ocultos_pares": _decimal(abs(ocultos["frente_a_pares"].iloc[0])),
        "seguido": INDICADOR_SEGUIDO,
        "resultado_despues": _decimal(despues["resultado"].median()),
        "meta_antes": _decimal(antes["meta"].median()),
        "meta_despues": _decimal(despues["meta"].median()),
        "cumplieron_antes": _entero(antes["cumplieron"].mean()),
        "cumplieron_despues": _entero(despues["cumplieron"].mean()),
        "frente_seguido": FRENTE_SEGUIDO,
        "indicadores_nuevos": _lista(nuevos),
    }


def resumir_base(mediciones):
    filas_originales = len(pd.read_excel(CRUDO, sheet_name="query", usecols=["Corte"]))
    indicadores = pd.read_excel(PROCESADO, sheet_name="indicadores")
    pendientes = indicadores.loc[indicadores["definicion"] == "Pendiente", "nombre"]
    fuera_de_catalogo = mediciones["indicador"].isin(pendientes).mean()
    acciones = pd.read_excel(CALIDAD, sheet_name="trazabilidad")["accion"].value_counts()

    return {
        "autor": AUTOR,
        "filas_originales": _miles(filas_originales),
        "filas_salientes": _miles(filas_originales - len(mediciones)),
        "pct_fuera_catalogo": _entero(fuera_de_catalogo * 100),
        "n_entornos": str(mediciones.loc[mediciones["entorno"] != SIN_ENTORNO, "entorno"].nunique()),
        "filas_excluidas": _miles(acciones.get("excluida", 0)),
        "peso_mediciones": str(len(mediciones)),
        "peso_excluidas": str(acciones.get("excluida", 0)),
        "peso_agrupadas": str(acciones.get("agrupada", 0)),
        "filas_agrupadas": _miles(acciones.get("agrupada", 0)),
    }


def escribir(plantilla, destino, datos, textos):
    html = plantilla.read_text(encoding="utf-8")

    for clave, valor in textos.items():
        html = html.replace("{{" + clave + "}}", valor)
    html = html.replace("__GRAFICAS__", GRAFICAS.read_text(encoding="utf-8"))
    html = html.replace("__DATOS__", json.dumps(datos, ensure_ascii=False, default=str))

    destino.write_text(html, encoding="utf-8")
    print(f"Publicado {destino.relative_to(CARPETA.parent)}")


def _miles(valor):
    return f"{valor:,}".replace(",", ".")


def _entero(valor):
    return f"{valor:.0f}"


def _decimal(valor):
    return f"{valor:.1f}".replace(".", ",")


def _lista(nombres):
    return ", ".join(nombres[:-1]) + " y " + nombres[-1] if len(nombres) > 1 else "".join(nombres)


if __name__ == "__main__":
    main()
