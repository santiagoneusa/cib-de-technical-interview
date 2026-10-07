import logging
import sys
from pathlib import Path

import pandas as pd

from etl import calidad, limpieza, modelo
from score import agregacion, features

DATOS = Path(__file__).resolve().parents[2] / "0_datos"
CRUDOS = DATOS / "1_crudos"
PROCESADOS = DATOS / "2_procesados"
SCORE = DATOS / "3_score"

log = logging.getLogger("kpis")


def main():
    configurar_log()

    archivos = sorted(archivo for archivo in CRUDOS.glob("*.xlsx") if not archivo.name.startswith("~$"))
    if not archivos:
        log.error("no hay archivos .xlsx en %s", CRUDOS)
        sys.exit(1)

    publicados = [procesar(archivo) for archivo in archivos]

    sys.exit(0 if all(publicados) else 1)


def procesar(archivo):
    hojas = pd.read_excel(archivo, sheet_name=None, dtype={"Corte": str, "Codigo_EQU": str, "EQU": str})

    errores = calidad.validar_esquema(hojas)
    if errores:
        log.error("%s: esquema inválido: %s", archivo.name, "; ".join(errores))
        return False

    procesado = etl(hojas)

    fallidas = procesado["validaciones"][~procesado["validaciones"]["ok"]]
    if not fallidas.empty:
        for validacion in fallidas.itertuples():
            log.error("%s: falló '%s' (%s)", archivo.name, validacion.validacion, validacion.detalle)
        return False

    tablas = {nombre: procesado[nombre] for nombre in modelo.TABLAS}
    calidad_del_proceso = {nombre: procesado[nombre] for nombre in ["registro_calidad", "trazabilidad", "validaciones"]}

    escribir_excel(PROCESADOS / f"{archivo.stem}_procesado.xlsx", tablas)
    escribir_excel(PROCESADOS / f"{archivo.stem}_calidad.xlsx", calidad_del_proceso)
    escribir_excel(SCORE / f"{archivo.stem}_score.xlsx", score(tablas))

    log.info("%s: %s filas originales → %s mediciones; %s acciones en la trazabilidad", archivo.name,
             f"{len(hojas['query']):,}", f"{len(procesado['mediciones']):,}", f"{len(procesado['trazabilidad']):,}")

    return True


def etl(hojas):
    kpis, cat_indicadores, cat_entornos = hojas["query"], hojas["catalogo_indicadores"], hojas["catalogo_entornos"]

    datos, traza = limpieza.limpiar(kpis, cat_entornos)
    tablas = modelo.normalizar(datos, cat_indicadores, cat_entornos)

    return {
        **tablas,
        "registro_calidad": calidad.registro(kpis, tablas, traza, cat_indicadores, cat_entornos),
        "trazabilidad": traza,
        "validaciones": calidad.validar(kpis, tablas, traza),
    }


def score(tablas):
    mediciones = features.calcular_meta_cumplida(features.unir_tablas(tablas))
    equipos = features.por_equipo_mes(mediciones)

    return {
        "mediciones": mediciones,
        "indicadores": features.por_indicador(mediciones),
        "equipos_mes": equipos,
        "frentes_mes": agregacion.por_frente(mediciones),
        "entornos_mes": agregacion.por_entorno(equipos),
        "evolucion_mes": agregacion.por_mes(equipos),
    }


def escribir_excel(destino, hojas):
    destino.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(destino, engine="openpyxl", date_format="YYYY-MM", datetime_format="YYYY-MM") as excel:
        for nombre, tabla in hojas.items():
            tabla.to_excel(excel, sheet_name=nombre, index=False, freeze_panes=(1, 0))
            ajustar_hoja(excel.sheets[nombre])


def ajustar_hoja(hoja):
    hoja.auto_filter.ref = hoja.dimensions

    for columna in hoja.columns:
        ancho = max(len(str(celda.value or "")) for celda in columna[:200])
        hoja.column_dimensions[columna[0].column_letter].width = min(max(ancho, 10) + 2, 60)


def configurar_log():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(DATOS / "ejecucion.log", encoding="utf-8"), logging.StreamHandler()],
    )


if __name__ == "__main__":
    main()
