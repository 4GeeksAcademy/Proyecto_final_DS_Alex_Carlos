import http
import urllib.request
import re
import os
import zipfile
import xml.etree.ElementTree as ET
import csv

def col_to_index(cell_ref):
    """
    Convierte la parte de letras de una referencia de celda (por ejemplo, "A1" o "BC3")
    a un índice basado en cero (A->0, B->1, ..., Z->25, AA->26, etc).
    """
    col_letters = ''.join(filter(str.isalpha, cell_ref))
    index = 0
    for char in col_letters:
        index = index * 26 + (ord(char.upper()) - ord('A') + 1)
    return index - 1

def descargar_enlace_excel(webpage_url):
    """
    Descarga la página HTML y extrae el enlace del archivo Excel.
    """
    response = urllib.request.urlopen(webpage_url)
    html = response.read().decode('utf-8')

    # Buscar enlace al archivo .xlsx
    match = re.search(r'href=[\'"]([^\'"]+\.xlsx)[\'"]', html, re.IGNORECASE)
    if not match:
        raise ValueError("No se encontró la URL del archivo Excel en la página.")
    
    excel_url = match.group(1)
    # Si el enlace es relativo, agregar el dominio base
    if not excel_url.startswith("http"):
        excel_url = "https://www.dgt.es" + excel_url
    return excel_url

def descargar_archivo(url, destino):
    """
    Descarga el archivo desde la URL y lo guarda en 'destino'.
    """
    urllib.request.urlretrieve(url, destino)


def convertir_xlsx_a_csv(xlsx_path, csv_path):
    """
    Convierte la primera hoja del archivo XLSX a CSV.
    Se procesan las cadenas compartidas y se toman todos los valores de celdas (tipo 's' o numérico).
    """   
    # Definir el namespace como cadena
    NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    
    # Abrir el XLSX como archivo ZIP
    with zipfile.ZipFile(xlsx_path) as z:
        # Leer el archivo de Shared Strings (si existe)
        shared_strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            with z.open("xl/sharedStrings.xml") as f:
                tree = ET.parse(f)
                root = tree.getroot()
                # Buscar todos los elementos <t> concatenando el namespace con 't'
                for t in root.findall('.//' + NS + 't'):
                    shared_strings.append(t.text)
        
        # Seleccionar la primera hoja (sheet1.xml)
        sheet_file = "xl/worksheets/sheet1.xml"
        if sheet_file not in z.namelist():
            raise ValueError("No se encontró la hoja sheet1.xml en el archivo Excel.")
        
        with z.open(sheet_file) as f:
            tree = ET.parse(f)
            root = tree.getroot()

            rows_csv = []
            # Buscar todas las filas usando el namespace
            for row in root.iter(NS + 'row'):
                fila = {}
                for c in row.findall(NS + 'c'):
                    cell_ref = c.attrib.get('r')
                    if not cell_ref:
                        continue
                    col_idx = col_to_index(cell_ref)
                    cell_type = c.attrib.get('t')  # 's' indica shared string
                    valor = ""
                    v_elem = c.find(NS + 'v')
                    if v_elem is not None and v_elem.text is not None:
                        if cell_type == 's':
                            try:
                                idx = int(v_elem.text)
                                valor = shared_strings[idx] if idx < len(shared_strings) else v_elem.text
                            except Exception as e:
                                valor = v_elem.text
                        else:
                            valor = v_elem.text
                    fila[col_idx] = valor
                if fila:
                    # Se asume que en cada fila se han marcado las columnas utilizadas;
                    # se completa hasta el mayor índice encontrado.
                    max_col = max(fila.keys())
                    fila_lista = [fila.get(i, "") for i in range(max_col + 1)]
                    rows_csv.append(fila_lista)
    
    # Guardar los datos extraídos en un archivo CSV
    with open(csv_path, mode='w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for fila in rows_csv:
            writer.writerow(fila)
    print("Archivo CSV generado:", csv_path)

def main():
    # URL de la página a analizar
    webpage_url = (
        "https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/"
        "dgt-en-cifras-detalle/Ficheros-microdatos-de-accidentes-con-victimas-2022/?utm_source=chatgpt.com"
    )
    try:
        excel_url = descargar_enlace_excel(webpage_url)
    except Exception as e:
        print("Error al extraer el enlace:", e)
        return

    excel_filename = "TABLA_ACCIDENTES_22.xlsx"
    csv_filename = "TABLA_ACCIDENTES_22.csv"

    try:
        descargar_archivo(excel_url, excel_filename)
    except Exception as e:
        print("Error al descargar el archivo Excel:", e)
        return

    try:
        convertir_xlsx_a_csv(excel_filename, csv_filename)
    except Exception as e:
        print("Error al convertir XLSX a CSV:", e)
        return

if __name__ == '__main__':
    main()
