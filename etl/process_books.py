from tika import parser
import re, os
import pandas as pd
  
def line_reader(target_file):    
    with open(target_file, 'r', encoding='utf8') as file:
        store = file.readlines()
        return store

def line_writer(file_name, store):
    with open(file_name, 'w', encoding='utf8') as file:
        file.writelines(store)

def breakdown(target, new_file_name, chunk_length = 10):
    # Numero de ficheros en el directorio
    n_files = len(os.listdir('books/'))
    print(n_files)
    data = line_reader(target)

    part_no = 0
    tmp_list = []
    condition = True
    while condition:
        for i in range(chunk_length):
            if len(data) > 0:
                tmp_list.append(re.sub(r'-\s+', '', data.pop(0)))
            else:
                condition = False
                tmp_list.append('\n')
                break

        part_no += 1
        
        line_writer(str(f'{new_file_name} {str(part_no+n_files)}.txt'), tmp_list)
        tmp_list = []

if __name__ == '__main__':
    parsed = parser.from_file('from_scratch/normal_5cef0106473dc.pdf', xmlContent=False)
    texto = parsed['content']

    with open('from_scratch/normal_5cef0106473dc.pdf.txt','w', encoding='utf8') as out_file: 
        out_file.write(texto)
        
    books = ['from_scratch/Principios_de_Finanzas_Corporativas_9Ed__Myers.pdf.txt',
            'from_scratch/RossWesterfieldJaffe_9ed.pdf.txt',
            'from_scratch/dee.pdf.txt',
            'from_scratch/FundamentosDeEconomiaSecuenciaCorrecta.pdf.txt',
            'from_scratch/images_investigacion_publicaciones_libros_colecciones-especiales_Conceptos-basicos-economia-enfoque-etico.pdf.txt',
            'from_scratch/libro_dinero_y_ahorro.pdf.txt',
            'from_scratch/normal_5cef0106473dc.pdf.txt',
            'from_scratch/finanzas-corporativas-berk.pdf.txt',
        ]
    books_clean = [book[:-8] + '_clean.pdf.txt' for book in books]

    for i in range(7):
        with open(books[i], 'r', encoding='utf8') as f:
            new_text = '\n'.join([line.strip() for line in f.read().split('\n') if (line.strip() and len(line) > 5)])
            with open(books_clean[i],'w', encoding='utf8') as in_file: 
                in_file.write(new_text)
        
        breakdown(books_clean[i], 'books/', 20)
