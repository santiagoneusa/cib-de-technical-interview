"""Proceso completo: lee cada Excel de 0_datos/entrada, lo limpia, calcula el score y publica el resultado en
0_datos/salida. Se ejecuta desde la raíz del repositorio con:

    uv run python 2_transformacion/src/main.py

Si una validación falla no publica nada, lo deja en el log y termina con código 1 (lo detecta cualquier orquestador).
"""

import logging
import sys
from pathlib import Path

import pandas as pd

from etl import calidad, limpieza
from score import agregacion, features

RAIZ = Path(__file__).resolve().parents[2]
ENTRADA = RAIZ / "0_datos" / "entrada"
SALIDA = RAIZ / "0_datos" / "salida"

log = logging.getLogger("kpis")


def procesar(archivo):
    """Procesa un archivo; devuelve True si se publicó la salida."""
    hojas = pd.read_excel(archivo, sheet_name=None, dtype={"Corte": str, "Codigo_EQU": str, "EQU": str})
    errores = calidad.validar_esquema(hojas)
    if errores:
        log.error("%s: esquema inválido: %s", archivo.name, "; ".join(errores))
        return False
    kpis, cat_indicadores, cat_entornos = hojas["query"], hojas["catalogo_indicadores"], hojas["catalogo_entornos"]

    datos, traza = limpieza.limpiar(kpis, cat_indicadores, cat_entornos)
    datos = features.calcular_meta_cumplida(datos)
    validaciones = calidad.validar(kpis, datos, traza)
    if not validaciones["ok"].all():
        for fila in validaciones[~validaciones["ok"]].itertuples():
            log.error("%s: falló '%s' (%s)", archivo.name, fila.validacion, fila.detalle)
        return False

    equipos = features.por_equipo_mes(datos)
    salida = {
        "registro_calidad": calidad.registro(kpis, datos, traza),
        "trazabilidad": traza,
        "validaciones": validaciones,
        "dataset_analitico": datos,
        "indicadores": features.por_indicador(datos, cat_indicadores),
        "equipos_mes": equipos,
        "frentes_mes": agregacion.por_frente(datos),
        "entornos_mes": agregacion.por_entorno(equipos),
        "evolucion_mes": agregacion.por_mes(datos, equipos),
    }
    destino = SALIDA / f"{archivo.stem}_analitico.xlsx"
    with pd.ExcelWriter(destino, engine="openpyxl", date_format="YYYY-MM", datetime_format="YYYY-MM") as excel:
        for nombre, tabla in salida.items():
            tabla.to_excel(excel, sheet_name=nombre, index=False, freeze_panes=(1, 0))
            hoja = excel.sheets[nombre]
            hoja.auto_filter.ref = hoja.dimensions
            for columna in hoja.columns:
                ancho = max(len(str(celda.value or "")) for celda in columna[:200])
                hoja.column_dimensions[columna[0].column_letter].width = min(max(ancho, 10) + 2, 60)

    acciones = traza["accion"].value_counts()
    log.info("%s: %s filas de entrada → %s en el dataset (%s excluidas, %s agrupadas, %s corregidas); %s filas en el score → %s",
             archivo.name, f"{len(kpis):,}", f"{len(datos):,}", acciones.get("excluida", 0), acciones.get("agrupada", 0),
             acciones.get("corregida", 0), f"{datos['meta_cumplida'].notna().sum():,}", destino.relative_to(RAIZ))
    return True


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(SALIDA / "ejecucion.log", encoding="utf-8"), logging.StreamHandler()])
    archivos = sorted(a for a in ENTRADA.glob("*.xlsx") if not a.name.startswith("~$"))
    if not archivos:
        log.error("no hay archivos .xlsx en %s", ENTRADA.relative_to(RAIZ))
        sys.exit(1)
    resultados = [procesar(archivo) for archivo in archivos]
    sys.exit(0 if all(resultados) else 1)


if __name__ == "__main__":
    main()
