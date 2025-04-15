import streamlit as st
import pandas as pd
import numpy as np
import json
from joblib import load

# Diccionarios de conversión
mes = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
dia_semana = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes', 6: 'Sábado', 7: 'Domingo'}
zona = {1: 'Carretera', 2: 'Travesía', 3: 'Calle', 4: 'Autopista o autovía urbana'}
interseccion = {1: 'En intersección', 2: 'Fuera de intersección'}
condicion_meteo = {1: 'Despejado', 2: 'Nublado', 3: 'Lluvia débil', 4: 'Lluvia fuerte', 5: 'Granizando', 6: 'Nevando'}
cod_provincia = {
    1: 'Álava', 2: 'Albacete', 3: 'Alicante', 4: 'Almería', 5: 'Ávila', 6: 'Badajoz', 7: 'Islas Baleares', 8: 'Barcelona', 
    9: 'Burgos', 10: 'Cáceres', 11: 'Cádiz', 12: 'Castellón', 13: 'Ciudad Real', 14: 'Córdoba', 15: 'Coruña', 16: 'Cuenca', 
    17: 'Girona', 18: 'Granada', 19: 'Guadalajara', 20: 'Gipuzkoa', 21: 'Huelva', 22: 'Huesca', 23: 'Jaén', 24: 'León', 
    25: 'Lleida', 26: 'Rioja, La', 27: 'Lugo', 28: 'Madrid', 29: 'Málaga', 30: 'Murcia', 31: 'Navarra', 32: 'Ourense', 
    33: 'Asturias', 34: 'Palencia', 35: 'Las Palmas', 36: 'Pontevedra', 37: 'Salamanca', 38: 'Santa Cruz de Tenerife', 
    39: 'Cantabria', 40: 'Segovia', 41: 'Sevilla', 42: 'Soria', 43: 'Tarragona', 44: 'Teruel', 45: 'Toledo', 46: 'Valencia', 
    47: 'Valladolid', 48: 'Bizkaia', 49: 'Zamora', 50: 'Zaragoza', 51: 'Ceuta', 52: 'Melilla'
}
tipo_mecanismo = {1: 'Colisión', 2: 'Atropello', 3: 'Salida de la vía', 4: 'Otros tipos de accidente'}

# Invertir los diccionarios para convertir de cadena a numérico
inv_dic_mes = {v: k for k, v in mes.items()}
inv_dic_dia = {v: k for k, v in dia_semana.items()}
inv_dic_zona = {v: k for k, v in zona.items()}
inv_dic_interseccion = {v: k for k, v in interseccion.items()}
inv_dic_meteo = {v: k for k, v in condicion_meteo.items()}
inv_dic_provincia = {v: k for k, v in cod_provincia.items()}
inv_dic_mecanismo = {v: k for k, v in tipo_mecanismo.items()}

# Extraer los nombres de las carreteras
try:
    with open("data/carreteras.txt", "r", encoding="utf-8") as f:
        opciones_carretera = json.load(f)
except Exception as e:
    st.error(f"Error al leer el archivo de carreteras: {e}")
    opciones_carretera = []

# Reconstruir el mapeo para las carreteras igual que en el entrenamiento
_, uniques = pd.factorize(opciones_carretera)
carretera_mapping = {v: i for i, v in enumerate(uniques)}

# Cargar el modelo
try:
    modelo = load(open('model/modelo_dgt_comprimido.pkl', 'rb'))
except FileNotFoundError:
    st.error("Error: Archivo 'modelo_dgt_comprimido.pkl' no encontrado.")
    st.stop()

# Título de la aplicación
st.title("Predicción de la Gravedad de un Accidente de Tráfico")

# Sección de entrada en la barra lateral
st.sidebar.header("Ingrese los datos del accidente:")

# Widgets para variables categóricas
dia_seleccionado = st.sidebar.selectbox("Día de la semana", list(dia_semana.values()))
zona_seleccionada = st.sidebar.selectbox("Zona", list(zona.values()))
interseccion_seleccionada = st.sidebar.selectbox("Intersección", list(interseccion.values()))
mes_seleccionada = st.sidebar.selectbox("Mes", list(mes.values()))
provincia_seleccionada = st.sidebar.selectbox("Provincia", list(cod_provincia.values()))
meteo_seleccionada = st.sidebar.selectbox("Condiciones meteorológicas", list(condicion_meteo.values()))
mecanismo_seleccionada = st.sidebar.selectbox("Mecanismo del accidente", list(tipo_mecanismo.values()))
carretera_seleccionada = st.sidebar.selectbox("Carretera (busque y filtre)", opciones_carretera)

# Widgets para variables numéricas
total_victimas = st.sidebar.number_input("Número total de víctimas", min_value=1, max_value=100, value=1)
total_vehiculos = st.sidebar.number_input("Número total de vehículos involucrados", min_value=1, max_value=50, value=1)

# Widget para la hora (de 0 a 23)
hora = st.sidebar.number_input("Introducir hora sin minutos (0-23)", min_value=0, max_value=23, value=12)

# Convertir la hora numérica a representaciones cíclicas
hora_sin = np.sin(2 * np.pi * hora / 24)
hora_cos = np.cos(2 * np.pi * hora / 24)

# Variable para almacenar el resultado de la predicción (inicialmente vacía)
resultado_texto = None

# Bloque de predicción: se ejecuta solo al presionar el botón "Predecir"
if st.sidebar.button("Predecir"):
    try:
        # Convertir las variables categóricas en sus valores numéricos
        dia_valor = inv_dic_dia[dia_seleccionado]
        zona_valor = inv_dic_zona[zona_seleccionada]
        mes_valor = inv_dic_mes[mes_seleccionada]
        provincia_valor = inv_dic_provincia[provincia_seleccionada]
        meteo_valor = inv_dic_meteo[meteo_seleccionada]
        mecanismo_valor = inv_dic_mecanismo[mecanismo_seleccionada]
        interseccion_valor = inv_dic_interseccion[interseccion_seleccionada]
        carretera_valor = carretera_mapping[carretera_seleccionada]

        # Construir el diccionario con los datos de entrada
        datos_entrada = {
            'MES': [mes_valor],
            'DIA_SEMANA': [dia_valor],
            'COD_PROVINCIA': [provincia_valor],
            'ZONA': [zona_valor],
            'MECANISMO_ACCIDENTE': [mecanismo_valor],
            'TOTAL_VICTIMAS_30DF': [total_victimas],
            'TOTAL_VEHICULOS': [total_vehiculos],
            'INTERSECCION': [interseccion_valor],
            'CONDICION_METEO': [meteo_valor],
            'HORA_cos': [hora_cos],   
            'HORA_sin': [hora_sin],  
            'CARRETERA': [carretera_valor]
        }
        # Crear el DataFrame solo en este bloque
        df_entrada = pd.DataFrame(datos_entrada)
        
        # Realizar la predicción utilizando el modelo cargado
        prediccion = modelo.predict(df_entrada)
        resultado = prediccion[0] if hasattr(prediccion, "__iter__") else prediccion
        
        # Mapeo para convertir el resultado numérico a etiqueta
        mapeo_original = {'Mortal': 2, 'Leve': 1, 'Sin lesiones': 0}
        resultado_mapping = {valor: clave for clave, valor in mapeo_original.items()}
        resultado_texto = resultado_mapping.get(resultado, "Valor desconocido")
        
        st.subheader("Resultado de la predicción:")
        st.write(f"La gravedad predicha del accidente es: **{resultado_texto}**")
    except Exception as e:
        st.error(f"Ocurrió un error al intentar predecir: {e}")

