# Descripción del Proyecto

Este proyecto se centra en el análisis de datos de accidentes de tráfico en España durante el año 2022, utilizando técnicas de *web scraping* y modelos de machine learning para extraer, procesar y analizar la información registrada por la DGT.

---

## Estructura de Archivos

A continuación, se detalla la organización de los archivos y directorios del proyecto:

### Carpeta `data`

Contiene 4 archivos:

- **carreteras.txt:**  
  Lista con los nombres de todas las carreteras presentes en el dataset.

- **data.py:**  
  Script que realiza *web scraping* para descargar datos de accidentes en formato Excel y los convierte a CSV. En total, genera dos archivos:
  - *TABLA_ACCIDENTES_22.csv* (junto con su versión Excel: `.xlsx` o `.xlsc`)  
    Contiene todos los registros de accidentes ocurridos en 2022 en España, según la DGT.

### Carpeta `model`

Contiene el modelo de machine learning entrenado:
- **modelo_dgt_comprimido.pkl**

### Carpeta `project`

Contiene 2 archivos:

- **project.ipynb:**  
  Notebook que documenta el análisis completo y el proceso de entrenamiento del modelo.

- **streamlit.py:**  
  Script para desplegar el modelo utilizando la librería Streamlit.

### Archivos Raíz

- **Anteproyecto.docx:**  
  Documento que explica la idea y el enfoque general del proyecto.

- **requirements.txt:**  
  Archivo que lista todos los módulos y dependencias necesarias para ejecutar los scripts y la aplicación en general.

---

## Ejecución de los Scripts

- **data.py:**  
  Este script puede ejecutarse desde cualquier directorio. Basta con ubicar el terminal en la carpeta que contenga `data.py` y ejecutar:
  
  python data.py
    Al finalizar, los documentos se guardarán en la misma carpeta.
- **streamlit.py:**
  Para ejecutarlo correctamente, abre la terminal en la carpeta raíz del proyecto y utiliza el siguiente comando:
  
  streamlit run project/streamlit.py
  Esto lanzará la aplicación de Streamlit.