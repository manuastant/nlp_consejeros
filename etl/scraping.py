import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

# Leer NIFs e iterar sobre ellos para descargar los PDF
df_nifs = pd.read_csv('nifs.txt', sep='\t', header=0)

df_nifs = df_nifs.rename(columns={'Nombre empresaAlfabeto latino': 'nombre_empresa', 'Número Nacional de Identidad': 'nif'})
df_nifs['nif'] = df_nifs['nif'].replace(r'([A-z]+)(\d+)', r'\1-\2', regex=True)

for nif in df_nifs['nif']:
    for n_pag in range(2):
        URL = 'https://www.cnmv.es/portal/Consultas/EE/InformacionGobCorp.aspx?nif=' + str(nif) + '&pageIAGC=' + str(n_pag)
        print(URL)

        response = requests.get(URL)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        if not soup.find_all('tbody'):
            continue

        tabla = str(soup.find_all('tbody')[0])

        pdf_codes = re.findall(r'Nº  registro oficial">(\d*).*', tabla)
        dates = re.findall(r'Ejercicio">(\d+).*', tabla)

        dates = [re.sub(r'\/', '-', s) for s in dates]

        pdf_tags = soup.find_all('a', href=True)
        i = 0
        for url in pdf_tags:
            filename = re.search(r'verDoc\.axd', url['href'])
            if filename:
                url = re.sub('\.\.\/\.\.\/',  'www.cnmv.es/portal/', url['href']) 
                response = requests.get('https://' + url)
                fichero = re.sub('\.axd', '\.pdf', filename.string)
                with open('pdfs_v2\\' + nif + '_' + pdf_codes[i] + '_' + dates[i] + '.pdf', 'wb') as f:
                    f.write(response.content)
                i += 1
