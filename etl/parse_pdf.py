import camelot
import pandas as pd
import re
import os
from tika import parser
from bs4 import BeautifulSoup

# Leer y procesar conjunto de datos con NIFs de empresas
df_nifs = pd.read_csv('nifs.txt', sep='\t', header=0, index_col=False)

df_nifs = df_nifs.rename(columns={'Nombre empresaAlfabeto latino': 'nombre_empresa', 'Número Nacional de Identidad': 'nif'})
df_nifs['nif'] = df_nifs['nif'].replace(r'([A-z]+)(\d+)', r'\1-\2', regex=True)

# Obtener PDFs fuente
pdfs = [f for f in os.listdir('pdfs') if os.path.isfile(os.path.join('pdfs', f))]

df_final = pd.DataFrame(columns=['nombre','tipo_consejero', 'empresa', 'nif', 'fecha', 'bio'])

# Recorrer cada PDF incluyendo los datos de las tablas dependiendo de la fecha en df_final
for pdf in pdfs:
    csv = re.sub(r'(.*)pdf', r'\1csv', pdf)
    if os.path.isfile(os.path.join('csvs_v2', csv)):
        print(f'    CSV for file {pdf} already exists. Skipping...')
        continue

    m = re.search('(.*)_.*_(.*).pdf', pdf)
    nif = m.group(1)
    year = int(m.group(2))
    empresa = df_nifs['nombre_empresa'].loc[df_nifs['nif'] == nif].to_string(index=False)
    

    texto = parser.from_file('pdfs_v2/' + pdf, xmlContent=True)
    texto = texto['content']

    doc = BeautifulSoup(texto, "html.parser")

    if ((2007 <= year <= 2012) or (2014 <= year <= 2017)):
        print(f'pdf: {pdf}')
        texto = parser.from_file('pdfs_v2/' + pdf)
        texto = texto['content']
        
        if not texto: continue

        contenido = re.search(r'(CONSEJEROS EXTERNOS INDEPENDIENTES.*Número total de consejeros independientes)', texto, re.DOTALL)
        if not contenido: continue

        contenido = contenido.group(1).strip()
        #contenido = contenido.split('\n\n')
        
        nombres = re.findall(r'Nombre o denominación del consejero(.*?)\nPerfil', contenido, re.DOTALL)
        bios = re.findall(r'Perfil(.*?)\nNombre o denominación del consejero', contenido, re.DOTALL)
        bios.append(re.findall(r'(?s:.*)Perfil(.*?)\nNúmero total de consejeros independientes', contenido, re.DOTALL)[-1])

        df = pd.DataFrame({'nombre': nombres, 'bio': bios})

        df['tipo_consejero'] = 'independiente'
        df['empresa'] = empresa
        df['nif'] = nif
        df['fecha'] = year

    elif year == 2013:
        print(f'pdf: {pdf}')
        texto = parser.from_file('pdfs_v2/' + pdf)
        texto = texto['content']
        
        if not texto: continue

        contenido = re.search(r'(CONSEJEROS EXTERNOS INDEPENDIENTES.*Número total de consejeros independientes)', texto, re.DOTALL)
        if not contenido: continue

        contenido = contenido.group(1).strip()
        
        nombres = re.findall(r'Nombre o denominación del consejero(.*?)\nPerfil', contenido, re.DOTALL)
        bios = re.findall(r'Perfil(.*?)\nNombre o denominación del consejero', contenido, re.DOTALL)
        bios.append(re.findall(r'(?s:.*)Perfil(.*?)\nNúmero total de consejeros independientes', contenido, re.DOTALL)[-1])


        try:
            df = pd.DataFrame({'nombre': nombres, 'bio': bios})
        except ValueError:
            print(f'Formato incorrecto, probar camelot')
            continue
        else:
            df['tipo_consejero'] = 'independiente'
            df['empresa'] = empresa
            df['nif'] = nif
            df['fecha'] = year

    elif year <= 2006:
        
        s1 = r'CONSEJEROS EXTERNOS INDEPENDIENTES'
        s2 = r'OTROS CONSEJEROS EXTERNOS'
        
        pags = doc.find_all('div', attrs={"class" : "page"})
        pags = [p.text for p in pags]

        # Encontrar las paginas que contienen la tabla de consejeros
        ini, fin = [], []
        for i in range(0, len(pags)):
            if re.search(s1, pags[i]):
                ini.append(i)
            if re.search(s2, pags[i]):
                fin.append(i)
            else:
                not_found = True
        
        if not ini or not fin: 
            print(f'    Unable to read {pdf}. Skipping...')
            continue
                

        ini, fin = min(ini), min(fin)
        print(f'pdf: {pdf} >>> inicio: {ini}, fin: {fin}')

        if ini != fin:
            pags = str(ini+1) + '-' + str(fin+1)
        else:
            pags = str(ini+1)

        tables = camelot.read_pdf('pdfs_v2/'+pdf, pages=pags)
        df_list = [t.df for t in tables]
        
        ix = set()
        for i, df in enumerate(df_list):
            for col in range(0, len(df.columns)):
                if re.search('\naccionista significativo', df.iloc[0,col]) \
                or re.search('organigrama de la', df.iloc[0,col]) \
                or re.search('Condición actual', df.iloc[0,col]) \
                or re.search('Breve descripción', df.iloc[0,col]):
                    ix.add(i)
                
        for i in sorted(ix, reverse=True):
            del df_list[i]

        cols = {0: 'nombre', 2: 'bio'}
        df_list = [df.rename(columns=cols)[['nombre', 'bio']] for df in df_list if len(df.columns) == 3]

        if df_list: 
            df = pd.concat(df_list, ignore_index=True)
        else:
            continue

        df = df[~df['bio'].str.contains("Perfil")]
        df = df[~df['nombre'].str.contains("social del consejero")]
        df = df[~df['nombre'].str.contains("CONSEJEROS EXTERNOS INDEPENDIENTES")].reset_index()

        for i in range(len(df)):
            if df.loc[i, 'nombre'] == '' and i != 0:
                df.loc[i-1, 'bio'] = df.loc[i-1, 'bio'] + df.loc[i, 'bio']
                df = df.drop(i)

        df['tipo_consejero'] = 'independiente'
        df['empresa'] = empresa
        df['nif'] = nif
        df['fecha'] = year

        df = df.drop(['index'], axis=1)

    elif year >= 2018:
        s1 = r'CONSEJEROS EXTERNOS INDEPENDIENTES'
        s2 = r'Número total de consejeros independientes'
        pags = doc.find_all('div',attrs={"class" : "page"})
        pags = [p.text for p in pags]

        ini, fin = [], []
        for i in range(0, len(pags)):
            if re.search(s1, pags[i]):
                ini.append(i)
            if re.search(s2, pags[i]):
                fin.append(i)

        if not ini or not fin: 
            print(f'    Unable to read {pdf}. Skipping...')
            continue

        ini, fin = min(ini), min(fin)
        print(f'pdf: {pdf} >>> inicio: {ini}, fin: {fin}')

        if ini != fin:
            pags = str(ini+1) + '-' + str(fin+1)
        else:
            pags = str(ini+1)
        tables = camelot.read_pdf('pdfs_v2/'+pdf, pages=pags)

        df_list = [t.df for t in tables]


        cols = {0: 'nombre', 1: 'bio'}
        df_list = [df.rename(columns=cols) for df in df_list if len(df.columns) == 2]


    # Parte común a todos los años
        if df_list: 
            df = pd.concat(df_list, ignore_index=True)
        else:
            continue

        df = df[~df['bio'].str.contains("Perfil")]
        df = df[~df['nombre'].str.contains("social del consejero")]
        df = df[~df['nombre'].str.contains("CONSEJEROS EXTERNOS INDEPENDIENTES")].reset_index()

        for i in range(len(df)):
            if df.loc[i, 'nombre'] == '' and i != 0:
                df.loc[i-1, 'bio'] = df.loc[i-1, 'bio'] + df.loc[i, 'bio']
                df = df.drop(i)

        df['tipo_consejero'] = 'independiente'
        df['empresa'] = empresa
        df['nif'] = nif
        df['fecha'] = year

        df = df.drop(['index'], axis=1)

    df.to_csv(os.path.join('csvs_v2', csv), index=False, header=True)
