import pandas as pd
import re
import os

df_nifs = pd.read_csv('nifs.txt', sep='\t', header=0, index_col=False)

df_nifs = df_nifs.rename(columns={'Nombre empresaAlfabeto latino': 'nombre_empresa', 'Número Nacional de Identidad': 'nif'})
df_nifs['nif'] = df_nifs['nif'].replace(r'([A-z]+)(\d+)', r'\1-\2', regex=True)

pdfs = [f for f in os.listdir('pdfs_v2') if os.path.isfile(os.path.join('pdfs_v2', f))]

for pdf in pdfs:
    m = re.search(r'([A-Z])(\d+)(_.*_.*.pdf)', pdf)
    if m:
        m = re.sub(r'(\w)(\d+)(_.*_.*.pdf)', r'\1-\2\3', pdf)
        os.rename('pdfs_v2\\' + pdf, 'pdfs_v2\\' + m)
