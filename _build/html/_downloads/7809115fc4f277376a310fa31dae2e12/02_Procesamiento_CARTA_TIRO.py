#####################################################
# Importación y carga de librerías
#####################################################

import pandas as pd
import numpy as np
import time
import requests
import json
import os
import re
import shutil
from datetime import datetime
from Funciones_Auxiliares_PD import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

#####################################################
# Inicialización de variables
#####################################################

# Ruta al archivo donde se guarda el diccionario
ruta_dicc_plantillas = 'E:/TFM/02. Datos/Trabajo/01. Diccionarios/02_Diccionario_plantillas.json'
ruta_dicc_partidos = 'E:/TFM/02. Datos/Trabajo/01. Diccionarios/01_Diccionario_partidos.json'

# Ruta de la carpeta de creación de carpetas
ruta_equipos = 'E:/TFM/02. Datos/ACB/EQUIPOS'
ruta_estadisticas = 'E:/TFM/02. Datos/ACB/ESTADISTICAS'

#####################################################
# Ejecución
#####################################################

# Cargar el diccionario desde el archivo JSON
with open(ruta_dicc_plantillas, 'r') as archivo:
    diccionario_plantillas = json.load(archivo)
    
# Cargar el diccionario desde el archivo JSON
with open(ruta_dicc_partidos, 'r') as archivo:
    diccionario_partidos = json.load(archivo)    
    
# Inicialización de las carpetas de almacenamineto
l_temporadas = list(diccionario_plantillas.keys())

for temporada in l_temporadas:
    
    # Se inicializa la carpeta de la temporada
    ruta_equipos_temporada = ruta_equipos + '/' + temporada
    
    # Se obtiene el listado de equipos
    l_equipos = list(diccionario_plantillas[temporada].keys())
    
    # Se extraen los datos por cada uno de los equipos que hay en la temporada
    for equipo in l_equipos:
        
        # Se obtiene el listado de partidos jugados por el equipo
        ruta_equipo_temporada = ruta_equipos_temporada + '/' + equipo
        l_partidos = os.listdir(ruta_equipo_temporada)
        l_partidos = [fichero for fichero in l_partidos if '.csv' not in fichero]
        
        # Se inicializa el dataframe de inicio
        df_equipo_volumen = pd.DataFrame()
        
        for partido in l_partidos:
            
            # Se obtiene el listado de ficheros dentro del equipo
            ruta_partido = ruta_equipo_temporada + '/' + partido
            ficheros = os.listdir(ruta_partido)
            
            # Se seleccionan los ficheros de box score
            ficheros = [fichero for fichero in ficheros if 'CARTA_TIRO' in fichero]
            
            # Se selecciona el fichero del equipo y del rival
            fichero_equipo = [fichero for fichero in ficheros if equipo in fichero ][0]
            fichero_rival = [fichero for fichero in ficheros if equipo not in fichero ][0]
            
            # Selección de DFs de los equipos
            df_equipo = pd.read_csv(ruta_partido + '/' + fichero_equipo, sep=';')
            df_rival = pd.read_csv(ruta_partido + '/' + fichero_rival, sep=';')
            
            # Se realiza la transformación de las coordenadas
            df_equipo = df_equipo.apply(modificar_coordenadas, axis=1)

            # Se realiza la asignación del espacio de la pista al que pertece el tiro
            df_equipo['GRUPO'] = df_equipo.apply(lambda row: obtener_grupo(row['x'], row['y']), axis=1)

            # Se convierte la variable href
            df_equipo = df_equipo.apply(modificar_href, axis=1)

            # Se realiza la selección de campos y la conversión de nombres
            df_equipo_lite = df_equipo[['D','NOMBRE','href','GRUPO']]
            df_equipo_lite.columns = ['D', 'NOMBRE', 'ACIERTO', 'GRUPO']

            # Se realiza el agrupación de los tiros realizados pore l jugador por zonas
            df_equipo_group = pd.DataFrame(df_equipo_lite.value_counts()).reset_index()
            df_equipo_group.columns = ['D', 'NOMBRE', 'ACIERTO', 'GRUPO', 'VOLUMEN']
            
            df_equipo_volumen = pd.concat([df_equipo_volumen,df_equipo_group])
        
        # Se realiza la creación de la carpeta de estadísticas
        ruta_estadistica_final = ruta_estadisticas + '/' + temporada + '/' + equipo
        
        # Se obtiene la volumetría final y se extrae el formato final de la tabla                    
        df_equipo_volumen = df_equipo_volumen.groupby(['D', 'NOMBRE', 'ACIERTO', 'GRUPO']).sum().reset_index()
        df_volumen_transformado = pd.pivot_table(df_equipo_volumen, values='VOLUMEN', index=['D', 'NOMBRE'], columns=['GRUPO', 'ACIERTO'], aggfunc='sum')
        df_volumen_transformado.columns = ['_'.join(map(str, col)).strip() for col in df_volumen_transformado.columns.values]
        df_volumen_transformado = df_volumen_transformado.reset_index()
        df_volumen_transformado = df_volumen_transformado.fillna(0)
        
        # Se realiza el guardado de la tabla
        df_volumen_transformado.to_csv(ruta_estadistica_final + '/02_ESTADISTICAS_CARTA_TIRO_EQUIPO.csv', sep=';',index=False)     