import pandas as pd
import glob

files = glob.glob("csvs_v2/*.csv")

df = pd.DataFrame()
for f in files:
    print(f)
    csv = pd.read_csv(f, header=0, names=['nombre','bio', 'tipo_consejero', 'empresa', 'nif', 'fecha'])
    df = df.append(csv)

df = df.dropna()
df = df.drop_duplicates()

df = df[~df['nombre'].str.contains('nombre')]
df = df[~df['nombre'].str.contains('Nombre')]
df = df[~df['nombre'].str.contains('Nombres')]
df = df[~df['nombre'].str.contains('Número de')]
df = df[~df['nombre'].str.contains('asistencia')]
df = df[~df['nombre'].str.contains('votos')]
df = df[~df['nombre'].str.contains('beneficiario')]
df = df[~df['nombre'].str.contains('consejero')]
df = df[~df['nombre'].str.contains('cargo')]
df = df[~df['nombre'].str.contains('devengada')]
df = df[~df['nombre'].str.contains('%')]
df = df[df['nombre'] != '']

df['nombre'] = df['nombre'].str.replace('\d+', '')
df = df.replace(r'\n',' ', regex=True)
df = df.replace(r':','', regex=True)
df = df.replace(r'-','', regex=True)

df.to_csv('final_v3.csv', index=False, header=True)
df.to_excel('final_v3.xlsx', sheet_name='hoja1', index=False, header=True)
