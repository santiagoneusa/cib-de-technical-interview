"""Proceso completo, desde la raíz del repositorio:

    uv run python 2_transformacion/src/main.py

Por cada Excel de 0_datos/1_crudos publica dos archivos:
  - 0_datos/2_procesados/<archivo>_procesado.xlsx: datos limpios, catálogo de indicadores actualizado,
    registro de calidad, trazabilidad y validaciones (etl/).
  - 0_datos/3_score/<archivo>_score.xlsx: meta cumplida y score por equipo, frente, entorno y mes (score/).
Si el esquema o una validación falla no publica nada, lo deja en el log y termina con código 1.
"""

import logging
import sys
from pathlib import Path

import pandas as pd

from etl import calidad, catalogos, limpieza
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
    """ETL y score de un archivo. Devuelve True si publicó sus dos salidas."""
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

    resultado = score(procesado["datos"], procesado["indicadores"])
    escribir_excel(PROCESADOS / f"{archivo.stem}_procesado.xlsx", procesado)
    escribir_excel(SCORE / f"{archivo.stem}_score.xlsx", resultado)
    log.info("%s: %s filas originales → %s filas procesadas; %s acciones en la trazabilidad",
             archivo.name, f"{len(hojas['query']):,}", f"{len(procesado['datos']):,}", f"{len(procesado['trazabilidad']):,}")
    return True


def etl(hojas):
    """Limpia la hoja query, la cruza con los catálogos y la valida. Devuelve las hojas del archivo procesado."""
    kpis, cat_indicadores, cat_entornos = hojas["query"], hojas["catalogo_indicadores"], hojas["catalogo_entornos"]
    datos, traza = limpieza.limpiar(kpis, cat_entornos)
    datos = catalogos.asignar_entorno(datos, cat_entornos)
    indicadores = catalogos.actualizar_catalogo_indicadores(datos, cat_indicadores)
    return {
        "datos": datos,
        "indicadores": indicadores,
        "registro_calidad": calidad.registro(kpis, datos, traza, cat_entornos, indicadores),
        "trazabilidad": traza,
        "validaciones": calidad.validar(kpis, datos, traza),
    }


def score(datos, indicadores):
    """Calcula la meta cumplida y la agrega. Devuelve las hojas del archivo de score."""
    mediciones = features.calcular_meta_cumplida(datos, indicadores)
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
    """Una hoja por tabla, con encabezado fijo, filtros y ancho de columna según el contenido."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(destino, engine="openpyxl", date_format="YYYY-MM", datetime_format="YYYY-MM") as excel:
        for nombre, tabla in hojas.items():
            tabla.to_excel(excel, sheet_name=nombre, index=False, freeze_panes=(1, 0))
            hoja = excel.sheets[nombre]
            hoja.auto_filter.ref = hoja.dimensions
            for columna in hoja.columns:
                ancho = max(len(str(celda.value or "")) for celda in columna[:200])
                hoja.column_dimensions[columna[0].column_letter].width = min(max(ancho, 10) + 2, 60)


def configurar_log():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(DATOS / "ejecucion.log", encoding="utf-8"), logging.StreamHandler()])


if __name__ == "__main__":
    main()
