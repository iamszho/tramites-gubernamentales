from pathlib import Path

import pandas as pd

from .config import RUTA_CSV

COLUMNAS_REQUERIDAS = [
    "Nombre del tramite",
    "Dependencia",
    "Descripcion",
    "Tipo",
    "Unidad Administrativa",
    "Homoclave",
    "Link",
    "Requisitos",
    "Como realizar el tramite",
    "Costo del tramite",
    "Vigencia",
    "Tiempo de respuesta",
    "id_unico",
]


def cargar_tramites(ruta_csv: Path = RUTA_CSV) -> pd.DataFrame:
    df = pd.read_csv(ruta_csv)
    df.columns = df.columns.str.strip()

    faltantes = [columna for columna in COLUMNAS_REQUERIDAS if columna not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas esperadas en el CSV: {faltantes}")

    nulos = df[COLUMNAS_REQUERIDAS].isnull().sum()
    columnas_con_nulos = nulos[nulos > 0]
    if not columnas_con_nulos.empty:
        raise ValueError(
            "El CSV debería llegar limpio de Fase 1 (sin nulos), "
            f"pero se encontraron nulos en: {columnas_con_nulos.to_dict()}"
        )

    return df


if __name__ == "__main__":
    df = cargar_tramites()
    print(df.head())