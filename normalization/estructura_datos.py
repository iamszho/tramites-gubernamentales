import pandas as pd
from pathlib import Path

# 1. Obtiene la carpeta donde está este script (normalization)
directorio_actual = Path(__file__).parent
print (directorio_actual)
# 2. Sube un nivel (.parent) y entra a 'data/Banco_datos_tramitoteca.csv'
ruta_csv = directorio_actual.parent / "data" / "Banco_datos_tramitoteca.csv"

df = pd.read_csv(ruta_csv)  # o read_excel()

print(df.shape)           # cuántas filas y columnas
print(df.columns.tolist()) # nombres de columnas
print(df.head(3))          # primeras 3 filas
print(df.isnull().sum())   # nulos por columna
df.columns = df.columns.str.strip()
print(df.columns.tolist())  # verificar que quedaron limpios
print(df['Costo del tramite'].dropna().value_counts().head(20))
